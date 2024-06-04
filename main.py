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

    sent_email_addresses = {}

    sent_sms = {}
    seen_sms = []

    sent_whatsapp_numbers = {}
    seen_whatsapp_numbers = {}

    email_sent_count = 0
    sms_sent_count = 0
    whatsapp_sent_count = 0

    email_seen_count = 0
    sms_delivered_count = 0

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
                cli.check_email_bounced_status(message["id"])
                self.sent_email_addresses[email_to] = "Sent"
                print("Email sent to:", email_to)

            except Exception as e:
                self.sent_email_addresses[email_to] = "Not Sent"
                print(f"Error: {e}")
            else:
                self.email_sent_count += 1

    def seen_emails(self, log_file: str) -> int:
        LOG_FILE = "email_seen.log"
        with open(LOG_FILE, "r") as file:
            lines = file.readlines()

            lines_with_200 = [
                line.strip() for line in lines if line.endswith("200 -\n")
            ]

            for line in lines_with_200:
                self.email_seen_count += 1
        return self.email_seen_count

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
                self.sent_sms[number_to] = "Sent"
            except Exception as e:
                self.sent_sms[number_to] = "Not Sent"
                print(f"Error: {e}")
            else:
                self.sms_sent_count += 1

    def delivered_sms(self) -> int:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        sms_sid_dic = self.sms_sid
        for sms_sid in sms_sid_dic:
            message = client.messages(sms_sid).fetch()
            if message.status == "delivered":
                self.sms_delivered_count += 1
                self.seen_sms.append(message.to)

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
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
                self.sent_whatsapp_numbers[number_to] = "Sent"
            except Exception as e:
                self.sent_whatsapp_numbers[number_to] = "Not Sent"
                print(f"Error: {e}")
            else:
                self.whatsapp_sent_count += 1

    def create_database(self, csvFile) -> None:
        csvFile["Email Sent"] = csvFile["Email"].map(self.sent_email_addresses)
        csvFile["SMS Sent"] = csvFile["Phone"].map(self.sent_sms)
        csvFile["SMS Delivered"] = csvFile["Phone"].map(self.delivered_sms)
        csvFile["WhatsApp Sent"] = csvFile["Phone"].map(self.sent_whatsapp_numbers)
        csvFile["WhatsApp Seen"] = csvFile["Phone"].map(self.seen_whatsapp_numbers)
        csvFile.to_csv("output.csv", index=False)

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
        # self.send_whatsapp_message(numbers_to)

        self.create_database(csvFile)


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

    def get_email(self, chosen_name, output_csv) -> str:
        email = output_csv.loc[output_csv["Name"] == chosen_name, "Email"].iloc[0]
        return email

    def set_threads_text(self, text_view, chosen_name, output_csv) -> None:
        to_email = self.get_email(chosen_name, output_csv)
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

        chosen_name = tk.StringVar()

        text_label = tk.Label(history_tk, font=tkFont.Font(size=24), text="History")
        text_view = tk.Text(history_tk)
        user_label = tk.Label(history_tk, text="Select a User: ")
        user_combobox = ttk.Combobox(history_tk, width=27, textvariable=chosen_name)
        output_csv = pandas.read_csv("output.csv")
        user_combobox["values"] = output_csv["Name"].tolist()
        email_button = tk.Button(
            history_tk,
            text="Get Threads",
            command=lambda: self.set_threads_text(
                text_view, chosen_name.get(), output_csv
            ),
        )

        text_label.grid(row=0, column=1, pady=30)
        user_label.grid(row=1, column=1)
        user_combobox.grid(row=2, column=1)
        email_button.grid(row=3, column=1)
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
