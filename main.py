from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import threading
import time
from twilio.rest import Client
import pytz
import os

app = FastAPI()
phone_records = {}

# Load Twilio credentials and sender number from Railway environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Sri Lanka Timezone
SLT = pytz.timezone('Asia/Colombo')

class PhoneData(BaseModel):
    phone: str
    timestamp: str

@app.post("/save-number")
def save_number(data: PhoneData):
    timestamp = datetime.fromisoformat(data.timestamp).astimezone(SLT)
    phone_records[data.phone] = timestamp
    return {"status": "saved"}

def sms_watcher():
    while True:
        now = datetime.now(SLT)
        print(f"Checking SMS at {now}")
        
        # Print the Twilio credentials (for debugging purposes)
        print(f"TWILIO_SID: {os.getenv('TWILIO_SID')}")
        print(f"TWILIO_AUTH_TOKEN: {os.getenv('TWILIO_AUTH_TOKEN')}")
        
        for phone, ts in list(phone_records.items()):
            if now - ts > timedelta(hours=12):
                try:
                    message = client.messages.create(
                        body="MyDayMate Alert: No recent activity from Lochana Edirisooriya (0711710593). Last seen over 12 hours ago. Please check in. – MyDayMate",

                        from_=TWILIO_PHONE,
                        to=phone
                    )
                    print(f"Sent SMS to {phone}, SID: {message.sid}")
                    del phone_records[phone]
                except Exception as e:
                    print(f"SMS error: {e}")
        time.sleep(60)

# Start background SMS checker
threading.Thread(target=sms_watcher, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
