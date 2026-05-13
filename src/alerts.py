import os
from twilio.rest import Client

def send_sms_alert(aqi, city):

    if aqi < 150:
        return

    sid = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    from_num = os.getenv("TWILIO_PHONE")
    to_num = os.getenv("MY_PHONE")

    if not all([sid, token, from_num, to_num]):
        return

    client = Client(sid, token)

    message = f"⚠ AQI ALERT in {city}: {aqi}. Take precautions."

    client.messages.create(
        body=message,
        from_=from_num,
        to=to_num
    )