import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter.filedialog import askopenfile

import pandas
from dotenv import load_dotenv
from twilio.rest import Client

import pymail_cli as cli

load_dotenv()

PLAYIT_URL = os.getenv("PLAYIT_URL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_NO = os.getenv("FROM_NO")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
client = Client(TWILIO_SID, TWILIO_TOKEN)

switch_value = False
bg_colour = "black"
fg = "white"
theme_switcher_text = "🌞"

# First element in list is for delivered count and second is for received count
email_count = [0, 0]
sms_count = [0, 0]
whatsapp_count = [0, 0]


def input_excel():
    file = askopenfile(
        initialdir=".",
        title="Select a File",
        filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")),
    )

    # Change label contents
    global csvFile
    try:
        csvFile = pandas.read_csv(file)
        tk.messagebox.showinfo("Info", "CSV Initialised!")
    except ValueError:
        tk.messagebox.showerror(
            "Error", "Invalid file or no file provided. Please input a CSV file."
        )


def send_email(to_email: str) -> None:
    global FROM_EMAIL
    html_code = f"""
<html>
    <body>
        <img src="{PLAYIT_URL}/image.png">
    </body>
</html>
    """
    print("Sending email")
    cli.gmail_send_message(
        FROM_EMAIL,
        to_email,
        "Test Email",
        "I am sending this as a test email",
        html_code,
    )


def send_sms(to_phone: str) -> None:
    global FROM_NO
    print("Sending sms")
    sms_message = client.messages.create(
        body="Hello from Python!",
        from_=FROM_NO,  # Your Twilio phone number
        to=to_phone,  # Recipient's phone number
    )


def send_whatsapp_message(to_phone: str) -> None:
    global FROM_NO
    print("Send whatsapp msg")
    whatsapp_message = client.messages.create(
        body="Hello there!", from_=f"whatsapp:{FROM_NO}", to=f"whatsapp:{to_phone}"
    )


def send_messages():
    global email_seen_count
    global email_failed_count
    for index, row in csvFile.iterrows():
        to_phone = row["Phone"]
        to_email = row["Email"]

        # Send Email
        send_email(to_email)

        # Send SMS
        send_sms(to_phone)

        # Send Whatsapp Msg
        send_whatsapp_message(to_phone)


def emails_delivered_and_received():
    global email_read_count
    with open("email_seen.log", "r") as file:
        lines = file.readlines()

        # Filter lines containing '200'
        lines_with_200 = [line.strip() for line in lines if line.endswith("200 -\n")]

        # Print filtered lines
        for line in lines_with_200:
            email_read_count += 1


def sms_delivered_and_sent():
    global sms_delivered_count
    global sms_sent_count
    delivery_receipts = (
        client.conversations.v1.conversations("CHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        .messages("IMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        .delivery_receipts.list(limit=20)
    )

    for record in delivery_receipts:
        if record.status == "delivered":
            sms_delivered_count += sms_delivered_count + 1
        elif record.status == "sent":
            sms_sent_count += sms_sent_count + 1


def whatsapp_delivered_and_sent():
    global sms_delivered_count
    global sms_sent_count
    delivery_receipts = (
        client.conversations.v1.conversations("CHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        .messages("IMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        .delivery_receipts.list(limit=20)
    )

    for record in delivery_receipts:
        if record.status == "delivered":
            sms_delivered_count += sms_delivered_count + 1
        elif record.status == "read":
            sms_sent_count += sms_sent_count + 1


# Defining a function to toggle
# between light and dark theme
def light_and_dark_toggle(
    root,
    content,
    text_label,
    input_button,
    report_button,
    dashboard_button,
    theme_changer_button,
):
    global switch_value, bg_colour, fg, theme_switcher_text
    if switch_value:
        bg_colour = "black"
        fg_colour = "white"
        theme_switcher_text = "🌞"
        switch_value = False
    else:
        bg_colour = "white"
        fg_colour = "black"
        theme_switcher_text = "🌚"
        switch_value = True

    root.config(bg=bg_colour)
    content.config(bg=bg_colour)
    text_label.config(fg=fg_colour, bg=bg_colour)
    input_button.config(fg=fg_colour, bg=bg_colour)
    report_button.config(fg=fg_colour, bg=bg_colour)
    dashboard_button.config(fg=fg_colour, bg=bg_colour)
    theme_changer_button.config(fg=fg_colour, bg=bg_colour, text=theme_switcher_text)


def create_ui():
    root = tk.Tk()
    root.title("PyMessage")
    root.config(bg=bg_colour)
    content = tk.Frame(root)
    content.place(relx=0.5, rely=0.5, anchor="center")
    content.config(bg=bg_colour)

    text_label = tk.Label(
        content, bg=bg_colour, font=tkFont.Font(size=24), text="Welcome to PyMessage!"
    )
    input_button = tk.Button(
        content, bg=bg_colour, text="Input", command=lambda: input_excel()
    )
    report_button = tk.Button(
        content, bg=bg_colour, text="Run Report", command=lambda: send_messages()
    )
    dashboard_button = tk.Button(
        content, bg=bg_colour, text="Open Dashboard", command=lambda: dashboard()
    )
    theme_changer_button = tk.Button(
        root,
        bg=bg_colour,
        text=theme_switcher_text,
        command=lambda: light_and_dark_toggle(
            root,
            content,
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
    root.mainloop()


def dashboard():
    dashboard_tk = tk.Toplevel()
    tk.Label(dashboard_tk, text="Emails Sent & Opened By User").pack()
    emails_text = tk.Text(dashboard_tk, height=5, width=52)
    tk.Label(dashboard_tk, text="SMS Sent & Received").pack()
    sms_text = tk.Text(dashboard_tk, height=5, width=52)
    tk.Label(dashboard_tk, text="WhatsApp messages Sent & Read").pack()
    whatsapp_text = tk.Text(dashboard_tk, height=5, width=52)
    emails_delivered_and_received()
    # sms_delivered_and_sent()
    # whatsapp_delivered_and_sent()

    emails_text.insert(tk.END, f"{email_count[0]}\t{email_count[1]}")
    sms_text.insert(tk.END, f"{sms_count[0]}\t{sms_count[1]}")
    whatsapp_text.insert(tk.END, f"{whatsapp_count[0]}\t{whatsapp_count[1]}")

    emails_text.pack()
    sms_text.pack()
    whatsapp_text.pack()


def main():
    create_ui()


if __name__ == "__main__":
    main()
