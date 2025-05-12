from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import threading
import time
from twilio.rest import Client
import pytz  # To handle timezones
import os

app = FastAPI()
phone_records = {}

# Directly storing Twilio config
TWILIO_SID = "ACb13005110eaf346d809e40aa745cf66c"
TWILIO_AUTH_TOKEN = "0806c548309adc4700ff19a1569cbea9"
TWILIO_PHONE = "+18155590365"

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Sri Lanka Timezone
SLT = pytz.timezone('Asia/Colombo')

class PhoneData(BaseModel):
    phone: str
    timestamp: str

@app.post("/save-number")
def save_number(data: PhoneData):
    # Convert the timestamp to Sri Lankan Time (SLT)
    timestamp = datetime.fromisoformat(data.timestamp).astimezone(SLT)
    phone_records[data.phone] = timestamp
    return {"status": "saved"}

# Background thread with timezone handling and error logging
def sms_watcher():
    while True:
        now = datetime.now(SLT)  # Current time in SLT
        print(f"Checking SMS at {now}")  # Log for debugging
        for phone, ts in list(phone_records.items()):
            if now - ts > timedelta(hours=10):  # Check if 10 minutes have passed
                try:
                    message = client.messages.create(
                        body="10 minutes have passed!",
                        from_=TWILIO_PHONE,
                        to=phone
                    )
                    print(f"Sent SMS to {phone}, SID: {message.sid}")
                    del phone_records[phone]
                except Exception as e:
                    print(f"SMS error: {e}")
        time.sleep(60)  # Check every 60 seconds

# Start the background thread
threading.Thread(target=sms_watcher, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
