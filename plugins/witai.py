import os
import random
import string

from slackbot.bot import respond_to
from slackbot.bot import listen_to
from wit import Wit

from wit_actions import actions

wit_client = Wit(
        access_token=os.environ['WIT_API_TOKEN'], 
        actions=actions
        )

wit_context = {}

def random_word(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

@respond_to('')
def wit(message):
    global wit_context

    message.react('+1')

    wit_context = wit_client.run_actions(
                    random_word(10), 
                    message.body['text'], 
                    wit_context)
