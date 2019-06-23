import os
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request, make_response
import json

app = Flask(__name__)
slack_api_client = SlackClient(os.environ['SLACK_API_TOKEN'])
slack_bot_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])

slack_api_client.api_call("api.test")

def is_request_valid(request):
  is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
  is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
  return is_token_valid and is_team_id_valid

def list_users():
  users_call = slack_api_client.api_call("users.list")
  if users_call.get('ok'):
    return users_call['channels']
  return None

@app.route('/', methods=['GET'])
def verify():
  return "Success"

@app.route('/test', methods=['POST'])
def test():
  if not is_request_valid(request):
    print("not valid")
    abort(400)
    
  message = request.form
  user_id = message['user_id']
  
  if message['command'] == '/test':
    open_dialog = slack_api_client.api_call(
      "dialog.open",
      trigger_id = message['trigger_id'],
      dialog = {
        "title": "Enter a message",
        "submit_label": "Submit",
        "callback_id": user_id + "test",
        "elements": [
          {
            "label": "Text 1",
            "name": "test1",
            "type": "textarea",
            "hint": "Provide additional information if needed."
          },
          {
            "label": "Text 2",
            "name": "test2",
            "type": "textarea",
            "hint": "Provide additional information if needed."
          },
          {
            "label": "Text 3",
            "name": "test3",
            "type": "textarea",
            "hint": "Provide additional information if needed."
          }
        ]
      }
    )
  
  
  payload = {
    'response_type':'in_channel',
    'text':'hello!'
  }
  
  return jsonify(payload)

@app.route('/interactive', methods=['POST'])
def interactive():
  message = json.loads(request.form['payload'])
  print(message)
  if message['type'] == 'dialog_submission':
    print("Received")
  return make_response("", 200)

if __name__ == "__main__":
  app.run()
  
  '''
def list_channels():
  channels_call = slack_api_client.api_call("channels.list")
  if channels_call.get('ok'):
    return channels_call['channels']
  return None
'''
  
  '''
def send_message(channel_id, message):
  slack_api_client.api_call(
    "chat.postMessage",
    channel=channel_id,
    text=message,
    username='pythonbot',
    icon_emoji=':robot_face:'
  )
'''
  
  '''
  channels = list_channels()
  if channels:
    print("Channels: ")
    for c in channels:
      print(c['name'] + " (" + c['id'] + ")")
      if c['name'] == 'general':
        send_message(c['id'], "Hello " + c['name'] + "!")
  else:
    print("Unable to authenticate.")
  '''