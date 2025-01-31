from twilio.rest import Client
from datetime import datetime, timedelta
import time

class WhatsAppService:
    def __init__(self,account_sid,auth_token):
        self.client = Client(account_sid, auth_token)


    def sand_message(self,recepient, message):
        try:
            message = self.client.messages.create(
                from_='whatsapp:+14155238886',
                body={message},
                to=f'whatsapp:{recepient}'
            )
            print(f"Message sent to {recepient} Message Sid {message.sid}")
            return message.sid 
        except Exception as e:
            print(f"Error sending message to {recepient} Error: {e}")
            return e


if __name__ == "__main__":
    whatsapp_service = WhatsAppService("AC896e93df5319d6a7d8a41347c8f2ff41","ee3f404d96d7c893074fb71649c78673")
    whatsapp_service.sand_message("whatsapp:+919601340723","Hello from Python")