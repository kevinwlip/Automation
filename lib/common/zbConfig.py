#!/usr/bin/python

import sys, os, logging, pdb

# Global variables
NUMBER_RETRIES = 0
DELAY_SECONDS = 5
SCREENSHOT_ON_FAIL = True

# setting up default logging
log = logging.getLogger('')

devices = {"Rebeccas-MBP": {"deviceid": "f4:5c:89:94:5f:d1"}}


def defaultEnv():
    # setting some global parameter based on test environment
    try:
        env = os.environ['NODE_ENV']
        o365_email = os.environ['ZBAT_O365_EMAIL_ACCOUNT']
        o365_pwd = os.environ['ZBAT_O365_EMAIL_PWD']
        splunk_username = os.environ['ZBAT_SPLUNK_UNAME']
        splunk_pwd = os.environ['ZBAT_SPLUNK_PWD']
        # PANFW credentials
        panfw_username = os.environ['ZBAT_PANFW_UNAME']
        panfw_pwd = os.environ['ZBAT_PANFW_PWD']
        # CONNECTIV credentials
        connectiv_uname = os.environ['ZBAT_CONNECTIV_UNAME']
        connectiv_pwd = os.environ['ZBAT_CONNECTIV_PWD']
        connectiv_client_id = os.environ['ZBAT_CONNECTIV_CLIENT_ID']
        connectiv_client_secret = os.environ['ZBAT_CONNECTIV_CLIENT_SECRET']
        # NUVOLO credentials
        nuvolo_uname = os.environ['ZBAT_NUVOLO_UNAME']
        nuvolo_pwd = os.environ['ZBAT_NUVOLO_PWD']
        # SERVICENOW credentials
        servicenow_uname = os.environ['ZBAT_SERVICENOW_UNAME']
        servicenow_pwd = os.environ['ZBAT_SERVICENOW_PWD']
        # CISCO ISE credentials
        ise_uname = os.environ['ZBAT_CISCO_ISE_UNAME']
        ise_pwd = os.environ['ZBAT_CISCO_ISE_PWD']
        # ForeScout credentials
        forescout_uname = os.environ['ZBAT_FORESCOUT_UNAME'] #grab from .bash_profile
        forescout_pwd = os.environ['ZBAT_FORESCOUT_PWD']
        # traffic generator
        tg_uname = os.environ['ZBAT_TG_UNAME']
        tg_pwd = os.environ['ZBAT_TG_PWD']
        # OpenVAS
        openvasUserName = os.environ['OPENVAS_UNAME']
        openvasPassword = os.environ['OPENVAS_PWORD']
        # Inspector credentials
        insp_uname = os.environ['ZBAT_INSPECTOR_UNAME']
        insp_pwd = os.environ['ZBAT_INSPECTOR_PWD']
        # Phantom
        phantom_uname = os.environ['PHANTOM_UNAME']
        phantom_password = os.environ['PHANTOM_PASSWORD']
        # Cisco Prime
        cisco_prime_uname = os.environ['CISCO_PRIME_UNAME']
        cisco_prime_password = os.environ['CISCO_PRIME_PASSWORD']

    except:
        print ('Test cannot run.  Please set NODE_ENV to testing|staging|production.')
        print ('Test cannot run.  Please set ZBAT_<PROD|TESTING>_UNAME.')
        print ('Test cannot run.  Please set ZBAT_<PROD|TESTING>_PWD.')
        print ('Test cannot run.  Please set ZBAT_O365_EMAIL_ACCOUNT.')
        print ('Test cannot run.  Please set ZBAT_O365_EMAIL_PWD.')
        print ('Test cannot run.  Please set ZBAT_SPLUNK_UNAME.')
        print ('Test cannot run.  Please set ZBAT_SPLUNK_PWD.')
        print ('Test cannot run.  Please set ZBAT_PANFW_UNAME.')
        print ('Test cannot run.  Please set ZBAT_PANFW_PWD.')
        print ('Test cannot run.  Please set ZBAT_CONNECTIV_UNAME.')
        print ('Test cannot run.  Please set ZBAT_CONNECTIV_PWD.')
        print ('Test cannot run.  Please set ZBAT_CONNECTIV_CLIENT_ID.')
        print ('Test cannot run.  Please set ZBAT_CONNECTIV_CLIENT_SECRET.')
        print ('Test cannot run.  Please set ZBAT_NUVOLO_UNAME.')
        print ('Test cannot run.  Please set ZBAT_NUVOLO_PWD.')
        print ('Test cannot run.  Please set ZBAT_SERVICENOW_UNAME.')
        print ('Test cannot run.  Please set ZBAT_SERVICENOW_PWD.')
        print ('Test cannot run.  Please set ZBAT_CISCO_ISE_UNAME.')
        print ('Test cannot run.  Please set ZBAT_CISCO_ISE_PWD.')
        print ('Test cannot run.  Please set ZBAT_FORESCOUT_UNAME.')
        print ('Test cannot run.  Please set ZBAT_FORESCOUT_PWD.')
        print ('Test cannot run.  Please set ZBAT_TG_UNAME.')
        print ('Test cannot run.  Please set ZBAT_TG_PWD.')
        print ('Test cannot run.  Please set ZBAT_REDIS_PWD.')
        print ('Test cannot run.  Please set OPENVAS_UNAME.')
        print ('Test cannot run.  Please set OPENVAS_PWORD.')
        print ('Test cannot run.  Please set ZBAT_INSPECTOR_UNAME')
        print ('Test cannot run.  Please set ZBAT_INSPECTOR_PWD')
        print ('Test cannot run.  Please set PHANTOM_UNAME')
        print ('Test cannot run.  Please set PHANTOM_PASSWORD')
        print ('Test cannot run.  Please set CISCO_PRIME_UNAME')
        print ('Test cannot run.  Please set CISCO_PRIME_PASSWORD')
        sys.exit()

    if 'dev0' in env and 'cloud' in env:
        configDict = {
            "siteTest": env,
            "siteCompare": 'testing.zingbox.com',
            "tenantid": "testing-soho",
            "uiportal": 'http://'+env+'/login?tenantid=testing-soho',
            "socportal": 'http://'+env+'/login?tenantid=testing-soho',
            "username": os.environ['ZBAT_TESTING_UNAME'],
            "password": os.environ['ZBAT_TESTING_PWD'],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD_TESTING"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "ostinatoDrone": "192.168.20.67",
            "trafficGenPort1": "eth1",
            "inspector": "testing-soho-vm-001",
            "customer_onboard_reseller_name": 'zbatreseller',
            "customers_admin_panel_uiportal": 'https://testing-admin.zingbox.com/login',
            "elasticsearch": [{"host": "testing-es001.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "testing-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['testing']:
        configDict = {
            "siteTest": "testing.zingbox.com",
            "siteCompare": "testing.zingbox.com", # using same testing-soho for comparison since not interest in comparison and just want to see if api call works.
            "tenantid": "qa-automation",
            "uiportal": "https://testing.zingbox.com/login?tenantid=qa-automation",
            "socportal": "https://testing.zingbox.com/login?tenantid=qa-automation",
            "username": os.environ['ZBAT_TESTING_UNAME'],
            "password": os.environ['ZBAT_TESTING_PWD'],
            "username_2fa_owner": os.environ['ZBAT_TESTING_2FA_UNAME'],
            "password_2fa_owner": os.environ['ZBAT_TESTING_2FA_PWD'],
            "username_2fa_user": os.environ['ZBAT_TESTING_2FA_USER_UNAME'],
            "password_2fa_user": os.environ['ZBAT_TESTING_2FA_USER_PWD'],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD_TESTING"],
            "superinv_username": "superinv@spam4.me",
            "superinv_password": "Zb@t4ever",
            "ostinatoDrone": "192.168.20.67",
            "inspector": "testing-soho-vm-001",
            "customer_onboard_reseller_name": 'zbatreseller',
            "customers_admin_panel_uiportal": 'https://testing-admin.zingbox.com/login',
            "elasticsearch": [{"host": "testing-es001.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "testing-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['staging']:
        configDict = {
            "siteTest": "staging.zingbox.com",
            "siteCompare": "production-candidate.zingbox.com",
            "tenantid": "soho",
            "uiportal": "https://staging.zingbox.com/login",
            "socportal": "https://staging.zingbox.com/login",
            "username": os.environ['ZBAT_STAGING_UNAME'],
            "password": os.environ['ZBAT_STAGING_PWD'],
            "passwordSuper": os.environ["ZBAT_STAGING_PWD"],
            "ostinatoDrone": "192.168.20.67",
            "trafficGenPort1": "eth1",
            "inspector": "inspector-zingbox123-vm",
            "customer_onboard_reseller_name": 'zbatreseller',
            "customers_admin_panel_uiportal": 'https://testing-admin.zingbox.com/login',
            "elasticsearch": [{"host": "staging-es001.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "staging-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['production-candidate']:
        configDict = {
            "siteTest": "production-candidate.zingbox.com",
            "siteCompare": "production-candidate.zingbox.com",
            "tenantid": "soho",
            "uiportal": "https://production-candidate.zingbox.com/login?tenantid=soho",
            "socportal": "https://production-candidate.zingbox.com/login?tenantid=soho",
            "username": os.environ['ZBAT_PROD_UNAME'],
            "password": os.environ['ZBAT_PROD_PWD'],
            "username_2fa_owner": os.environ['ZBAT_PRODUCTION_CANDIDATE_2FA_OWNER_UNAME'],
            "password_2fa_owner": os.environ['ZBAT_PRODUCTION_CANDIDATE_2FA_OWNER_PWD'],
            "username_2fa_user": os.environ['ZBAT_PRODUCTION_CANDIDATE_2FA_USER_UNAME'],
            "password_2fa_user": os.environ['ZBAT_PRODUCTION_CANDIDATE_2FA_USER_PWD'],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "trafficGenPort1": "eth1",
            "inspector": "prod-soho-vm001",
            "elasticsearch": [{"host": "es003.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "production-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['production']:
        configDict = {
            "siteTest": "soho.zingbox.com",
            "siteCompare": "soho.zingbox.com",
            "tenantid": "soho",
            "uiportal": "https://soho.zingbox.com/",
            "socportal": "https://soho.zingbox.com/",
            "username": os.environ['ZBAT_PROD_UNAME'],
            "password": os.environ['ZBAT_PROD_PWD'],
            "username_2fa_owner": os.environ['ZBAT_PRODUCTION_2FA_OWNER_UNAME'],
            "password_2fa_owner": os.environ['ZBAT_PRODUCTION_2FA_OWNER_PWD'],
            "username_2fa_user": os.environ['ZBAT_PRODUCTION_2FA_USER_UNAME'],
            "password_2fa_user": os.environ['ZBAT_PRODUCTION_2FA_USER_PWD'],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "trafficGenPort1": "eth1",
            "inspector": "prod-soho-vm001",
            "elasticsearch": [{"host": "es003.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "production-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['ge_production']:
        configDict = {
            "siteTest": "soho.zingbox.com",
            "siteCompare": "soho.zingbox.com",
            "tenantid": "soho",
            "uiportal": "https://soho.zingbox.com/",
            "socportal": "https://soho.zingbox.com/",
            "username": os.environ['ZBAT_PROD_UNAME'],
            "password": os.environ['ZBAT_PROD_PWD'],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "trafficGenPort1": "eth1",
            "inspector": "prod-soho-vm001",
            "elasticsearch": [{"host": "es003.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "production-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['qa_automation']:
        configDict = {
            "siteTest": "testing.zingbox.com",
            "siteCompare": "testing.zingbox.com",
            "tenantid": "qa-automation",
            "uiportal": "https://testing.zingbox.com/login?tenantid=qa-automation",
            "socportal": "https://testing.zingbox.com/login?tenantid=qa-automation",
            "username": "qa@zingbox.com",
            "password": "Zb@t4ever",
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "trafficGenPort1": "eth1",
            "inspector": "zbat_inspector1",
            "elasticsearch": [{"host": "es003.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "production-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['ge_mssp']:
        configDict = {
            "siteTest": "dev007.cloud.zingbox.com",
            "siteCompare": "dev007.cloud.zingbox.com",
            "tenantid": "testing-ge",
            "uiportal": "http://dev007.cloud.zingbox.com/login?tenantid=testing-ge",
            "socportal": "http://dev007.cloud.zingbox.com/login?tenantid=testing-ge",
            "username": "analystmgr@testing-ge.com",
            "password": "4Gg9YW6u!",
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "trafficGenPort1": "eth1",
            "inspector": "prod-soho-vm001",
            "elasticsearch": [{"host": "es003.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "production-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['ge_guardian']:
        configDict = {
            "siteTest": "production-candidate.zingbox.com",
            "siteCompare": "production-candidate.zingbox.com",
            "tenantid": "soho",
            "uiportal": "http://production-candidate.zingbox.com/login?tenantid=soho",
            "socportal": "http://production-candidate.zingbox.com/login?tenantid=soho",
            "username": "ge_guardian@soho.com",
            "password": os.environ["ZBAT_PROD_PWD"],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "timestrict": False,
            "comparestrict": True,
            "datastrict": True,
            "compareNumberThreshold": 5,
            "trafficGenPort1": "eth1",
            "inspector": "prod-soho-vm001",
            "elasticsearch": [{"host": "es003.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "production-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    elif env in ['devy']:
        configDict = {
            "siteTest": "dev009.cloud.zingbox.com",
            "siteCompare": "dev009.cloud.zingbox.com",
            "tenantid": "qa-automation",
            "uiportal": "https://dev009.cloud.zingbox.com/login?tenantid=qa-automation",
            "socportal": "https://dev009.cloud.zingbox.com/login?tenantid=qa-automation",
            "username": os.environ['ZBAT_TESTING_UNAME'],
            "password": os.environ['ZBAT_TESTING_PWD'],
            "username_2fa_owner": os.environ['ZBAT_TESTING_2FA_UNAME'],
            "password_2fa_owner": os.environ['ZBAT_TESTING_2FA_PWD'],
            "username_2fa_user": os.environ['ZBAT_TESTING_2FA_USER_UNAME'],
            "password_2fa_user": os.environ['ZBAT_TESTING_2FA_USER_PWD'],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD_TESTING"],
            "ostinatoDrone": "192.168.20.67",
            "inspector": "testing-soho-vm-001",
            "customer_onboard_reseller_name": 'zbatreseller',
            "customers_admin_panel_uiportal": 'https://testing-admin.zingbox.com/login',
            "elasticsearch": [{"host": "testing-es001.cloud.zingbox.com", "port": 443, "use_ssl": True, "verify_certs": False, "url_prefix": "es"}],
            "redisHost": "testing-ec-redis.cloud.zingbox.com",
            "splunk_port": 8089,
            "panfw_host": "192.168.10.23:443",
            "trafficGenPort": 20022,
            "openvasPort" : "9400"
        }
    else:
        print ("Test cannot run.  Please set NODE_ENV to testing|staging|production.")
        sys.exit()

    commonDict = {
            "zbat_home": os.environ["ZBAT_HOME"],
            "deviceid": "00:17:88:16:44:09",
            "device_id_risk": "20:25:64:7c:2c:12",
            "appid": "http",
            "uiportal": None,
            "socportal": None,
            "usernameSuper": os.environ["ZBAT_SUPER_UNAME"],
            "passwordSuper": os.environ["ZBAT_SUPER_PWD"],
            "remoteSeleniumServer": "selenium-linux001.cloud.zingbox.com:4444",
            "timestrict": False,
            "comparestrict": False,
            "datastrict": False,
            "compareNumberThreshold": 15,
            "splunk": "192.168.10.40",
            "splunk_ui_config_ip": "192.168.10.40",
            "splunk_username": splunk_username,
            "splunk_pwd": splunk_pwd,
            "aimsServer": "zingboxdemo.aimsasp.net:443",
            "aimsToken": "375A9601-0C94-401F-B6CE-CC1EBA267CA2",
            "panfw_username": panfw_username,
            "panfw_pwd": panfw_pwd,
            "sms_uiportal": "https://www.textnow.com/login",
            "sms_apiportal": "https://www.textnow.com/api/users",
            'ring_central_api': 'https://platform.devtest.ringcentral.com/restapi/',
            "o365_email": o365_email,
            "o365_pwd": o365_pwd,
            "phone": "4086147631",
            "connectiv_uname": connectiv_uname,
            "connectiv_pwd": connectiv_pwd,
            "connectiv_client_id": connectiv_client_id,
            "connectiv_client_secret": connectiv_client_secret,
            "connectiv_client_url": "https://ven01658.service-now.com",
            "nuvolo_uname": nuvolo_uname,
            "nuvolo_pwd": nuvolo_pwd,
            "nuvolo_key": "02c1fba90fb4c300429585ace1050e40",
            "nuvolo_url": "https://ven02432.service-now.com",
            "servicenow_url": "https://dev11967.service-now.com/",
            "servicenow_uname": servicenow_uname,
            "servicenow_pwd": servicenow_pwd,
            "servicenow_table": "u_medical_devices",
            "servicenow_category": "u_category",
            "servicenow_profile": "u_profile",
            "ise_host": "192.168.20.74",
            "ise_uname": ise_uname,
            "ise_pwd": ise_pwd,
            "ise_profile": "ZingboxProfile",
            "forescout_host": "192.168.20.72",
            "forescout_uname": forescout_uname,
            "forescout_pwd": forescout_pwd,
            "forescout_account": "user",
            "trafficGenHost": "192.168.20.67",
            "trafficGenUname": tg_uname,
            "trafficGenPwd": tg_pwd,
            "trafficGenPort1": "eth1",
            "trafficGenPort2": "eth1",
            "openvasIP" : "192.168.10.40",
            "openvasUserName" : openvasUserName,
            "openvasPassword" : openvasPassword,
            "phantom_uname": phantom_uname,
            "phantom_password": phantom_password,
            "phantom_host": "192.168.20.192",
            "cisco_prime_uname": cisco_prime_uname,
            "cisco_prime_password": cisco_prime_password,
            "cisco_prime_host": "192.168.20.75"
    }

    # return merge configuration with configDict overriding duplicate values in commonDict
    mergeDict = commonDict.copy()
    mergeDict.update(configDict)
    return mergeDict
