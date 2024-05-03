from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
from datetime import datetime, timedelta
import configparser

# Setting Line Token
config = configparser.ConfigParser()
config.read('config/config.ini')
token = config['LINE']['MY_LINE_NOTIFY_TOKEN']

# Setting Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
creds = None

def get_calendar_events():
    flow = InstalledAppFlow.from_client_secrets_file('json/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    
    # Calculate current time and 24 hours later in Tokyo time
    tokyo_now = datetime.utcnow() + timedelta(hours=9)
    tokyo_tomorrow = tokyo_now + timedelta(days=1)
    
    # ‘Z’ indicates UTC, but the time here is treated as Tokyo time
    now = tokyo_now.isoformat() + 'Z'
    tomorrow = tokyo_tomorrow.isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=tomorrow,
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        if event['summary'] == 'Sakuragaoka5':
            send_line_notify(event['summary'])
            
def send_line_notify(message):
    headers = {'Authorization': 'Bearer ' + token}
    data = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)
    print(response.text)

get_calendar_events()