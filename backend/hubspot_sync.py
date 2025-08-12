import requests
import os

HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

def push_session_to_hubspot(session_id, chat_history):
    url = "https://api.hubapi.com/engagements/v1/engagements"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }

    body = f"Chat Session ID: {session_id}\n\n"
    for msg in chat_history:
        body += f"{msg['role'].capitalize()}: {msg['content']}\n"

    data = {
        "engagement": {
            "active": True,
            "type": "NOTE",
            "timestamp": int(__import__('time').time() * 1000)
        },
        "metadata": {
            "body": body[:32768]  # HubSpot limit
        }
    }

    try:
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code in [200, 201]:
            print(f"✅ HubSpot: Session {session_id} synced.")
        else:
            print(f"❌ HubSpot error {resp.status_code}: {resp.text}")
    except Exception as e:
        print("❌ HubSpot sync failed:", str(e))