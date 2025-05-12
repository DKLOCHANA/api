from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import threading
import time
from twilio.rest import Client
import os

app = FastAPI()
phone_records = {}

# Twilio config from environment
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

class PhoneData(BaseModel):
    phone: str
    timestamp: str

@app.post("/save-number")
def save_number(data: PhoneData):
    phone_records[data.phone] = datetime.fromisoformat(data.timestamp)
    return {"status": "saved"}

# Background thread
def sms_watcher():
    while True:
        now = datetime.utcnow()
        for phone, ts in list(phone_records.items()):
            if now - ts > timedelta(minutes=10):
                try:
                    client.messages.create(
                        body="10 minutes have passed!",
                        from_=TWILIO_PHONE,
                        to=phone
                    )
                    print(f"Sent SMS to {phone}")
                    del phone_records[phone]
                except Exception as e:
                    print(f"SMS error: {e}")
        time.sleep(60)

threading.Thread(target=sms_watcher, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
