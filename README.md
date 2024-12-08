# Custom Email Sender Application

This project is a **Custom Email Sender** application built with **Streamlit** that allows users to upload a CSV file, customize email content, and send personalized emails to recipients. It also includes an **Email Statistics** dashboard to fetch and visualize email delivery and engagement statistics via the **Brevo API**.

## Features

- **Upload CSV**: Upload a CSV file containing recipient data, which must include an `Email` column.
- **Customize Email**: Customize the subject and body of the email using placeholders from the uploaded CSV data.
- **Send Emails**: Send personalized emails using SMTP credentials and a template.
- **Email Statistics**: Fetch real-time email statistics such as open rates, click rates, bounces, etc., from the Brevo API.
- **Error Logging**: Failed email attempts are logged in a file for debugging.

## Requirements

Before running the application, make sure you have the required libraries installed. You can install them using `pip`:

```bash
pip install -r requirements.txt
Setup Instructions
Follow these steps to get the application up and running on your local machine:

Clone this repository to your local machine:

bash
Copy code
git clone https://github.com/your-username/your-repository-name.git
Navigate to the project directory:

bash
Copy code
cd your-repository-name
Install the dependencies:

bash
Copy code
pip install -r requirements.txt
Create a .env file in the project root and add your sensitive information (API keys, SMTP credentials, etc.):

Example .env file:

makefile
Copy code
API_KEY=your_groq_api_key
SMTP_PASSWORD=your_smtp_password
SMTP_LOGIN=your_smtp_login
SENDER_EMAIL=your_sender_email
BREVO_API_KEY=your_brevo_api_key
Run the Streamlit app:

bash
Copy code
streamlit run app.py
Visit the app in your browser (usually http://localhost:8501) to interact with the application.

Usage
1. Email Sender
Step 1: Upload CSV

Upload a CSV file with an Email column. This column will be used to send personalized emails to each recipient.
Step 2: Customize Email Template

Customize your email content by adding placeholders from the CSV file (e.g., {Name}, {Product}). The application will replace these placeholders with actual data from the uploaded CSV.
Step 3: Configure SMTP

Input your SMTP server details, including SMTP server, port, and login credentials. These settings are needed to send the emails.
Step 4: Send Emails

Once you have uploaded the CSV and customized the email content, you can send emails to the recipients in the CSV. The emails are sent one at a time with a pause between each to avoid rate limiting.
Error Logging

If an email fails to send, the error will be logged in the email_errors.log file with details about the email address and the error encountered.
2. Email Statistics
Step 1: Enter Brevo API Key

Input your Brevo API key to fetch email statistics.
Step 2: Specify Date Range

Select the start and end dates for the range of email statistics you want to view.
Step 3: View Email Statistics

The application will fetch aggregated email statistics, such as the number of emails sent, delivered, opened, clicked, and bounced during the specified date range.
Step 4: Visualize Statistics

The statistics are displayed in various charts:
Bar Chart: Shows email delivery metrics (Requests, Delivered, Bounces, etc.)
Pie Chart: Displays engagement metrics (Opens, Clicks, Spam Reports, etc.)
Line Chart: Trends for opens and clicks over the past 7 days (optional).
Error Logging
If an email fails to send, it will be logged in the email_errors.log file. The log will include:

The email address of the recipient
The error message or reason for failure
Example log entry:

vbnet
Copy code
Failed to send email to: recipient@example.com. Error: SMTPAuthenticationError: Invalid login credentials.
Notes
CSV Format: The CSV file must contain a column labeled Email. If the column is missing, the app will display an error.
Email Placeholders: In the email body, you can use placeholders like {First Name}, {Product}, etc. These placeholders will be replaced with data from the corresponding row in the CSV.
SMTP Credentials: Ensure you have valid SMTP credentials and the correct SMTP server settings for sending emails (e.g., Gmail, SendGrid, Brevo).
API Keys: Make sure to add your Groq and Brevo API keys in the .env file for the email generation and statistics fetching features.
License
This project is licensed under the MIT License.

sql
Copy code

This placement ensures that the user knows how to set up the project before using it.






