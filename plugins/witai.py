import os

from slackbot.bot import respond_to
from slackbot.bot import listen_to
from wit import Wit

from wit_actions import actions

wit_client = Wit(
        access_token=os.environ['WIT_API_TOKEN'], 
        actions=actions
        )

@respond_to('')
def wit(message):
    message.react('+1')
    message.reply('Hi!')
    message.reply('You said: ' + message.body['text'])

    wit_client.run_actions('asdf', message.body['text'])
