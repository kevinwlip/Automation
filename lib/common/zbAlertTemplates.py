import time

policy_alert_default_dict = {
    "hostname":"Chromecast",
    "remoteIPAddr":"192.168.10.223",
    "evtType":"evt_ttsd",
    "appName":"mdns",
    "evtContent":{
      "access_list":[
        {
          "localIPAddr":"192.168.10.186"
        }
      ]
    },
    "ruleid":"5938994d3911ef0c007d92cf",
    "iotDevid":"18:65:90:cd:88:0d"
}

policy_alert_tag_default_dict = {
    "taggedBy": "PolicyAlert",
    "appName": "mdns",
    "alertType": "user policy",
    "values": [
        {
           "label":"IoT category",
           "value":"CT Scanner"
        },
        {
           "label":"IoT profile",
           "value":"DICOM-Imager-CT"
        },
        {
           "label":"remote URLs",
           "value":[  
              "b.scorecardresearch.com",
              "bats.video.yahoo.com",
              "mg.mail.yahoo.com",
              "geo.yahoo.com"
           ]
        },
        {
           "label":"applications",
           "value":"http"
        },
        {
           "label":"time period (seconds)",
           "value":300
        },
        {
           "label":"similar devices",
           "value":[  
              "18:65:90:cd:88:0d",
              "44:85:00:7b:7d:66",
              "50:7b:9d:91:d0:ce"
           ]
        }
    ],
    "ruleid":"5938994d3911ef0c007d92cf",
    "description": "Automated zbat policy alert description at unix time {}".format(time.time() * 1000),
    "name": "Automated zbat policy alert name at unix time {}".format(time.time() * 1000),
    "status":"publish",
    "toURL":"192.168.10.223",
    "toPort":5353,
    "toip":"192.168.10.223",
    "proto":17,
    "fromip":"192.168.10.186",
}

threat_alert_default_list = {
  "remoteIPAddrList":[
    "10.30.0.28",
    "10.30.0.33",
    "10.30.7.112",
    "10.30.7.81",
    "10.30.7.229"
  ],
  "evtType":"evt_fex",
  "type":"tracker",
  "iotDevid":"18:65:90:cd:88:0d",
  "appNameList":[
    "ssh",
    "telnet",
    "http",
    "https"
  ],
  "ttBytes":1284727,
  "portList":["443","22","23","80","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50","51","52","53","54","55","56","57","58","59","60","61","62","63","64","65","66","67","68","69","70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","92","93","94","95","96","97","98","99","100","101","102","103","104","105","106","107","108","109"],
  "encryptedBytes":87143,
  "key":"KTKdJPQheZ2a_d_Dkgbv8r7kqKHQnoVbf4:5c:89:b9:f7:83",
  "timestamp":1497049323000,
  "accessCount":100,
  "portCount":113,
  "rxBytes":12513,
  "_date":"2016.08.19",
  "evtContent":{
    "access_list":[
      {
        "localIPAddr":"null"
      }
    ]
  },
  "deviceid":"f4:5c:89:b9:f7:83",
  "remoteIPCount":5,
  "unencryptedBytes":1197584,
  "txBytes":1242214,
  "interval":300,
  "fields":"tenant-device-isOutBound",
  "ruleid":"analytics-port-scan",
  "portSeq":112,
  "ts":1475257838000
}

threat_alert_tag_default_list = {
  "taggedBy":"PolicyAlert",
  "alertType":"anomalous behavior",
  "appName":"ssh, telnet, http, https",
  "values":[
    {
      "label":"portCount",
      "value":113
    },
    {
      "label":"portList",
      "value":["443","22","23","80","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50","51","52","53","54","55","56","57","58","59","60","61","62","63","64","65","66","67","68","69","70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","92","93","94","95","96","97","98","99","100","101","102","103","104","105","106","107","108","109"]
    }
  ],
  "name": "Automated zbat threat alert name at unix time {}".format(time.time() * 1000),
  "fromip":"192.168.3.5",
  "description": "Automated zbat threat alert description at unix time {}".format(time.time() * 1000),
  "ruleid":"analytics-port-scan",
  "status":"publish",
  "id" : "zbatTh",
  "anomalyMap" : {
      "payload" : 3
    }
}
