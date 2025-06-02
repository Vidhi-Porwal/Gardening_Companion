from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from email.message import EmailMessage
import smtplib
import pendulum
from config import Config

def send_email(**context):
    conf = context["dag_run"].conf or {}
    subject = conf.get("subject", "Default Subject")
    recipients = conf.get("recipients", [])
    body = conf.get("body", "")

    if not recipients:
        raise ValueError("No recipients provided!")

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = Config.MAIL_USERNAME
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        smtp.send_message(msg)

with DAG(
    dag_id="send_email",
    start_date=pendulum.datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    tags=["manual", "email"],
) as dag:
    send_email_task = PythonOperator(
        task_id="send_email",
        python_callable=send_email,
        priority_weight=5
    )


def watering_notification():
    recipients = []
    subject = "Reminder Water Your Plants"
    body = "water yout plants today"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = Config.MAIL_USERNAME
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        smtp.send_message(msg)

with DAG(
    dag_id="daily_plant_watering",
    schedule="0 8 * * *",  
    start_date=pendulum.datetime(2023, 1, 1),
    catchup=False,
    tags=["daily", "email"],
) as dag:
    daily_task = PythonOperator(
        task_id="watering_notification",
        python_callable=watering_notification,
        priority_weight=5
    )
def fertilizer_reminder():
    recipients = ["user@example.com"]
    subject = "Monthly Reminder: Fertilize Your Plants 🌼"
    body = "It's time to fertilize your plants for healthy growth!"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = Config.MAIL_USERNAME
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        smtp.send_message(msg)

with DAG(
    dag_id="monthly_fertilizer_reminder",
    schedule="0 9 1 * *",  
    start_date=pendulum.datetime(2023, 1, 1),
    catchup=False,
    tags=["monthly", "email"],
) as dag:
    monthly_task = PythonOperator(
        task_id="fertilizer_reminder",
        python_callable=fertilizer_reminder,
        priority_weight=10
    )
