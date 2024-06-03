import json
import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.filedialog import askopenfile

import pandas
import requests
from dotenv import load_dotenv
from twilio.rest import Client

import pymail.main as cli


class message_sending:
    sms_sid = []
    sent_email_addresses = []
    sent_phone_numbers = []

    def __init__(self, email_from: str, number_from: str) -> None:
        self.email_from = email_from
        self.number_from = number_from

    def send_email(self, emails_to: list[str], label_name: str) -> None:
        PLAYIT_URL = os.getenv("PLAYIT_URL")
        EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")
        EMAIL_BODY = os.getenv("EMAIL_BODY")
        EMAIL_HTML = f"""
        <html>
            <body>
                <img src="{PLAYIT_URL}/image.png">
            </body>
        </html>
            """

        for email_to in emails_to:
            try:
                message = cli.send_message(
                    self.email_from,
                    email_to,
                    EMAIL_SUBJECT,
                    EMAIL_BODY,
                    EMAIL_HTML,
                )

                cli.add_label(message["id"], label_name)
                self.sent_email_addresses.append(message)
                print("Email sent to:", email_to)

            except Exception as e:
                self.sent_email_addresses[email_to] = "Not Sent"
                print(f"Error: {e}")
            else:
                delivery_sent_messages.email_sent_count += 1

    def send_sms(self, numbers_to: list[str]) -> None:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        sms_body = os.getenv("SMS_BODY")
        for number_to in numbers_to:
            try:
                print("Sending SMS")
                message = client.messages.create(
                    body=sms_body,
                    from_=self.number_from,
                    to=number_to,
                )
                self.sms_sid.append(message.sid)
            except Exception as e:
                print(f"Error: {e}")
            else:
                delivery_sent_messages.sms_sent_count += 1

    def send_whatsapp_message(self, numbers_to: list[str]) -> None:
        INTERAKT_API = os.getenv("INTERAKT_API")
        TEMPLATE_NAME = os.getenv("TEMPLATE_NAME")
        TEMPLATE_BODY_VALUES = os.getenv("TEMPLATE_BODY_VALUES")
        url = "https://api.interakt.ai/v1/public/message/"
        headers = {
            "Authorization": "Basic {{" + INTERAKT_API + "}}",
            "Content-Type": "application/json",
        }
        for number_to in numbers_to:
            try:
                payload = json.dumps(
                    {
                        "countryCode": "+91",
                        "phoneNumber": f"{number_to}",
                        "callbackData": "some text here",
                        "type": "Template",
                        "template": {
                            "name": f"{TEMPLATE_NAME}",
                            "languageCode": "en",
                            "bodyValues": f"{TEMPLATE_BODY_VALUES}",
                        },
                    }
                )
                print(payload)

                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
            except Exception as e:
                print(f"Error: {e}")
            else:
                delivery_sent_messages.whatsapp_sent_count += 1

    def send_all(self, csvFile):
        label_name = "PyMessage"
        cli.create_label(label_name)
        numbers_to = csvFile["Phone"].tolist()
        emails_to = csvFile["Email"].tolist()

        # Send Email
        self.send_email(emails_to, label_name)

        # Send SMS
        self.send_sms(numbers_to)

        # Send Whatsapp Msg
        self.send_whatsapp_message(numbers_to)


class delivery_sent_messages:
    email_sent_count = 0
    sms_sent_count = 0
    whatsapp_sent_count = 0

    email_seen_count = 0
    sms_delivered_count = 0

    delivered_phone_numbers = []

    def emails_seen(self, log_file: str) -> int:
        with open(log_file, "r") as file:
            lines = file.readlines()

            lines_with_200 = [
                line.strip() for line in lines if line.endswith("200 -\n")
            ]

            for line in lines_with_200:
                self.email_seen_count += 1
        return self.email_seen_count

    def sms_delivered(self, message_sending) -> int:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        sms_sid_dic = message_sending.sms_sid
        for sms_sid in sms_sid_dic:
            message = client.messages(sms_sid).fetch()
            if message.status == "delivered":
                self.sms_delivered_count += 1
                self.delivered_phone_numbers.append(message.to)

        return self.sms_delivered_count

    def export_sms_to_csv(self, csvFile) -> None:
        df = pandas.DataFrame(csvFile)
        self.phone_numbers.append("+91 87654 32109")
        for phone_number in self.phone_numbers:
            filtered_df = df[df["Phone"] == phone_number][["Name", "Course Name"]]
            filtered_df.to_csv(
                "filtered_data.csv",
                index=False,
                mode="a",
                header=not os.path.exists("filtered_data.csv"),
            )


class gui:
    def __init__(self, root) -> None:
        self.root = root
        self.content = tk.Frame(root)

        self.root.title("PyMessage")
        self.content.place(relx=0.5, rely=0.5, anchor="center")

    def input_excel(self):
        file = askopenfile(
            initialdir=".",
            title="Select a File",
            filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")),
        )

        try:
            self.csvFile = pandas.read_csv(file)
            tk.messagebox.showinfo("Info", "CSV Initialised!")
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Invalid file or no file provided. Please input a CSV file."
            )

    def create_widgets(self, email_from, number_from) -> None:
        sender1 = message_sending(email_from, number_from)
        text_label = tk.Label(
            self.content,
            font=tkFont.Font(size=24),
            text="Welcome to PyMessage!",
        )
        input_button = tk.Button(
            self.content,
            text="Input",
            command=lambda: self.input_excel(),
        )
        report_button = tk.Button(
            self.content,
            text="Run Report",
            command=lambda: sender1.send_all(self.csvFile),
        )
        dashboard_button = tk.Button(
            self.content,
            text="Open Dashboard",
            command=lambda: self.dashboard(email_from, number_from),
        )
        history_button = tk.Button(
            self.content,
            text="Get History",
            command=lambda: self.history(),
        )
        text_label.grid(row=1, column=1, pady=30)
        input_button.grid(row=2, column=1, pady=5)
        report_button.grid(row=3, column=1, pady=5)
        dashboard_button.grid(row=4, column=1, pady=5)
        history_button.grid(row=5, column=1, pady=5)

    def dashboard(self, email_from, number_from):
        # Configuring Dashboard
        dashboard_tk = tk.Toplevel()
        dashboard_tk.rowconfigure(1, weight=1)
        dashboard_tk.rowconfigure(2, weight=1)
        dashboard_tk.columnconfigure(0, weight=1)
        dashboard_tk.columnconfigure(1, weight=1)
        dashboard_tk.columnconfigure(2, weight=1)
        dashboard_tk.columnconfigure(3, weight=1)
        dashboard_tk.columnconfigure(4, weight=1)

        message_sending_obj = message_sending(email_from, number_from)
        email_sent = delivery_sent_messages.email_sent_count
        sms_sent = delivery_sent_messages.sms_sent_count
        whatsapp_sent = delivery_sent_messages.whatsapp_sent_count

        log_file = "email_seen.log"
        sent_message_class = delivery_sent_messages()
        email_seen = sent_message_class.emails_seen(log_file)
        sms_delivered = sent_message_class.sms_delivered(message_sending_obj)

        sent_message_class.export_sms_to_csv(self.csvFile)

        email_label = tk.Label(dashboard_tk, text="Emails Sent & Opened By User")
        sms_label = tk.Label(dashboard_tk, text="SMS Sent & Received")
        whatsapp_label = tk.Label(dashboard_tk, text="WhatsApp messages Sent & Read")

        email_sent_label = tk.Label(
            dashboard_tk,
            text=f"Emails Sent: {email_sent}\nEmails Seen: {email_seen}",
        )
        sms_sent_label = tk.Label(
            dashboard_tk,
            text=f"SMS Sent: {sms_sent}\nSMS Delivered: {sms_delivered}",
        )
        whatsapp_sent_label = tk.Label(
            dashboard_tk, text=f"WhatsApp Messages Sent: {whatsapp_sent}"
        )

        # Separator object
        separator1 = ttk.Separator(dashboard_tk, orient="vertical")
        separator2 = ttk.Separator(dashboard_tk, orient="vertical")
        separator1.grid(row=1, column=1, padx=0, pady=0, ipady=10000)
        separator2.grid(row=1, column=3, padx=0, pady=0, ipady=10000)

        email_label.grid(row=0, column=0)
        sms_label.grid(row=0, column=2)
        whatsapp_label.grid(row=0, column=4)

        email_sent_label.grid(row=1, column=0)
        sms_sent_label.grid(row=1, column=2)
        whatsapp_sent_label.grid(row=1, column=4)

    def set_threads_text(self, text_view, to_email) -> None:
        result = cli.get_threads("PyMessage", to_email)
        if not result:
            raise Exception("No valid threads returned.")
        formatted_str = ""
        for email in result:
            formatted_str += f"{email["subject"]}\n\n{email["body"]}\n\n{"-"*50}\n\n"

        text_view.delete("1.0", tk.END)
        text_view.insert("1.0", formatted_str)

    def history(self):
        history_tk = tk.Toplevel()
        history_tk.rowconfigure(0, weight=1)
        history_tk.rowconfigure(1, weight=1)
        history_tk.rowconfigure(2, weight=5)
        history_tk.rowconfigure(3, weight=1)
        history_tk.rowconfigure(4, weight=1)
        history_tk.columnconfigure(0, weight=1)
        history_tk.columnconfigure(1, weight=1)
        history_tk.columnconfigure(2, weight=1)

        username = tk.StringVar()

        text_label = tk.Label(history_tk, font=tkFont.Font(size=24), text="History")
        text_view = tk.Text(history_tk)
        user_label = tk.Label(history_tk, text="Select a User: ")
        user_combobox = ttk.Combobox(history_tk, width=27, textvariable=username)
        # user_combobox['values'] =
        to_email = self.get_email(username)
        email_button = tk.Button(
            history_tk,
            text="Get Threads",
            command=lambda: self.set_threads_text(text_view, to_email),
        )
        whatsapp_button = tk.Button(history_tk, text="Get WhatsApp Messages")

        text_label.grid(row=0, column=1, pady=30)
        user_label.grid(row=1, column=0)
        user_combobox.grid(row=2, column=0)
        email_button.grid(row=3, column=0)
        whatsapp_button.grid(row=3, column=2, padx=5)
        text_view.grid(row=4, column=1)


def main():
    load_dotenv()
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    FROM_NUMBER = os.getenv("FROM_NUMBER")

    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    PLAYIT_URL = os.getenv("PLAYIT_URL")
    EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")
    EMAIL_BODY = os.getenv("EMAIL_BODY")
    SMS_BODY = os.getenv("SMS_BODY")
    INTERAKT_API = os.getenv("INTERAKT_API")
    if not all(
        [
            FROM_EMAIL,
            FROM_NUMBER,
            TWILIO_SID,
            TWILIO_TOKEN,
            PLAYIT_URL,
            EMAIL_SUBJECT,
            EMAIL_BODY,
            SMS_BODY,
            INTERAKT_API,
        ]
    ):
        raise ValueError("One or more required environment variables are missing.")

    root = tk.Tk()
    main_window = gui(root)
    main_window.create_widgets(FROM_EMAIL, FROM_NUMBER)
    root.mainloop()


if __name__ == "__main__":
    main()
