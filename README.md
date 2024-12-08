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
