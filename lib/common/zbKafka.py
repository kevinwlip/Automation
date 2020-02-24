import os
import pdb
import time
import json
from datetime import datetime
from common import zbAlertFactory
from kafka import SimpleClient
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from kafka.protocol.offset import OffsetRequest, OffsetResetStrategy
from kafka.common import OffsetRequestPayload

SYSTEM_ALERT = 'system_alert'
POLICY_ALERT = 'policy_alert'
THREAT_ALERT = 'threat_alert'
supported_alert_types = [THREAT_ALERT, POLICY_ALERT]

ALERT_FILE_PATH = './alert'

def createKafka(topic):
    kwargs = {}
    kwargs['host'] = os.environ['ZBAT_KAFKA_BROKER']
    kwargs['topic'] = topic
    return zbKafka(**kwargs)

def checkTtsd(kafka, starts, stops, flows):
    print(("start offset: {}".format(starts)))
    print(("stop offset: {}".format(stops)))
    print ("target flows:")
    print (flows)

    print ("checking new messages in analytics_ttsd topic...")
    match = [False for _ in range(len(flows))]
    read_break = [False for _ in range(len(starts))]
    kafka.setOffset(starts)
    for msg in kafka.consumer:
        src = flows[0][0]
        data = json.loads(msg.value)
        try:
            for access in data['evtContent']['access_list']:
                try:
                    remote = access['remoteIPAddr']
                    local = access['localIPAddr']
                    if [local, remote] in flows:
                        idx = flows.index([local, remote])
                        if not match[idx]:
                            match[idx] = True
                            if all(m for m in match):
                                return True
                except:
                    pass
        except:
            pass
            
        # check if it's the end, if so, break
        if msg.offset >= stops[msg.partition]:
            read_break[msg.partition] = True
            if all(b for b in read_break):
                break
    
    print ("\nconnection not found in analytics_ttsd topic:")
    for i in range(len(match)):
        if match[i] == False:
            print((flows[i]))
    
    return False

def checkTagged(kafka, starts, stops, devIDs, alertname):
    print(("start offset: {}".format(starts)))
    print(("stop offset: {}".format(stops)))

    print ("checking new messages in tagged topic...")
    read_break = [False for _ in range(len(starts))]
    kafka.setOffset(starts)
    for msg in kafka.consumer:
        data = json.loads(msg.value)
        if 'iotDevid' in data and data['iotDevid'] in devIDs:
            for tag in data['tags']:
                if tag['name'] == alertname:
                    return True

        # check if it's the end, if so, break
        if msg.offset >= stops[msg.partition]:
            read_break[msg.partition] = True
            if all(b for b in read_break):
                break
    
    print(("\nalert not found in tagged topic: "+alertname))
    return False

class zbKafka():

    command_list = ['$KAFKA_PRODUCER', '-broker-list', 'testing-kafka1:9092', '--topic', 'tagged']

    def __init__(self, **kwargs):
        if 'host' in kwargs and 'topic' in kwargs:
            self.client = SimpleClient(kwargs['host'])
            self.topic = kwargs['topic']
            self.partitions = self.client.topic_partitions[self.topic]
            # consumer timeout after 1 minutes (60 seconds)
            self.consumer = KafkaConsumer(bootstrap_servers=kwargs['host'], consumer_timeout_ms=60000)

    def sendAlert(self, **kwars):
        if 'alert_type' not in kwars:
            print('No alert_type in kwars, please specify alert_type')
            return

        if kwars['alert_type'] not in supported_alert_types:
            print(('Unsupported alert type {0}, currently only support alert types {1}'.format(kwars['alert_type'], supported_alert_types)))
            return

        alert_payload = self._generateAlertPayload(**kwars)
        if bool(alert_payload) is False:
            print('Error in alert payload generation, payload is empty')
            return

        self._saveToFile(alert_payload)
        
        _command = self._joinCommand(alert_payload)
        print('\n\n\n')
        print(_command)
        print('\n\n\n')
        output = os.popen(_command).readlines()
        return output

    # get the last item in queue
    def getOffset(self):
        offset_requests = [OffsetRequestPayload(self.topic, p, -1, 1) for p in list(self.partitions.keys())]
        offset_responses = self.client.send_offset_request(offset_requests)
        last_offsets = []
        for r in offset_responses:
            last_offsets.append(r.offsets[0]-1)
        return last_offsets

    def setOffset(self, starts):
        partitions = list(self.partitions.keys())
        tps = [TopicPartition(self.topic, p) for p in partitions]
        self.consumer.assign(tps)
        for i in range(len(partitions)):
            self.consumer.seek(tps[i], starts[i])

    def _saveToFile(self, alert_payload):
        text_file = open(ALERT_FILE_PATH, "w")
        alert_payload = str(alert_payload)
        alert_payload = alert_payload.replace("'", '"')
        # REMINDER: This amends the payload to send boolean to js console, python give True, which is not recognised by js console.
        # The hack here is the genereate string "true", and then convert it to js boolean true before saving the payload.
        alert_payload = alert_payload.replace('"true"', 'true')
        text_file.write(str(alert_payload))
        text_file.close()

    def _generateAlertPayload(self, **kwars):
        payload = {}
        alert_type = kwars['alert_type']
        print(('Generating {0} payload'.format(alert_type)))

        if alert_type == SYSTEM_ALERT:
            payload = zbAlertFactory.create_system_alert(**kwars)
        elif alert_type == POLICY_ALERT:
            payload = zbAlertFactory.create_policy_alert(**kwars)
        elif alert_type == THREAT_ALERT:
            payload = zbAlertFactory.create_threat_alert(**kwars)
        return payload

    def _joinCommand(self, payload):
        _command_list = self.command_list[:]
        _command_list.append('<')
        _command_list.append(ALERT_FILE_PATH)
        return ' '.join(_command_list)

'''
# test
kwargs = {}
kwargs['host'] = os.environ['ZBAT_KAFKA_BROKER']
kwargs['topic'] = 'tagged'
kafka = zbKafka(**kwargs)
start = kafka.getOffset()
print (start)
time.sleep(60)

kafka = zbKafka(**kwargs)
kafka.consume(start=start)
'''