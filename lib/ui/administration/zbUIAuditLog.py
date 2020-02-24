from ui.administration.zbUIAdministration import Administration
from ui.zbUIShared import *
from ui.zbUISharedTable import click_and_verify_columns, verify_table_entries
from locator.navigator import UISharedLoc
from locator.profiles import ProfileLoc
from common.zbSelenium import get_downloaded_files, get_file_content
from locator.administration import AdministrationLoc
import re
from io import StringIO
import csv
import logging
import base64
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditLog(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Audit Log Page...')
        super(AuditLog, self).__init__(**kwargs)


    def reg_audit_log(self):
        izzet = True
        ls = ["2 Hours", "1 Day", "1 Week", "1 Month", "1 Year", "All to Date"]
        if not self._go_to_administration_page_by("Audit Logs"):
            logger.error('Unable to reach the Audit Log Page')
            return False
        lastNum = -1
        
        for l in ls:
            self.selenium.click(selector=AdministrationLoc.CSS_DATE_DROPDOWN)
            keld = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_DATE_DROPDOWN_OPTS)
            time.sleep(1)
            if not keld:
                self.selenium.click(selector=AdministrationLoc.CSS_DATE_DROPDOWN)
                keld = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_DATE_DROPDOWN_OPTS)
            for k in keld:
                if l in k.text:
                    k.click()
                    break
            waitLoadProgressDone(self.selenium)
            currNum = self.selenium.findSingleCSS(selector = AdministrationLoc.CSS_AUDIT_LOG_TITLE).text
            print(currNum)
            currNum = int(re.findall(r"\d+", currNum)[0])
            if currNum < lastNum:
                logger.critical("{} in selector has out of order looking numbers".format(l))
                izzet = False
        
        #Prime the sample
        self.selenium.click(selector=AdministrationLoc.CSS_DATE_DROPDOWN)
        keld = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_DATE_DROPDOWN_OPTS)
        time.sleep(1)
        if not keld:
            self.selenium.click(selector=AdministrationLoc.CSS_DATE_DROPDOWN)
            keld = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_DATE_DROPDOWN_OPTS)
        for k in keld:
            if "1 Day" in k.text:
                k.click()
                break
        entrees = []
        tCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_TIME_1)
        if not tCol:
            tCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_TIME_1)
        aCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_EVT_1)
        if not aCol:
            aCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_EVT_1)
        uCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_USERNAME_1)
        if not uCol:
            uCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_USERNAME_1)
        dCol = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_DESCRIPTION_1)
        if not dCol:
            self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_COLUMN_DESCRIPTION_1)
        mapy = list(zip(tCol,aCol,uCol,dCol))
        for x in mapy[1:]:
            entrees.append( (x[0].text,x[1].text,x[2].text,x[3].text) )
        print(entrees)

        self.selenium.click(selector=AdministrationLoc.CSS_AUDIT_LOG_DOWNLOADER)

        filey = WebDriverWait(self.selenium.driver, 30, 1).until(get_downloaded_files)
        print (filey)
        if len(filey) == 0:
            logger.info("Error: File not Downloaded")
            return False
        linx = get_file_content(self.selenium.driver,filey[-1])
        trutext = linx.split(",")[-1]
        trutext = base64.standard_b64decode(trutext)
        trutext = trutext.decode("utf-8")

        
        f = StringIO(trutext)
        reader = csv.reader(f, delimiter=',')
        #for row in reader:
            #print('\t'.join(row))

        memes = list(reader)
        for oko,food in enumerate(entrees):
            if(food[1] != memes[oko+1][1]):
                logger.critical("CSV download event match failed with entry number {}".format(oko))
                izzet = False
                print(food[1])
                print(memes[oko+1][1])
            if(food[2] != memes[oko+1][3]):
                logger.critical("CSV download username match failed with entry number {}".format(oko))
            if(food[3] != memes[oko+1][4]):
                logger.critical("CSV download description match failed with entry number {}".format(oko))


        

        return izzet

        #Check download


    def check_audit_log(self):
        if not self._go_to_administration_page_by("Audit Logs"):
            logger.error('Unable to reach the Audit Log Page')
            return False
        logger.info('Checking the inventory of the audit logs...')
        inventory_card = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_PROFILE_TABLE, waittype='visibility')
        if not inventory_card:
            logger.error('Audit Inventory is not found')
            return False

        table_title = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_TABLE_NAME, waittype='visibility')
        if not table_title or 'Audit Logs' not in table_title.text:
            logger.error('Title of the Inventory is not Audit Logs!')
            return False

        if not click_and_verify_columns(self.selenium, verify_list=AdministrationLoc.audit_log_column_list):
            logger.info('Unable to click and verify all column headers')
            return False

        if not verify_table_entries(self.selenium):
            logger.error('Unable to verify all columns on the inventory page')
            return False

        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=AdministrationLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="Audit Logs")\
                     .add_to_checklist(css=AdministrationLoc.CSS_AUDIT_LOG_TITLE,
                                       element_name="Table Title",
                                       text="Audit Logs")\
                     .add_to_checklist(css=AdministrationLoc.CSS_AUDIT_LOG_VIEW_COLUMN_ICON,
                                       element_name="View Column Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_AUDIT_LOG_DOWNLOADER,
                                       element_name="download icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_TEXT_BELOW_AUDIT_LOG,
                                       element_name="Text below table")\
                     .add_to_checklist(css=AdministrationLoc.CSS_AUDIT_LOG_PAGENATION,
                                       element_name="pages")
        if not check_factory.check_all():
            return False
        logger.info('All Columns on the first page passed the check')
        return True


