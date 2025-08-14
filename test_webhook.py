import requests
import json

# Test the webhook endpoint
url = "http://localhost:8000/v1/webhook/"
payload = {
    "contactId": "test123",
    "type": "sms", 
    "message": "hello world"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Contact ID: {data.get('contactId')}")
        print(f"Response ID: {data.get('responseId')}")
        print(f"Response Message: {data.get('responseMessage')}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
