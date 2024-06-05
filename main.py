import json
import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.filedialog import askopenfile
from tkinter import messagebox

import pandas as pd
import requests
from dotenv import load_dotenv
from twilio.rest import Client

import pymailcli.main as cli


class MessageSending:
    def __init__(self, email_from: str, number_from: str) -> None:
        self.email_from = email_from
        self.number_from = number_from
        self.sms_sid = []

        self.sent_email_addresses = {}
        self.sent_sms = {}
        self.sent_whatsapp_numbers = {}

        self.email_sent_count = 0
        self.sms_sent_count = 0
        self.whatsapp_sent_count = 0

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

    def send_sms(self, numbers_to: list[str]) -> None:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        sms_body = os.getenv("SMS_BODY")

        for number_to in numbers_to:
            try:
                number_to_str = str(number_to)
                if not number_to_str.startswith("+") and len(number_to_str) == 12:
                    number_to_str = "+" + number_to_str
                elif len(number_to_str) == 10:
                    number_to_str = "+91" + number_to_str
                else:
                    raise ValueError("Invalid number")

                print("Sending SMS")
                message = client.messages.create(
                    body=sms_body,
                    from_=self.number_from,
                    to=number_to_str,
                )
                self.sms_sid.append(message.sid)
            except Exception as e:
                self.sent_sms[number_to] = "Not Sent"
                print(f"Error: {e}")
            else:
                self.sent_sms[number_to] = "Sent"
                self.sms_sent_count += 1

    def send_whatsapp_message(self, numbers_to: list[str]) -> None:
        INTERAKT_API = os.getenv("INTERAKT_API")
        TEMPLATE_NAME = os.getenv("TEMPLATE_NAME")
        TEMPLATE_BODY_VALUES = json.loads(os.getenv("TEMPLATE_BODY_VALUES"))
        url = "https://api.interakt.ai/v1/public/message/"
        headers = {
            "Authorization": "Basic {{" + INTERAKT_API + "}}",
            "Content-Type": "application/json",
        }

        for number_to in numbers_to:
            try:
                number_to_str = str(number_to)
                if not number_to_str.startswith("+") and len(number_to_str) == 12:
                    number_to_str = "+" + number_to_str
                elif len(number_to_str) == 10:
                    number_to_str = "+91" + number_to_str
                else:
                    raise ValueError("Invalid number")

                payload = json.dumps(
                    {
                        "fullPhoneNumber": number_to_str,
                        "callbackData": "some text here",
                        "type": "Template",
                        "template": {
                            "name": TEMPLATE_NAME,
                            "languageCode": "en",
                            "bodyValues": TEMPLATE_BODY_VALUES,
                        },
                    }
                )
                response = requests.post(url, headers=headers, data=payload)
                print(response.text)
            except Exception as e:
                self.sent_whatsapp_numbers[number_to] = "Not Sent"
                print(f"Error: {e}")
            else:
                self.sent_whatsapp_numbers[number_to] = "Sent"
                self.whatsapp_sent_count += 1

    def create_database(self, csvFile: pd.DataFrame) -> None:
        csvFile["Email Sent"] = csvFile["Email"].map(self.sent_email_addresses)
        csvFile["SMS Sent"] = csvFile["Phone"].map(self.sent_sms)
        csvFile["WhatsApp Sent"] = csvFile["Phone"].map(self.sent_whatsapp_numbers)
        csvFile.to_csv("output.csv", index=False)

    def send_all(self, csvFile: pd.DataFrame) -> None:
        label_name = "PyMessage"
        cli.create_label(label_name)
        numbers_to = csvFile["Phone"].tolist()
        emails_to = csvFile["Email"].tolist()

        self.send_email(emails_to, label_name)
        self.send_sms(numbers_to)
        self.send_whatsapp_message(numbers_to)
        self.create_database(csvFile)


class MessageStatus:
    @staticmethod
    def seen_emails(log_file: str) -> int:
        email_seen_count = 0
        try:
            with open(log_file, "r") as file:
                lines = file.readlines()

                lines_with_200 = [
                    line.strip() for line in lines if line.endswith("200 -\n")
                ]

                for line in lines_with_200:
                    email_seen_count += 1
        except FileNotFoundError:
            print(f"{log_file} does not exist. Run server.py or create {log_file}.")
        return email_seen_count

    @staticmethod
    def delivered_sms(message_sending: MessageSending) -> int:
        sms_delivered_count = 0
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        for sms_sid in message_sending.sms_sid:
            message = client.messages(sms_sid).fetch()
            if message.status == "delivered":
                sms_delivered_count += 1
        return sms_delivered_count


class Gui:
    def __init__(self, root) -> None:
        self.root = root
        self.content = tk.Frame(root)

        self.root.title("PyMessage")
        self.root.geometry("500x600")
        self.content.place(relx=0.5, rely=0.5, anchor="center")

    def input_excel(self) -> None:
        file = askopenfile(
            initialdir=".",
            title="Select a File",
            filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")),
        )

        try:
            self.csvFile = pd.read_csv(file)
            messagebox.showinfo("Info", "CSV Initialized!")
        except (ValueError, FileNotFoundError):
            messagebox.showerror(
                "Error", "Invalid file or no file provided. Please input a CSV file."
            )

    def create_widgets(self, email_from: str, number_from: str) -> None:
        message_sending = MessageSending(email_from, number_from)
        text_label = tk.Label(
            self.content,
            font=tkFont.Font(size=24),
            text="Welcome to PyMessage!",
        )
        instructions_text = tk.Label(
            self.content,
            text="Input a CSV file and then Run Report. All statistics will be displayed in the Dashboard and thread messages can be browsed through History. Enjoy :)",
            font=tkFont.Font(size=10),
            wraplength=300,
        )
        input_button = tk.Button(
            self.content,
            text="Input",
            command=self.input_excel,
        )
        report_button = tk.Button(
            self.content,
            text="Run Report",
            command=lambda: message_sending.send_all(self.csvFile),
        )
        dashboard_button = tk.Button(
            self.content,
            text="Open Dashboard",
            command=lambda: self.dashboard(email_from, number_from, message_sending),
        )
        history_button = tk.Button(
            self.content,
            text="Get History",
            command=self.history,
        )

        text_label.grid(row=1, column=1)
        instructions_text.grid(row=2, column=1, pady=(0, 10))
        input_button.grid(row=3, column=1, pady=5)
        report_button.grid(row=4, column=1, pady=5)
        dashboard_button.grid(row=5, column=1, pady=5)
        history_button.grid(row=6, column=1)

    def dashboard(
        self, email_from: str, number_from: str, message_sending: MessageSending
    ) -> None:
        dashboard_tk = tk.Toplevel()
        dashboard_tk.geometry("500x600")
        dashboard_tk.rowconfigure(1, weight=1)
        dashboard_tk.rowconfigure(2, weight=1)
        dashboard_tk.columnconfigure(0, weight=1)
        dashboard_tk.columnconfigure(1, weight=1)
        dashboard_tk.columnconfigure(2, weight=1)
        dashboard_tk.columnconfigure(3, weight=1)
        dashboard_tk.columnconfigure(4, weight=1)

        message_status = MessageStatus()
        email_sent = message_sending.email_sent_count
        sms_sent = message_sending.sms_sent_count
        whatsapp_sent = message_sending.whatsapp_sent_count

        LOG_FILE = "email_seen.log"
        email_seen = message_status.seen_emails(LOG_FILE)
        sms_delivered = message_status.delivered_sms(message_sending)

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

    def get_email(self, chosen_name: str, output_csv: pd.DataFrame) -> str:
        email = output_csv.loc[output_csv["Name"] == chosen_name, "Email"].iloc[0]
        return email

    def set_threads_text(
        self, text_view: tk.Text, chosen_name: str, output_csv: pd.DataFrame
    ) -> None:
        to_email = self.get_email(chosen_name, output_csv)
        result = cli.get_threads("PyMessage", to_email)
        if not result:
            print("No valid threads returned. Threads must have >1 emails in them.")
            text_view.insert("1.0", "No threads found with >1 emails.")
        else:
            formatted_str = ""
            for email in result:
                formatted_str += (
                    f"{email['subject']}\n\n{email['body']}\n\n{'-'*50}\n\n"
                )

            text_view.delete("1.0", tk.END)
            text_view.insert("1.0", formatted_str)

    def history(self) -> None:
        history_tk = tk.Toplevel()
        history_tk.geometry("500x600")
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
        output_csv = pd.read_csv("output.csv")
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


def main() -> None:
    load_dotenv()
    required_env_vars = [
        "FROM_EMAIL",
        "FROM_NUMBER",
        "TWILIO_SID",
        "TWILIO_TOKEN",
        "PLAYIT_URL",
        "EMAIL_SUBJECT",
        "EMAIL_BODY",
        "SMS_BODY",
        "INTERAKT_API",
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"One or more required environment variables are missing: {', '.join(missing_vars)}"
        )

    root = tk.Tk()
    main_window = Gui(root)
    main_window.create_widgets(os.getenv("FROM_EMAIL"), os.getenv("FROM_NUMBER"))
    root.mainloop()


if __name__ == "__main__":
    main()
