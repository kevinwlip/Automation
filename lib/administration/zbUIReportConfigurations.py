from ui.administration.zbUIAdministration import Administration
from ui.zbUIShared import checkFactory, clickAndVerifyColumns, verifyTableEntries
from locator.administration import AdministrationLoc


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportConfig(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Report Configuration Page...')
        super(ReportConfig, self).__init__(**kwargs)

    def check_report_config_history(self):
        if not self._go_to_administration_page_by("Report Configurations"):
            logger.error('Unable to reach the Report Configuration Page')
            return False

        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=AdministrationLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="Report Configurations")\
                     .add_to_checklist(css=AdministrationLoc.CSS_REPORT_TABLE_TITLE,
                                       element_name="Table Title",
                                       text="Report Configs",
                                       timeout=10)\
                     .add_to_checklist(css=AdministrationLoc.CSS_REPORT_TABLE_SEARCH,
                                       element_name="Search Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_REPORT_TABLE_VIEW_COLUMN,
                                       element_name="View Column Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_REPORT_TABLE_ADD,
                                       element_name="Add Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_REPORT_TABLE_BELOW_TEXT,
                                       element_name="Text below table")\
                     .add_to_checklist(css=AdministrationLoc.CSS_REPORT_TABLE_PAGE_NAV,
                                       element_name="pages")
        if not check_factory.check_all():
            return False

        if not clickAndVerifyColumns(self.selenium, verify_list=AdministrationLoc.report_config_list):
            logger.error('Unable to click and verify all column headers')
            return False

        if not verifyTableEntries(self.selenium):
            logger.error('Rows in table are not matched!')
            return False

        logger.info('All Columns on the first page passed the check')
        return True


