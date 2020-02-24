from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoliciesPage(object):
    CSS_POLICY_NAV = ".nav-item.ng-star-inserted[data-title='Policies']"
    CSS_POLICY_SELECTOR = ".policy-name.mat-cell .left-word"
    CSS_POLICY_ADD = ".clickable.add-circle"
    CSS_POLICIES_MAIN_CHECKS ={
    ".policy-name.mat-cell .left-word",
    ".mat-card.policy-list .header-wrap",
    ".page-title-badget",
    ".cdk-column-status",
    ".cdk-column-severity",
    ".cdk-column-policy",
    ".cdk-column-select",
    ".cdk-column-edit",
    ".cdk-column-createdTime"
    }
    CSS_POLICIES_DETAIL_CHECKS = {
    ".page-title-badget",
    "[formcontrolname='severity']",
    "[formcontrolname='name']",
    ".mat-radio-label-content",
    "[formcontrolname='device']",
    "[formcontrolname='destination']",
    "[formcontrolname='application']",
    "[formcontrolname='sizeNumber']",
    "[formcontrolname='sizeUnit']",
    "[formcontrolname='durationNumber']",
    "[formcontrolname='durationUnit']",
    "form .working-day[category='Policy Configuration']",
    ".email-input-container"
    }