import os
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request

app = Flask(__name__)
slack_api_client = SlackClient(os.environ['SLACK_API_TOKEN'])
slack_bot_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])

slack_api_client.api_call("api.test")

def is_request_valid(request):
  is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
  is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
  return is_token_valid and is_team_id_valid

@app.route('/', methods=['POST'])
def test():
  print("in test")
  if not is_request_valid(request):
    print("not valid")
    abort(400)

  payload = {
    response_type = 'in_channel',
    text = 'hello world!'
  }
    
  return jsonify(
    response_type='in_channel',
    text='<https://youtu.be/frszEJb0aOo|General Kenobi!>',)

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