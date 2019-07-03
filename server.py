import os, requests, json
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request, make_response
from pprint import pprint
import pyrebase

app = Flask(__name__)
slack_api_client = SlackClient(os.environ['SLACK_API_TOKEN'])
slack_bot_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])
slack_api_client.api_call("api.test")

# Firebase configurations
config = {
  "apiKey": os.environ['FIREBASE_APIKEY'],
  "authDomain": os.environ['FIREBASE_AUTHDOMAIN'],
  "databaseURL": os.environ['FIREBASE_DATABASEURL'],
  "storageBucket": os.environ['FIREBASE_STORAGEBUCKET']
}
# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()
db = db.child('slack-bot-245306')

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
  
def get_member_name(user_id):
  user_info = slack_bot_client.api_call("users.info", user=user_id)
  return user_info['user']['real_name']

@app.route('/', methods=['GET'])
def verify():
  return "Success"

@app.route('/createnote', methods=['POST'])
def createnote():
  if not is_request_valid(request):
    print("not valid")
    abort(400)

  message = request.form
  file_name = message['text']
  
  headers = {
    'Content-Type': 'application/json',
  }
  data = {
    "value1": file_name
  }
  ifttt_makenote_url = "https://maker.ifttt.com/trigger/makenote/with/key/coqoCKj-CvTtB6KT-ZQda-"
  response = requests.post(url=ifttt_makenote_url, json = data)

  payload = {
    'response_type':'in_channel',
    'text':'Created ' + file_name + " in Google Drive!"
  }
  
  doc_file = open("doc.txt", "w+")
  doc_file.write(file_name)
  doc_file.close()
  
  return jsonify(payload)
  
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

@app.route('/actionitem', methods=['POST'])
def actionitem():
  if db.get().val() == None:
    members = get_members_id("CK5HEF5R7")
    for member in members:
      data = { "name": get_member_name(member),
               "actionitems": []
             }
      
      db.child(member).set(data)
    
  message = request.form['text']
  print(message)
  
  assignee = message[message.find('@')+1: message.find('|')]
  task = message[message.find('>')+2::]
  cur_items = db.child(assignee).child('actionitems').get().val()
  
  print('cur_items:', cur_items)
  if cur_items == None:
    print("IN HERE")
    cur_items = []
    
  print(cur_items)
  cur_items.append(task)
  print('after:', cur_items)
  
  db.child(assignee).child('actionitems').set(cur_items)
  
  payload = {
    'response_type':'in_channel',
    'text':'Added'
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
                  "value": "Mentorship"
                },
                {
                  "label": "Projects Team",
                  "value": "Projects"
                },
                {
                  "label": "Professional",
                  "value": "Professional"
                },
                {
                  "label": "Faculty Mixer",
                  "value": "Faculty Mixer"
                },
                {
                  "label": "Town Hall",
                  "value": "Town Hall"
                },
                {
                  "label": "Destressers",
                  "value": "Destresser"
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
                  "value": "Mentorship"
                },
                {
                  "label": "Projects Team",
                  "value": "Projects"
                },
                {
                  "label": "Professional",
                  "value": "Professional"
                },
                {
                  "label": "Faculty Mixer",
                  "value": "Faculty Mixer"
                },
                {
                  "label": "Town Hall",
                  "value": "Town Hall"
                },
                {
                  "label": "Destressers",
                  "value": "Destressers"
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
    doc_file = open("doc.txt", "r")
    submission = message['submission']
    
    # Get the last saved meeting notes doc
    file_name = doc_file.readline()
    
    # Format content to be sent to meeting notes doc
    content = ""
    
    content += submission['first'] + ": \n" + "<br>"
    content += submission['topic1'].replace("\n", "<br>")
    content += "<br>"
    if submission['second'] != None:
      content += submission['second'] + ": \n" + "<br>"
      content += submission['topic2'].replace("\n", "<br>")
    
    if submission['third'] != None:
      content += submission['third'] + ": \n" + "<br>"
      content += submission['topic3'].replace("\n", "<br>")
    
    headers = {
      'Content-Type': 'application/json',
    }
    data = {
      "value1": file_name,
      "value2": content
    }
    
    print(content)
    
    ifttt_addnote_url = "https://maker.ifttt.com/trigger/addnote/with/key/coqoCKj-CvTtB6KT-ZQda-"
    response = requests.post(url=ifttt_addnote_url, json = data)
    
    print(response.status_code, response.reason)
    
    confirm_res = slack_bot_client.api_call("chat.postMessage",channel=user_id,text="Gotcha, thanks!", as_user=True)
    
  return make_response("", 200)

if __name__ == "__main__":
  app.run()