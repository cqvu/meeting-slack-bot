import os
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
  print("Running")
  return "Success"

def is_request_valid(request):
  is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
  is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
  return is_token_valid and is_team_id_valid

if __name__ == "__main__":
  app.run()
