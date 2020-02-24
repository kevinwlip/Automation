import os
import sys
import requests

CHANNEL = '#zingbots'
USERNAME = 'zbat'
WEBHOOK = None
try:
    WEBHOOK = os.environ['ZBAT_SLACK_WEBHOOK_URL']
except:
    print('Slack webhook url not detected in ZBAT_SLACK_WEBHOOK_URL, please prepare you own webhook_url, username and channel during init.')

class zbSlack:
    def __init__(self, webhook_url=WEBHOOK, username=USERNAME, channel=CHANNEL):
        self.webhook_url = webhook_url
        self.username = username
        self.channel = channel

    def sendMsg(self, message='', linkedNames=0):
        if self.webhook_url is None:
            print('Webhook is not given, no message sent.')
        payload = {
            "channel": self.channel,
            "username": self.username,
            "text": message,
            "icon_emoji": ":robot_face:",
            "link_names" : linkedNames
        }
        try:
            requests.post(self.webhook_url, json=payload)
            print(('payload sent: {}'.format(payload)))
        except:
            print(('message not sent, please check your webhook url - {}.'.format(self.webhook_url)))

'''
slack = zbSlack(webhook_url=WEBHOOK, username=USERNAME, channel=CHANNEL)
slack.sendMsg('testing')
'''
