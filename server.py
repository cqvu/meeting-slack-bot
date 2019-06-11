import os
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request

app = Flask(__name__)
slack_api_client = SlackClient(os.environ['SLACK_API_TOKEN'])
print(os.environ['SLACK_BOT_TOKEN'])
#slack_bot_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])


slack_api_client.api_call("api.test")

def list_channels():
  channels_call = slack_api_client.api_call("channels.list")
  if channels_call.get('ok'):
    return channels_call['channels']
  return None

def is_request_valid(request):
  is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
  is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

  return is_token_valid and is_team_id_valid
'''
@app.route('/test', methods=['POST'])
def test():
  if not is_request_valid(request):
    abort(400)

  payload = {
    response_type = 'in_channel',
    text = 'hello world!'
  }
    
  return jsonify(payload)
'''

if __name__ == "__main__":
  channels = list_channels()
  if channels:
    print("Channels: ")
    for c in channels:
      print(c['name'] + " (" + c['id'] + ")")
    else:
      print("Unable to authenticate.")
