#!/usr/bin/python
import sys
import os
import pytest
import pdb, time

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from common.zbConfig import defaultEnv
from ui.needle.zbUINeedle import Needle, ZBatNeedle, Needle_V2
from ui.needle.zbUINeedleGE import Needle_GE_Login, Needle_GE

defaultConfig = defaultEnv()
# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    config = {}
    return browser_factory(Needle, config)

@pytest.fixture(scope="module")
def browser_V2(browser_factory):
    config = {}
    return browser_factory(Needle_V2, config)

@pytest.fixture(scope="module")
def browser_GE_Login(browser_factory):
    config = {}
    return browser_factory(Needle_GE_Login, config)

@pytest.fixture(scope="module")
def browser_GE(browser_factory):
    config = {}
    return browser_factory(Needle_GE, config)

class Test_GE_Baseline:
    def test_sanity_login_baseline(self,browser_GE_Login,threshold=0.10):
        selenium = browser_GE_Login["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_login_page(needles, True, threshold) == True
    def test_sanity_dashboard_baseline(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_executive_dashboard(needles, True, threshold) == True
    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["ge_mssp"], reason="No Inventory on MSSP")
    def test_sanity_dev_inv_baseline(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_device_inv(needles, True, threshold) == True
    def test_sanity_alerts_baseline(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_alert_page(needles, True, threshold) == True
    def test_sanity_vulnerabilities_baseline(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_vulnerabilities(needles, True, threshold) == True
    def test_sanity_sidebar_baseline(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_sidebar(needles, True, threshold) == True
    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["ge_mssp"], reason="MSSP only")
    def test_sanity_customer_baseline(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_mssp_customer(needles, True, threshold) == True


class Test_GE:
    def test_sanity_login(self,browser_GE_Login,threshold=0.10):
        selenium = browser_GE_Login["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_login_page(needles, False, threshold) == True
    def test_sanity_dashboard(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_executive_dashboard(needles, False, threshold) == True
    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["ge_mssp"], reason="No Inventroy on MSSP")
    def test_sanity_dev_inv(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_device_inv(needles, False, threshold) == True
    def test_sanity_alerts(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_alert_page(needles, False, threshold) == True
    def test_sanity_vulnerabilities(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_vulnerabilities(needles, False, threshold) == True
    def test_sanity_sidebar(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_sidebar(needles, False, threshold) == True
    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["ge_mssp"], reason="MSSP only")
    def test_sanity_customer(self,browser_GE,threshold=0.10):
        selenium = browser_GE["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_mssp_customer(needles, False, threshold) == True


@pytest.mark.needle
class Test_Needle:

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_dashboard(self,browser,threshold=0.10):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_dashboard_elements(needles, False, threshold) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_device_detail(self,browser,threshold=0.10):
        #browser_s = browser_factory_s(Needle, {})
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_device_detail_elements(needles, False, threshold) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_alert_detail(self,browser, threshold=0.10):
        #browser_s = browser_factory_s(Needle, {})
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_alert_detail_elements(needles, False, threshold) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_sidebar(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_sidebar_elements(needles, False) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_vuln(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_vulnerability_elements(needles, False) == True


class Test_Needle_V2:
    def test_executive_dashboard(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_executive_dashboard(needles, False, threshold) == True

    def test_security_dashboard(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_security_dashboard(needles,False,threshold) == True

    def test_operational_dashboard(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_operational_dashboard(needles, False, threshold) == True

    def test_sidebar(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_sidebar(needles, False, threshold) == True
    def test_devices(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_devices(needles, False, threshold) == True
    def test_alerts(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_alerts(needles, False, threshold) == True
    def test_integrations(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_integrations(needles, False, threshold) == True
    def test_administration(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_administration(needles, False, threshold) == True
    #def test_vuln(self,browser_V2,threshold=0.10):
    #def test_reports(self,browser_V2,threshold=0.10):
    #def test_servers(self,browser_V2,threshold=0.10):
    #def test_protocols(self,browser_V2,threshold=0.10):
    #def test_applications(self,browser_V2,threshold=0.10):
    #def test_networks(self,browser_V2,threshold=0.10):
    #def test_profiles(self,browser_V2,threshold=0.10):
    #def test_policies(self,browser_V2,threshold=0.10):
    #def test_integrations(self,browser_V2,threshold=0.10):
    #def test_administration(self,browser_V2,threshold=0.10):

class Test_Needle_V2_Baseline:

    def test_executive_dashboard_baseline(self,browser_V2,threshold=0.10):
        selenium =browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_executive_dashboard(needles, True, threshold) == True

    def test_security_dashboard_baseline(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_security_dashboard(needles, True, threshold) == True

    def test_operational_dashboard_baseline(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_operational_dashboard(needles, True, threshold) == True

    def test_sidebar_baseline(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_sidebar(needles, True, threshold) == True
    def test_devices(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_devices(needles, True, threshold) == True
    def test_alerts(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_alerts(needles, True, threshold) == True
    def test_integrations(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_integrations(needles, True, threshold) == True
    def test_administration(self,browser_V2,threshold=0.10):
        selenium = browser_V2["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_administration(needles, True, threshold) == True
        #Look for test name in zbUINeelde
        #Run it with parameters





@pytest.mark.needle #Just so bamboo would skip this
class Test_Needle_Baseline:

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_vuln_baseline(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_vulnerability_elements(needles, True) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_sidebar_baseline(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_sidebar_elements(needles, True) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_dashboard_baseline(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_dashboard_elements(needles, True) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_device_detail_baseline(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_device_detail_elements(needles, True) == True

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Needle should only run on testing")
    def test_sanity_alert_detail_baseline(self,browser):
        selenium = browser["selenium"]
        needles = ZBatNeedle(selenium.selenium.driver)
        assert selenium.test_alert_detail_elements(needles, True) == True

