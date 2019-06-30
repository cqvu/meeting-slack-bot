import os
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request, make_response
import json
from pprint import pprint
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
slack_api_client = SlackClient(os.environ['SLACK_API_TOKEN'])
slack_bot_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
slack_api_client.api_call("api.test")

def is_request_valid(request):
  is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
  is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
  return is_token_valid and is_team_id_valid

def get_members_id(channel):
  channels_info = slack_bot_client.api_call("channels.info", channel=channel)
  if channels_info.get('ok'):
    return channels_info['channel']['members']
  return None

def check_bot(user_id):
  user_info = slack_bot_client.api_call("users.info", user=user_id)
  if user_info['user']['is_bot']:
    return True
  else:
    return False

@app.route('/', methods=['GET'])
def verify():
  return "Success"

@app.route('/createnote', methods=['POST'])
def createnote():
  if not is_request_valid(request):
    print("not valid")
    abort(400)
  
  '''
  creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server()
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)
      
  service = build('docs', 'v1', credentials=creds)
  print("in createnote")
  title = 'Test Doc'
  body = {
    'title': title
  }
  doc = service.documents() \
    .create(body=body).execute()
  print('Created document with title: {0}'.format(
    doc.get('title')))
  '''
  
  g_login = GoogleAuth()
  g_login.LocalWebserverAuth()
  drive = GoogleDrive(g_login)
  
  file1 = drive.CreateFile({'title': 'Hello'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
  file1.SetContentString('Hello World!') # Set content of the file from given string.
  file1.Upload()
  
@app.route('/remindnotes', methods=['POST'])
def remindnotes():
  if not is_request_valid(request):
    print("not valid")
    abort(400)
    
  message = request.form
  user_id = message['user_id']
  
  if message['command'] == '/remindnotes':
    members = get_members_id("CK5HEF5R7")
    for member in members:
      if not check_bot(member):
        print("Sending to", member)
        attach_json = [
        {
            "fallback": "You are unable use message buttons",
            "callback_id": "addnotes",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "addnotes",
                    "text": "Add Notes",
                    "type": "button",
                    "value": "addnotes"
                }
            ]
        }
        ]
        
        button_res = slack_bot_client.api_call("chat.postMessage",channel=member,text="Add Your Meeting Notes", attachments = attach_json, as_user=True)
  
  payload = {
    'response_type':'in_channel',
    'text':'Sent Add Notes Reminder!'
  }
  
  return jsonify(payload)

@app.route('/interactive', methods=['POST'])
def interactive():
  message = json.loads(request.form['payload'])
  user_id = message['user']['id']
  print("Message in interactive: ", message)
  if message['callback_id'] == 'addnotes':
    open_dialog = slack_api_client.api_call(
      "dialog.open",
      trigger_id = message['trigger_id'],
      dialog = {
        "title": "Add Your Meeting Notes",
        "submit_label": "Submit",
        "callback_id": "meetingnotes " + user_id,
        "elements": [
            {
              "label": "Topic",
              "type": "select",
              "name": "first",
              "options": [
                {
                  "label": "Mentorship",
                  "value": "mentorship"
                },
                {
                  "label": "Projects Team",
                  "value": "project"
                },
                {
                  "label": "Professional",
                  "value": "professional"
                },
                {
                  "label": "Faculty Mixer",
                  "value": "facultymixer"
                },
                {
                  "label": "Town Hall",
                  "value": "townhall"
                },
                {
                  "label": "Destressers",
                  "value": "destress"
                }
              ]
            },
            
            {
              "label": "Notes/Updates",
              "name": "topic1",
              "type": "textarea",
            },
            {
              "label": "Topic",
              "type": "select",
              "name": "second",
              "options": [
                {
                  "label": "Mentorship",
                  "value": "mentorship"
                },
                {
                  "label": "Projects Team",
                  "value": "project"
                },
                {
                  "label": "Professional",
                  "value": "professional"
                },
                {
                  "label": "Faculty Mixer",
                  "value": "facultymixer"
                },
                {
                  "label": "Town Hall",
                  "value": "townhall"
                },
                {
                  "label": "Destressers",
                  "value": "destress"
                }
              ],
              "optional": True
            },
            {
              "label": "Notes/Updates",
              "name": "topic2",
              "type": "textarea",
              "optional": True
            },
            {
              "label": "Others",
              "name": "third",
              "type": "text",
              "placeholder": "Other topic",
              "optional": True
            },
            {
              "label": "Notes/Updates",
              "name": "topic3",
              "type": "textarea",
              "optional": True
            }
        ]
      }
    )
    
  if message['type'] == 'dialog_submission':
    confirm_res = slack_bot_client.api_call("chat.postMessage",channel=user_id,text="Gotcha, thanks!", as_user=True)
    
  return make_response("", 200)

if __name__ == "__main__":
  app.run()