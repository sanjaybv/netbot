#!/usr/bin/python

import sys
import logging
import logging.config

from slackbot import settings
from slackbot.bot import Bot

import wit_actions

def main():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool')\
            .setLevel(logging.WARNING)

    bot = Bot()

    @wit_actions.register
    def send(message):
        if bot._client:
            bot._client.send_message(channel='random', message=message)

    bot.run()

if __name__ == '__main__':
    main()
