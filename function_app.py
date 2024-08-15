import azure.functions as func
import datetime
import json
import logging
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = func.FunctionApp()

@app.queue_trigger(
    arg_name="azqueue"
    , queue_name="activateaccounts"
    , connection="QueueAzureWebJobsStorage"
)
def QueueTriggerFunctionActivateAccount(azqueue: func.QueueMessage):
    body = azqueue.get_body().decode('utf-8')

    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))

    SECRET_KEY_FUNC = os.getenv('SECRET_KEY_FUNC')

    response = requests.post(
        f"https://api-otd-dev.azurewebsites.net/user/{body}/code",
        headers={"Authorization": SECRET_KEY_FUNC}
    )
    response.raise_for_status()
    code = response.json().get('code')

    message = MIMEText(f" Your activation code is: {code}")
    message['Subject'] = 'Test Email'
    message['From'] = sender
    message['To'] = body

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [body], message.as_string())
        logging.info(f"Email sent to {body}")
    except Exception as e:
        logging.error(f"Failed to send email to {body}: {str(e)}")

    logging.info('Python Queue trigger processed a message: %s', body )
