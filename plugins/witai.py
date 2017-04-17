from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re

@respond_to('(.*)')
def wit(message, text):
    message.react('+1')
    message.reply('Hi!')
    message.reply('You said: ' + text)
