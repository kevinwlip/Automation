from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationSelectors:

    CSS_INTEGRATION_NAV = ".nav-item.ng-star-inserted[data-title='Integrations']"
    CSS_NAV_ALL = "li.ng-star-inserted"
    CSS_CLICK_TO_CHOOSE = '.nav-menu li a[href*="{}"]'
    CSS_INTEGRATION_NAV_ALL = "[href='/guardian/integrations/all?interval=oneday&stime=2019-08-21T23:55Z&etime=now&filter_monitored=yes']"
    CSS_INTEGRATION_MAIN_CARDS = "div.boxwrap ._md"
    CSS_MAIN_TITLE = ".page-title-badget"

class IntegrationAsset:
    asset_list = ["aims", "connectiv", "nuvolo"]
    CSS_ASSET_CARD = ".asset-management"

    CSS_ASSET_MANAGEMENT = ".asset-management"
    CSS_SELECTOR_AIMS_IMAGE = ".vendor-icon-container .vendor-icon-aims"
    CSS_SELECTOR_CONNECTIV_IMAGE = ".vendor-icon-connectiv"
    CSS_SELECTOR_NUVOLO_IMAGE = ".vendor-icon-nuvolo"
    CSS_SELECTOR_VENDOR_IMAGE = ".vendor-pic"
    CSS_SELECTOR_ASSET_IMAGE = ".vendor-images img"
    CSS_EDIT_PART = ".edit-part"
    CSS_ELEMENT_PROPERTY = ".confirm-page div .property-value.ng-binding"
    CSS_PROPERTY_TITLE = ".property-title"

    CSS_ASSET_CONFIGURATION = "zing-asset-management .vendor-images"
    CSS_ASSET_CONFIRM = ".config-detail .confirm-page"
    CSS_VENDOR_ICON = "img.vendor-icon-"
    CSS_VENDOR_CONFIRM = '[ng-src="static/images/asset-management/{}Icon.png"]'
    CSS_ASSET_AIMS_HOST = '#host'
    CSS_ASSET_AIMS_TOKEN = "#auth_token"
    CSS_CONNECTIV_UNAME = "#username"
    CSS_CONNECTIV_PWD = "#password"
    CSS_CONNECTIV_CLIENT_ID = '[name="client_id"]'
    CSS_CONNECTIV_CLIENT_SECRET = '[name="clientsecret"]'
    CSS_CONNECTIV_URL = '[name="desturl"]'
    CSS_NUVOLO_UNAME = '[id="username"]'
    CSS_NUVOLO_PWD = '[id="password"]'
    CSS_NUVOLO_SOURCE_KEY = '[name="source_key"]'
    CSS_NUVOLO_URL = '[name="desturl"]'

    CSS_EDIT_ASSET_DETAIL_TITLE = "fieldset .main-title"
    CSS_SELECTOR_SERVICENOW_IMAGE = "div.vendor-pic .service-now-icon"
    CSS_SERVICENOW_INFO = ".property-label-wrapper"
    CSS_ASSET_SAVE_BUTTON = '[type="submit"].md-primary'
    CSS_ASSET_CANCEL_BUTTON = '[action*="cancel"]'
    CSS_CONFIRM_TO_SAVE = 'md-dialog .confirm'

    CSS_DISABLE_ASSET_SWITCH = 'md-switch[aria-checked="true"]'
    CSS_SERVICENOW_EDIT = ".config-page .material-icons"
    CSS_SERVICENOW_URL = ".asset-management .md-input[placeholder=' Your ServiceNow URL']"
    CSS_SERVICENOW_USERNAME = ".asset-management .md-input[placeholder='Your ERS (External RESTful Services) Endpoint']"

    CSS_SERVICENOW_PWD = ".asset-management .md-input[placeholder='Your ERS Password']"
    CSS_SERVICENOW_TABLE = ".asset-management .md-input[placeholder='Your Table']"
    CSS_SERVICENOW_CATEGORY = ".asset-management .md-input[placeholder='Your Category']"
    CSS_SERVICENOW_PROFILE = ".asset-management .md-input[placeholder='Your Profile']"
    CSS_SERVICENOW_SAVE = ".save.md-primary"


class IntegrationNAC:
    CSS_ASSET_CARD = ".asset-management"
    CSS_EDIT_PART = ".md-scroll-disabled"
    check_words = [
    ["Cisco ISE Integration", "Host", "Forwarding Inspector"],
    ["Aruba ClearPass Integration", "Host", "Inspector ID"],
    ["ForeScout Integration", "Host", "Inspector ID"]
    ]
class IntegrationManagement:
    CSS_ASSET_CARD = ".asset-management"
    CSS_EDIT_PART = ".edit-part"
    check_words = [["Cisco Prime Integration","Host","Inspector ID"]]

class IntegrationSIEM:
    CSS_SIEM_DISABLED = "md-card-content .inactive.ng-valid.ng-pristine"
    CSS_EDIT_PART = "md-card-header .material-icons"
    CSS_SIEM_CARD = 'md-card[aria-hidden="false"]'
    CSS_SIEM_TITLE = '[aria-hidden="false"] md-title.main-title'
    CSS_INK_RIPPLE = ".md-container[md-ink-ripple-checkbox='']"
    CSS_INFO_ELEMENTS = "p.ng-binding"

class IntegrationFirewall:
    CSS_TITLE = ".firewall-integration .title"
    CSS_ADD_BUTTON = ".add-button"
    CSS_FIREWALL_CARD = "zing-firewall"
    CSS_CARD_PROVIDER = ".firewall-provider"
    checkwords = ["IP", "Port", "User Name", "Inspector ID", "Model"]

class IntegrationSOAR:
    CSS_ASSET_CARD = ".asset-management"
    CSS_EDIT_PART = ".edit-part"
    check_words = [["Phantom Integration","Host","Inspector ID"]]

class IntegrationMSS:
    CSS_CARD_TITLE = "[aria-hidden='false'] md-card-header .main-title"
    CSS_TOGGLE = ".md-thumb-container .md-thumb"
    CSS_EDIT_PART = "md-card-header .zing-hide-for-readonly"
    CSS_CARD = ".symantec-integration-wrap md-card"
    check_words = ["Discovered Devices", "Alerts", "Inspector:", "Deliver To:", "IP:", "Port:", "Protocol:"]

class IntegrationVulnScan:
    CSS_CARD_TITLE = "md-title"
    CSS_CARD = "._md.asset-management"
    CSS_EDIT_PART = ".edit-part"
    CSS_VENDOR_IMAGE = ".vendor-pic img"
    check_sets = [
    ["Qualys Integration", "Username", "QualysGuard"],
    ["Tenable Integration", "Product", "Access Key"],
    ["Rapid7 Integration", "Username", "Rapid7 URL", "Port","Inspector ID"]

    ]

class IntegrationWLAN:
    CSS_TITLE = ".firewall-integration .title"
    CSS_ADD_BUTTON = ".add-button"
    CSS_WLAN_CARD = "zing-wlan"
    CSS_CARD_PROVIDER = "img"
    CSS_CARD_TOGGLE = "md-switch"
    checkwords = ["Controller IP", "Inspector ID"]