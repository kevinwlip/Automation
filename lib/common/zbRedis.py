#!/usr/bin/python

import redis, pdb

def deleteSubduedAlert(REDIS_HOST, REDIS_PWD, REDIS_TESTING_TENANT, devID=None, alertID=None, keyword=None):
        r = Redis(REDIS_HOST, REDIS_PWD, REDIS_TESTING_TENANT)
        
        if devID is not None and alertID is not None:
            r.deleteEntryByKey(devID, alertID)
        else:
            r.deleteEntriesByKeyword(keyword, devID)

class Redis:
    def __init__(self, host, password, tenant=None):
        # timeout after 5 minutes
        if password:
            self.rd = redis.Redis(host=host, password=password, socket_timeout=300)
        else:
            self.rd = redis.Redis(host=host, socket_timeout=300)

        if tenant is not None:
            self.tenant = tenant

    def _findAllSubduedAlerts(self):
        allkeys = self.rd.keys('data:subdued_alert:*')
        return allkeys

    def deleteSubduedAlertsWithPattern(self, pattern):
        alerts = _findAllSubduedAlerts()
        for alert in alerts:
            match = re.search(pattern, alert)
            if match:
                self.rd.delete(alert)
                
    def _findAllIgnoredAlerts(self):
        allkeys = self.rd.keys('data:ignored_alert:*')
        return allkeys

    def deleteIgnoredAlertsWithPattern(self, pattern):
        alerts = _findAllIgnoredAlerts()
        for alert in alerts:
            match = re.search(pattern, alert)
            if match:
                self.rd.delete(alert)
                
    def deleteEntryByKey(self, devID, alertID):
        self.rd.delete("data:subdued_alert:"+self.tenant+devID+alertID)
        self.rd.delete("data:ignored_alert:"+self.tenant+devID+alertID)

    def deleteEntriesByKeyword(self, keyword, devID=None):
        alertkey = "data:subdued_alert:"+self.tenant
        if devID is not None:
            alertkey += devID
        
        for key in self.rd.keys(alertkey+"*"):
            if key.find(keyword) != -1:
                self.rd.delete(key)
                
        alertkey = "data:ignored_alert:"+self.tenant
        for key in self.rd.keys(alertkey+"*"):
            if key.find(keyword) != -1:
                self.rd.delete(key)
