import requests
import json
from dotenv import load_dotenv
import os

def send_notification(topic, message, priority=None, title=None, tags=None):
    url = f"https://ntfy.sh/{topic}"
    
    try:
        response = requests.post(url, data=message)
        if response.status_code in [200, 201]:
            print(f"Notification sent successfully to {topic}")
            return True
        else:
            print(f"Failed to send notification. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    TOPIC = os.getenv("NOTIFY_CHANNEL")
    send_notification(TOPIC, "Hello from Python!")
    