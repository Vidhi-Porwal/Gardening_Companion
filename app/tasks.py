# from celery_config import make_celery
# # from app import app, mail, Message

# celery = make_celery(app)

# @celery.task
# def send_email_task(email, subject, body):
#     with app.app_context():
#         msg = Message(subject, recipients=[email])
#         msg.body = body
#         mail.send(msg)
        # return f"Email sent to {email}!"
# from celery import shared_task
# from flask_mail import Message
# from flask import current_app
# from . import mail

# @shared_task
# def send_plant_added_email(user_email, plant_name):
#     print("function")
#     with current_app.app_context():
#         print("0000")
#         msg = Message(
#             subject="Plant Added to Your Garden!",
#             sender=current_app.config['MAIL_DEFAULT_SENDER'],
#             recipients=[user_email],
#         )
#         print("1111")
#         msg.body = f"Hello,\n\nThe plant '{plant_name}' has been successfully added to your garden. Happy gardening!\n\nBest Regards,\nGardening Companion Team"
#         mail.send(msg)
from celery import shared_task
from flask_mail import Message
from flask import current_app
from app import mail
from datetime import datetime, timedelta
# from app import app, mail, Message
@shared_task
def send_plant_added_email(user_email, plant_name):
    with current_app.app_context():
        msg = Message(
            subject="Plant Added to Your Garden!",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user_email],
        )
        msg.body = f"Hello,\n\nThe plant '{plant_name}' has been successfully added to your garden. Happy gardening!\n\nBest Regards,\nGardening Companion Team"
        mail.send(msg)

# @shared_task
# def send_fertilizer_notification():
#     """Check for plants due for fertilizer and send notifications."""
#     db_connection = current_app.config['DB_CONNECTION']()
#     try:
#         with db_connection.cursor() as cursor:
#             query = """
#                 SELECT up.id, up.user_id, up.created_at, up.fertilizing, u.email 
#                 FROM UserPlant up
#                 JOIN User u ON up.user_id = u.id
#                 WHERE DATE_ADD(up.created_at, INTERVAL up.fertilizing DAY) <= NOW();
#             """
#             cursor.execute(query)
#             plants = cursor.fetchall()

#             for plant in plants:
#                 send_email(plant['email'], f"Fertilizer Reminder for Plant ID {plant['id']}", 
#                            f"Hi, it's time to fertilize your plant (ID: {plant['id']}). Please do so today!")

#     finally:
#         db_connection.close()

# @shared_task
# def send_watering_notification():
#     """Check for plants due for watering and send notifications."""
#     db_connection = current_app.config['DB_CONNECTION']()
#     try:
#         with db_connection.cursor() as cursor:
#             query = """
#                 SELECT up.id, up.user_id, up.created_at, up.watering, u.email 
#                 FROM UserPlant up
#                 JOIN User u ON up.user_id = u.id
#                 WHERE DATE_ADD(up.created_at, INTERVAL up.watering DAY) <= NOW();
#             """
#             cursor.execute(query)
#             plants = cursor.fetchall()

#             for plant in plants:
#                 send_email(plant['email'], f"Watering Reminder for Plant ID {plant['id']}", 
#                            f"Hi, it's time to water your plant (ID: {plant['id']}). Please do so today!")

#     finally:
#         db_connection.close()

# def send_email(recipient, subject, body):
#     """Send an email using Flask-Mail."""
#     msg = Message(subject=subject, recipients=[recipient], body=body)
#     with current_app.app_context():
#         mail.send(msg)
# from celery import shared_task
# from flask_mail import Message
# from flask import current_app
# from . import mail, celery  # Import Celery instance

from .celery_app import make_celery
# celery = make_celery(app)
from celery import Celery
@shared_task
def send_periodic_email(user_email, plant_name):
    """Send an email reminder about the plant."""
    with current_app.app_context():
        msg = Message(
            subject="Plant Reminder",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user_email],
            body=f"Hello,\n\nYour plant '{plant_name}' is still active in your garden.\n\nBest,\nGardening Companion"
        )
        mail.send(msg)

def schedule_email_for_plant(user_email, plant_name, plant_id):
    """Schedule an email every 2 minutes for a specific plant."""
    print("hkjhjhj")
    task_id = f"email_task_{plant_id}"

    print("task is ",task_id)
    
    celery = Celery(
        current_app.import_name,
        backend=current_app.config['CELERY_RESULT_BACKEND'],
        broker=current_app.config['CELERY_BROKER_URL']
    )
    # Add dynamic task to beat_schedule
    celery.conf.beat_schedule[task_id] = {
        'task': 'tasks.send_periodic_email',
        'schedule': 120.0,  # 2 minutes in seconds
        'args': (user_email, plant_name),
    }