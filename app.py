import pandas as pd
import streamlit as st
import time
import re
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import datetime
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Sidebar Navigation
load_dotenv()

api_key = os.getenv('API_KEY')
smtp_password = os.getenv('SMTP_PASSWORD')
smtp_login = os.getenv('SMTP_LOGIN')
sender_email = os.getenv('SENDER_EMAIL')
brevo_api_key = os.getenv('BREVO_API_KEY')

error_log_path = "email_errors.log"

# Streamlit UI: Title and Description
st.title("Custom Email Sender")
st.write("Upload your CSV, customize email content, and send personalized emails!")

# Create a navigation menu
option = st.selectbox(
    "Select an option",
    ["Email Sender", "Email Statistics"]
)

# Step 1: Email Sender Application
if option == "Email Sender":

    def generate_email_content(row, email_body_template):
        try:
            # Example prompt: "Generate an email for a customer named {Name} who is interested in {Product}"
            prompt = email_body_template.format(**row.to_dict())

            # Sending the request to Groq API for LLM processing
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"Error in LLM request: {response.status_code}, {response.text}")
        except Exception as e:
            st.error(f"Error generating email content: {e}")
            return None


    # Step 1: Upload CSV
    st.header("Step 1: Upload CSV")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)
            st.write("Preview of your data:")
            st.write(data.head())
            if 'Email' not in data.columns:
                st.error("Your CSV must include an 'Email' column.")
            else:
                st.session_state['data'] = data
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    # Step 2: Customize Email Template
    if 'data' in st.session_state:
        st.header("Step 2: Customize Email Template")
        columns = st.session_state['data'].columns.tolist()
        st.text("Available placeholders: " + ", ".join([f"{{{col}}}" for col in columns]))

        email_subject = st.text_input("Email Subject", value="Discover Our Exclusive Product Line – Just for You!")
        email_body = st.text_area(
            "Email Content (use placeholders like {ColumnName})",
            "Hello {Company Name},\n\nWe are excited to share our product {Products} with you!"
        )

        # Preview Email
        if st.button("Preview Email"):
            try:
                sample_row = st.session_state['data'].iloc[0].to_dict()
                preview = email_body.format(**sample_row)
                st.subheader("Preview Email Content:")
                st.write(preview)
            except KeyError as e:
                st.error(f"Missing placeholder data: {e}")
            except Exception as e:
                st.error(f"Error formatting preview: {e}")

        st.session_state.update({'email_subject': email_subject, 'email_body': email_body})

    # Step 3: Configure SMTP
    st.header("Step 3: Configure Email Account")
    smtp_server = st.text_input("SMTP Server", value="smtp-relay.brevo.com")
    smtp_port = st.number_input("SMTP Port", value=587, step=1)

    sender_email = st.text_input("Sender Email", value=sender_email)

    st.session_state.update({
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "smtp_login": smtp_login,
        "smtp_password": smtp_password,
        "sender_email": sender_email
    })

    # Step 4: Send Emails
    if 'email_body' in st.session_state and 'data' in st.session_state:
        st.header("Step 4: Send Emails")
        if st.button("Send Emails"):
            success_count, failure_count = 0, 0
            for index, row in st.session_state['data'].iterrows():
                try:
                    # Validate email format
                    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    if not re.match(email_regex, row['Email']):
                        st.error(f"Invalid email format: {row['Email']}")
                        failure_count += 1
                        continue

                    # Generate email content using LLM
                    email_content = generate_email_content(row, st.session_state['email_body'])

                    if not email_content:
                        failure_count += 1
                        continue

                    # Set up the MIMEText object (email content)
                    message = MIMEMultipart()
                    message["From"] = st.session_state['sender_email']
                    message["To"] = row['Email']
                    message["Subject"] = st.session_state['email_subject']
                    message.attach(MIMEText(email_content, "plain"))

                    # Connect to the SMTP server and send the email
                    try:
                        server = smtplib.SMTP(st.session_state['smtp_server'], st.session_state['smtp_port'])
                        server.starttls()  # Encrypt the connection
                        server.login(st.session_state['smtp_login'],
                                     st.session_state['smtp_password'])  # Login to the server
                        server.sendmail(st.session_state['sender_email'], row['Email'],
                                        message.as_string())  # Send the email
                        st.success(f"Email sent to: {row['Email']}")
                        success_count += 1
                    except Exception as e:
                        failure_count += 1
                        with open(error_log_path, "a") as log:
                            log.write(f"Failed to send email to: {row['Email']}. Error: {e}\n")
                        st.error(f"Failed to send email to: {row['Email']}. Check error log.")
                    finally:
                        server.quit()  # Close the connection

                except KeyError as e:
                    failure_count += 1
                    with open(error_log_path, "a") as log:
                        log.write(f"Missing data for email: {row['Email']}. Error: {e}\n")
                    st.error(f"Missing data for email: {e}")
                except Exception as e:
                    failure_count += 1
                    with open(error_log_path, "a") as log:
                        log.write(f"Unexpected error for {row['Email']}: {e}\n")
                    st.error(f"Unexpected error: {e}")

                # Optional: Rate limiting
                time.sleep(1)  # Pause for 1 second between emails

            st.write(f"**Total Emails Sent:** {success_count}")
            st.write(f"**Total Failures:** {failure_count}")
            if failure_count > 0:
                st.info(f"Check the error log at {error_log_path}.")

# Step 2: Email Statistics Application

if option == "Email Statistics":
    if brevo_api_key:
        st.title("Real-Time Email Statistics Dashboard")
        brevo_api_key = st.text_input("Enter Brevo API Key", type="password")

        # Set up Brevo API configuration
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Input for date range
        st.subheader("Specify Date Range for Statistics")
        start_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=7))
        end_date = st.date_input("End Date", value=datetime.date.today())

        # Fetch the statistics when the button is clicked
        if st.button("Fetch Statistics"):
            try:
                # Fetch aggregated SMTP report
                api_response = api_instance.get_aggregated_smtp_report(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )
                st.subheader("Aggregated SMTP Report:")
                st.write(api_response.to_dict())

                # Extract the fetched data
                stats_data = api_response.to_dict()

                # Bar Chart for Delivery Stats (Requests, Delivered, Bounces, etc.)
                st.subheader("Email Delivery Overview")
                fig1 = go.Figure()

                fig1.add_trace(go.Bar(
                    x=["Requests", "Delivered", "Hard Bounces", "Soft Bounces", "Blocked"],
                    y=[stats_data["requests"], stats_data["delivered"], stats_data["hard_bounces"],
                       stats_data["soft_bounces"], stats_data["blocked"]],
                    name="Delivery Stats",
                    marker_color="rgb(55, 83, 109)"
                ))

                fig1.update_layout(
                    title="Email Delivery Statistics",
                    xaxis=dict(title="Metrics"),
                    yaxis=dict(title="Count"),
                    barmode="group"
                )

                st.plotly_chart(fig1)

                # Pie Chart for Opens and Clicks Stats
                st.subheader("Opens and Clicks Overview")
                fig2 = go.Figure()

                fig2.add_trace(go.Pie(
                    labels=["Opens", "Unique Opens", "Clicks", "Unique Clicks", "Spam Reports"],
                    values=[stats_data["opens"], stats_data["unique_opens"], stats_data["clicks"],
                            stats_data["unique_clicks"], stats_data["spam_reports"]],
                    hoverinfo="label+percent",
                    textinfo="value+percent",
                    marker=dict(colors=["#00cc96", "#1f77b4", "#ff7f0e", "#d62728", "#9467bd"])
                ))

                fig2.update_layout(
                    title="Email Engagement Stats",
                )

                st.plotly_chart(fig2)

                # Line Chart for Open and Click Trends (optional for future integration)
                st.subheader("Open and Click Trends (Last 7 Days)")
                fig3 = go.Figure()

                # Simulate time-based trends for opens and clicks (example: past 7 days)
                days = [start_date + datetime.timedelta(days=i) for i in range(7)]
                opens_trend = [stats_data["opens"] for _ in
                               days]  # This is a simplified assumption, use actual time series data if available
                clicks_trend = [stats_data["clicks"] for _ in days]  # Same as above

                fig3.add_trace(
                    go.Scatter(x=days, y=opens_trend, mode="lines+markers", name="Opens", line=dict(color="blue")))
                fig3.add_trace(
                    go.Scatter(x=days, y=clicks_trend, mode="lines+markers", name="Clicks", line=dict(color="red")))

                fig3.update_layout(
                    title="Open and Click Trends (Last 7 Days)",
                    xaxis=dict(title="Date"),
                    yaxis=dict(title="Count"),
                    hovermode="closest"
                )

                st.plotly_chart(fig3)

                # Show additional stats in a table format
                st.subheader("Detailed Statistics")
                stats_table = {
                    "Metric": ["Requests", "Delivered", "Hard Bounces", "Soft Bounces", "Clicks", "Unique Clicks",
                               "Opens",
                               "Unique Opens", "Spam Reports", "Blocked", "Invalid", "Unsubscribed"],
                    "Value": [stats_data["requests"], stats_data["delivered"], stats_data["hard_bounces"],
                              stats_data["soft_bounces"], stats_data["clicks"], stats_data["unique_clicks"],
                              stats_data["opens"],
                              stats_data["unique_opens"], stats_data["spam_reports"], stats_data["blocked"],
                              stats_data["invalid"],
                              stats_data["unsubscribed"]],
                }

                df_stats = pd.DataFrame(stats_table)
                st.write(df_stats)

            except ApiException as e:
                st.error(f"Error fetching SMTP statistics: {e}")
