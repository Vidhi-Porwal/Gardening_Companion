import requests
from bson import ObjectId

def trigger_airflow_email_task(user, data, plant_common_name):
    subject = f"New Plant Added to Your Garden: {plant_common_name}"
    body = f"""
        Hello {user.get('full_name', 'Gardener')},

        A new plant has been added to your garden:

        🌱 Common Name: {plant_common_name}
        💧 Watering every {data['watering']} days
        🌞 Sunlight requirement: {data['sunlight']}
        🌾 Fertilizer: {data['fertilizer_type']}
        🪴 Soil Type: {data['soil_type']}
        ♻️ Change soil every {data['change_soil']} months

        Happy Gardening! 🌼

        - Garden Team
    """

    airflow_url = "http://localhost:8080/api/v1/dags/send_email_task/dagRuns"
    response = requests.post(
        airflow_url,
        auth=("airflow", "airflow"),  # Replace with actual creds
        headers={"Content-Type": "application/json"},
        json={
            "conf": {
                "subject": subject,
                "recipients": [user["email"]],
                "body": body
            }
        }
    )

    return response.status_code, response.json()
