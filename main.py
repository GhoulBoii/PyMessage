import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter.filedialog import askopenfile
from tkinter import ttk

# FIX HTML, DASHBOARD, SMS
import pandas
from dotenv import load_dotenv
from twilio.rest import Client

import pymail.main as cli

load_dotenv()

# whatsapp_sent_label = tk.Label(
#     dashboard_tk, text=f"Whatsapp Sent: {whatsapp_sent}"
# )
# sms_delivered_and_sent()
# whatsapp_delivered_and_sent()

# emails_text = tk.Text(dashboard_tk, height=5, width=52)
# sms_text = tk.Text(dashboard_tk, height=5, width=52, justify=tk.CENTER)
# whatsapp_text = tk.Text(dashboard_tk, height=5, width=52)
# emails_text.insert(tk.END, f"{email_count[0]}\t{email_count[1]}")
# sms_text.insert(tk.END, f"{sms_count[0]}\t{sms_count[1]}")
# whatsapp_text.insert(tk.END, f"{whatsapp_count[0]}\t{whatsapp_count[1]}")


# def send_whatsapp_message(to_phone: str) -> None:
#     global FROM_NUMBER
#     print("Send whatsapp msg")
#     whatsapp_message = client.messages.create(
#         body="Hello there!",
#         from_=f"whatsapp:{FROM_NUMBER}",
#         to=f"whatsapp:{to_phone}",
#     )
# def sms_delivered_and_sent(self) -> int:
#     global sms_delivered_count
#     global sms_sent_count
#     delivery_receipts = (
#         client.conversations.v1.conversations("CHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
#         .messages("IMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
#         .delivery_receipts.list(limit=20)
#     )
#
#     for record in delivery_receipts:
#         if record.status == "delivered":
#             sms_delivered_count += sms_delivered_count + 1
#         elif record.status == "sent":
#             sms_sent_count += sms_sent_count + 1
#
# def whatsapp_delivered_and_sent():
#     global sms_delivered_count
#     global sms_sent_count
#     delivery_receipts = (
#         client.conversations.v1.conversations("CHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
#         .messages("IMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
#         .delivery_receipts.list(limit=20)
#     )
#
#     for record in delivery_receipts:
#         if record.status == "delivered":
#             sms_delivered_count += sms_delivered_count + 1
#         elif record.status == "read":
#             sms_sent_count += sms_sent_count + 1


class message_sending:
    sms_sid = []

    def __init__(self, email_from: str, number_from: str) -> None:
        self.email_from = email_from
        self.number_from = number_from

    def send_email(self, email_to: str) -> None:
        print("Sending email")
        PLAYIT_URL = os.getenv("PLAYIT_URL")
        email_subject = "Test Email"
        email_body = "Hello From Python!"
        EMAIL_HTML = f"""
        <html>
            <body>
                <img src="{PLAYIT_URL}/image.png">
            </body>
        </html>
            """

        cli.gmail_send_message(
            self.email_from,
            email_to,
            email_subject,
            email_body,
            EMAIL_HTML,
        )

    def send_sms(self, number_to: str) -> None:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        sms_body = "Hello From Python"

        print("Sending sms")
        message = client.messages.create(
            body=sms_body,
            from_=self.number_from,  # Your Twilio phone number
            to=number_to,  # Recipient's phone number
        )
        self.sms_sid.append(message.sid)

    def send_all(self, csvFile):
        # FIX: store to number and email to in dictionary and then send
        for index, row in csvFile.iterrows():
            number_to = row["Phone"]
            email_to = row["Email"]

            # Send Email
            try:
                self.send_email(email_to)
            except Exception as e:
                print(f"Error: {e}")
            else:
                delivery_sent_messages.email_sent_count += 1

            # Send SMS
            try:
                self.send_sms(number_to)
            except Exception as e:
                print(f"Error: {e}")
            else:
                delivery_sent_messages.sms_sent_count += 1

            # Send Whatsapp Msg
            # send_whatsapp_message(self.to_phone)


class delivery_sent_messages:
    email_sent_count = 0
    sms_sent_count = 0
    email_seen_count = 0
    sms_delivered_count = 0

    def emails_delivered_and_sent(self, log_file: str) -> int:
        with open(log_file, "r") as file:
            lines = file.readlines()

            # Filter lines containing '200'
            lines_with_200 = [
                line.strip() for line in lines if line.endswith("200 -\n")
            ]

            # Print filtered lines
            for line in lines_with_200:
                self.email_seen_count += 1
        return self.email_seen_count

    def sms_delivered_and_sent(self, message_sending) -> int:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        sms_sid_dic = message_sending.sms_sid
        for sms_sid in sms_sid_dic:
            message = client.messages(sms_sid).fetch()
            if message.status == "delivered":
                self.sms_delivered_count += 1

        return self.sms_delivered_count


class gui:
    def __init__(self, root, bg_colour) -> None:
        self.root = root
        self.content = tk.Frame(root)
        self.bg_colour = bg_colour
        self.switch_value = False
        self.theme_switcher_text = "🌞"

        self.root.title("PyMessage")
        self.root.config(bg=bg_colour)
        self.content.place(relx=0.5, rely=0.5, anchor="center")
        self.content.config(bg=bg_colour)

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
            bg=self.bg_colour,
            font=tkFont.Font(size=24),
            text="Welcome to PyMessage!",
        )
        input_button = tk.Button(
            self.content,
            bg=self.bg_colour,
            text="Input",
            command=lambda: self.input_excel(),
        )
        report_button = tk.Button(
            self.content,
            bg=self.bg_colour,
            text="Run Report",
            command=lambda: sender1.send_all(self.csvFile),
        )
        dashboard_button = tk.Button(
            self.content,
            bg=self.bg_colour,
            text="Open Dashboard",
            command=lambda: self.dashboard(email_from, number_from),
        )
        theme_changer_button = tk.Button(
            self.root,
            bg=self.bg_colour,
            text=self.theme_switcher_text,
            command=lambda: self.light_and_dark_toggle(
                text_label,
                input_button,
                report_button,
                dashboard_button,
                theme_changer_button,
            ),
        )

        text_label.grid(row=1, column=1, pady=30)
        input_button.grid(row=2, column=1, pady=5)
        report_button.grid(row=3, column=1, pady=5)
        dashboard_button.grid(row=4, column=1, pady=5)
        theme_changer_button.place(relx=0.9, rely=0.9, anchor="nw")

    # Defining a function to toggle
    # between light and dark theme
    def light_and_dark_toggle(
        self,
        text_label,
        input_button,
        report_button,
        dashboard_button,
        theme_changer_button,
    ):
        if self.switch_value:
            bg_colour = "black"
            fg_colour = "white"
            self.theme_switcher_text = "🌞"
            self.switch_value = False
        else:
            bg_colour = "white"
            fg_colour = "black"
            self.theme_switcher_text = "🌚"
            self.switch_value = True

        self.root.config(bg=bg_colour)
        self.content.config(bg=bg_colour)
        text_label.config(fg=fg_colour, bg=bg_colour)
        input_button.config(fg=fg_colour, bg=bg_colour)
        report_button.config(fg=fg_colour, bg=bg_colour)
        dashboard_button.config(fg=fg_colour, bg=bg_colour)
        theme_changer_button.config(
            fg=fg_colour, bg=bg_colour, text=self.theme_switcher_text
        )

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

        log_file = "email_seen.log"
        sent_message_class = delivery_sent_messages()
        email_seen = sent_message_class.emails_delivered_and_sent(log_file)
        sms_delivered = sent_message_class.sms_delivered_and_sent(message_sending_obj)

        email_label = tk.Label(dashboard_tk, text="Emails Sent & Opened By User")
        sms_label = tk.Label(dashboard_tk, text="SMS Sent & Received")
        whatsapp_label = tk.Label(dashboard_tk, text="WhatsApp messages Sent & Read")

        email_sent_label = tk.Label(
            dashboard_tk, text=f"Emails Sent: {email_sent}\nEmails Seen: {email_seen}"
        )
        sms_sent_label = tk.Label(
            dashboard_tk, text=f"SMS Sent: {sms_sent}\nSMS Delivered: {sms_delivered}"
        )
        whatsapp_sent_label = tk.Label(dashboard_tk, text="WIP")

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


def main():
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    FROM_NUMBER = os.getenv("FROM_NUMBER")
    if not all([FROM_EMAIL, FROM_NUMBER]):
        # Raise an exception if any variable is None
        raise ValueError("One or more required environment variables are missing.")

    bg_colour = "black"
    root = tk.Tk()
    main_window = gui(root, bg_colour)
    main_window.create_widgets(FROM_EMAIL, FROM_NUMBER)
    root.mainloop()


if __name__ == "__main__":
    main()
