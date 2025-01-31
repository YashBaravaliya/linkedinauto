from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    WHATSAPP_FROM_NUMBER = os.getenv("WHATSAPP_FROM_NUMBER")
    WHATSAPP_TO_NUMBER = os.getenv("WHATSAPP_TO_NUMBER")
    LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")