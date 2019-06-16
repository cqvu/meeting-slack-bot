import os
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request

app = Flask(__name__)
slack_api_client = SlackClient(os.environ['SLACK_API_TOKEN'])
slack_bot_client = SlackClient(os.environ['SLACK_BOT_TOKEN'])

@app.route('/', methods=['GET'])
def is_request_valid(request):
  is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
  is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
  if is_token_valid and is_team_id_valid:
    return "Success"
  return is_token_valid and is_team_id_valid