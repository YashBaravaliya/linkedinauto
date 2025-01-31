# LinkedIn Holiday Post Automation

This Flask application automatically generates and posts LinkedIn content for Indian holidays. It checks for holidays daily and creates draft posts with email notifications.

## Features

- 🗓️ Automatic holiday detection from Google Calendar
- ✍️ AI-powered post generation using Mistral AI
- 📱 LinkedIn draft post creation
- ⏰ Scheduled daily checks at 10 AM
- 🌐 API endpoint for manual generation

## Project Structure

```
linkedin_automation/
├── .env
├── requirements.txt
├── app.py
└── src/
    ├── __init__.py
    ├── config.py
    ├── services/
    │   ├── __init__.py
    │   ├── linkedin_service.py
    │   ├── calendar_service.py
    │   ├── post_generator.py
    └── utils/
        ├── __init__.py
        └── constants.py
```

## Prerequisites

- Python 3.8 or higher
- A LinkedIn Developer account

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YashBaravaliya/LinkedIn-automation-
cd linkedin_automation
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```


### 3. Google Calendar API Setup

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials file and save as `credentials.json`

### 4. LinkedIn API Setup

1. Go to LinkedIn Developer Portal (https://www.linkedin.com/developers/)
2. Create a new app
3. Request access to UGC Post API
4. Get your access token

### 5. Environment Variables

Create a `.env` file in the root directory:

```env
MISTRAL_API_KEY=your_mistral_api_key
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
GOOGLE_CALENDAR_CREDENTIALS=path_to_credentials.json
```

## Running the Application

### Local Development

```bash
python app.py
```


## API Endpoints

- `GET /generate-post`: Manually trigger post generation for today's holiday (if any)

## Scheduling

The application automatically runs at 10 AM daily to:
- Check for holidays on the current date
- Generate and save LinkedIn post drafts if a holiday is found
- Send email notifications about the status

