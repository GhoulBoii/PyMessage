<a name="readme-top"></a>
<h1 align="center"> 🐍 PyMessage 📬 </h1>
<h3 align="center">Multichannel Messaging Automator</h3>

<p align="center">
  <img src="https://github.com/GhoulBoii/PyMessage/assets/78494833/36b54b52-5cf2-4533-89ac-5f68e472906f" />
</p>

# About The Project
Python application to send emails, SMS and WhatsApp message on the click of a button. You also can see the total count of sent and seen messages and read through threads of each user.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#format-of-inputted-csv-file">Format of Inputted CSV File</a></li>
    <li><a href="#credits">Credits</a></li>
  </ol>
</details>

# Prerequisites

- python 3.12+ [**Not tested on older versions**]
- [credentials.json](https://developers.google.com/gmail/api/quickstart/python) [**Used for sending emails and display threads**]
- [Paid Twilio Account](https://help.twilio.com/articles/223183208-Upgrading-to-a-paid-Twilio-Account) [**Used for sending SMS**]
- [playit](https://playit.gg/) [**Optional, Used for seeing Seen Emails**]
<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Installation

1. Clone the repo
```sh
git clone https://github.com/ghoulboii/pymessage
```

2. Install dependencies
```sh
pip install -r requirements.txt
```

3. Pull submodules
```sh
git submodule init
git submodule update
```

4. Create a .env in the root of the project following the .env.example template

5. Place credentials.json into the root of the project

6. Run main.py
<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Format of Inputted CSV File

The application only accepts CSV files. The CSV file should be of the following format:

| Name | Phone | Email | Course Name |
| ------------- | -------------- | -------------- | -------------- |
| John Smith | +911234567890 | johnsmith@example.com | Python Fundamentals |
| Matthew King | 1234567890 | matthewking@example.com | Python Advanced |

> [!NOTE]
> Phone can be written with or without area code
<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Credits

- [Interakt](https://www.interakt.shop/) for sending messages through WhatsApp
- [Twilio](https://www.twilio.com/en-us) for sending and receiving SMS
- [Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) for sending emails and reading threads
- [Ethan's Tech](https://ethans.co.in/) for providing me tools to complete this project
<p align="right">(<a href="#readme-top">back to top</a>)</p>
