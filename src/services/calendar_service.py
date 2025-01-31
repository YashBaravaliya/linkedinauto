import os
import json
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleCalendarManager:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.credentials_file = "credentials.json"
        self.token_file = 'token.json'
        self.service = self.authenticate_google()

    def authenticate_google(self):
        """Authenticate and return the Google Calendar API service."""
        creds = None

        # Load token.json if it exists
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

        # If credentials are not valid, initiate OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)

            # Save the credentials for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        return build('calendar', 'v3', credentials=creds)

    def list_events(self, max_results=10):
        """Fetch and return upcoming events in JSON format."""
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return json.dumps({"events": [], "message": "No upcoming events found."})

        # Create a list of event details
        all_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            all_events.append({
                "title": event.get('summary', 'No title'),
                "start_time": start,
                "event_id": event.get('id', 'No ID'),
                "description": event.get('description', 'No description available'),
                "location": event.get('location', 'No location available'),
            })

        # Return as JSON
        return json.dumps({"events": all_events})
    
    def fetch_indian_festival(self):
        """Fetch and return Indian public holidays in JSON format."""
        # Indian Holidays calendar ID (provided by Google)
        indian_holidays_calendar_id = 'en.indian#holiday@group.v.calendar.google.com'
        
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # Current time in UTC
        events_result = self.service.events().list(
            calendarId=indian_holidays_calendar_id,
            timeMin=now,
            maxResults=50,  # Adjust this as needed
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return json.dumps({"events": [], "message": "No upcoming holidays found."})

        # Create a list of holiday details
        holidays = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            holidays.append({
                "title": event['summary'],
                "start_date": start,
                # "event_id": event['id'],
                # "description": event.get('description', 'No description available'),
                # "location": event.get('location', 'No location available'),
            })

        # Return as JSON
        return json.dumps({"events": holidays})

# Example usage
if __name__ == "__main__":
    calendar_manager = GoogleCalendarManager()
    festival = calendar_manager.fetch_indian_festival()
    for event in json.loads(festival)["events"]:
        print(event)
    # print(calendar_manager.list_events())