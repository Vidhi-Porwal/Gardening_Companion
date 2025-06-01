from email.message import EmailMessage
import smtplib
from airflow import DAG
#from airflow.operators.python import PythonOperator
from airflow.providers.standard.operators.python import PythonOperator
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
    print('Task1 processing')
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        smtp.send_message(msg)

with DAG(
    dag_id="send_email_task",
    start_date=pendulum.datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    tags=["email"],
) as dag:
    print('task1')
    task = PythonOperator(
        task_id="send_email",
        python_callable=send_email,
        #provide_context=True,
    )
    task
