import sendgrid, os
from flask_slack import Slack
from flask import Flask
from slacker import Slacker
import time

# 
TEAM_ID = os.environ.get('TEAM_ID')
SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
SCRATCH_COMMAND_TOKEN = os.environ.get('SCRATCH_COMMAND_TOKEN')

# Initalize everything
app = Flask(__name__)
slash = Slack(app)
slack = Slacker(SLACK_API_TOKEN)

# Get list of users in slack org
user_list = slack.users.list().body['members']
emails = filter(None, [u['profile']['email'] for u in user_list])
admins = set(u['id'] for u in user_list if u['is_admin'])


@slash.command(command='email', token=SCRATCH_COMMAND_TOKEN, team_id=TEAM_ID, methods=['POST'])
def email_command(**kwargs):
    text = kwargs.get('text')

    # check if user is admin
    user_id = kwargs.get('user_id')
    if user_id in admins :
        return slash.response("Sorry, you must be an admin to use this command.")

    msg = send_email(text)
    return slash.response(msg)

def send_email(body) :
    responses = []
    for email in emails :
        message = sendgrid.Mail(to=email, subject='Code Orange Update', text=body, from_email='info@codeorange.io')
        status, msg = sg.send(message)
        responses.append(status)
    
    if all(response == 200 for response in responses) :
        return "Successfully sent messages."
    else :
        return "Something fucked up... sorry :-("


app.add_url_rule('/send', view_func=slash.dispatch)

if __name__ == '__main__':
    app.run()
