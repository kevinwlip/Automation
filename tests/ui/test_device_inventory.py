#!/usr/bin/python
import sys
import os
import pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')
    
from ui.devices.zbUIDeviceInventory import DeviceInventory, BulkEdit
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(DeviceInventory)
    return browser["selenium"]

@pytest.fixture(scope="module")
def browserBulkEdit(browser_factory):
    browser = browser_factory(BulkEdit)
    return browser["selenium"]


class Test_DeviceInventory:

    # ========================================================================
    # Smoke Tests
    # ========================================================================

    # Checks if graphs, columns and cells of Devices Type Graph Visualization for page 1 is loaded
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C354632"])
    def test_DeviceTypes_Visualization(self, testid, browser):
        assert rerunIfFail(function=browser.checkDeviceTypes(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_InventoryEntries.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # check if the number of bars in traffic graph matches time of 1 Day
    @pytest.mark.skip #Element no longer exists
    @pytest.mark.smoke
    def test_TrafficSeries_OneDay(self, browser):
        assert rerunIfFail(function=browser.checkDeviceInventoryTimeSeries(time_series=['1 Day'], strict=False),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_TrafficSeries.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Checks all columns and cells of Inventory Table for page 1 are loaded.
    @pytest.mark.parametrize("testid", ["C355155"])
    @pytest.mark.smoke
    def test_InventoryEntries_FirstPage(self, testid, browser):
        assert rerunIfFail(function=browser.checkEntries(pageNumber=1),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_InventoryEntries.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Checks Device Inventory Downloading by spinning icon
    @pytest.mark.parametrize("testid", ["C355157"])
    @pytest.mark.smoke
    def test_DeviceInventoryExport(self, testid, browser):
        assert rerunIfFail(function=browser.checkInventoryExport(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DeviceInventoryExport.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Check if device name inside device inventory page is linked to device details
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C355159"])
    def test_DeviceLink(self, testid, browser):
        assert rerunIfFail(function=browser.checkDeviceLink(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_DeviceLink.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # ========================================================================
    # Regression Tests
    # ========================================================================
    @pytest.mark.parametrize("testid", ["C355160,C355162,C355161"])
    @pytest.mark.parametrize("time",
                             ['2 Hours', '1 Day', '1 Week', '1 Month', '1 Year', 'All to Date'])
    @pytest.mark.parametrize("to_be_filtered", ["sites", "devices", "monitored"])
    @pytest.mark.regression
    def test_global_filter(self, testid, browser, time, to_be_filtered):
        assert browser.check_global_filter(time_range=time, to_be_filtered=to_be_filtered)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C354818"])
    def test_device_types(self, testid, browser):
        assert rerunIfFail(function=browser.check_device_types_recursive(),
                           selenium=browser.selenium,
                           number=1,
                           delay=DELAY_SECONDS)

    # Filtered by Category and Profile, check if a list of filtered results is returned
    @pytest.mark.parametrize("testid", ["C355164"])
    @pytest.mark.bugs #AP-13915
    @pytest.mark.regression
    def test_local_filter(self, testid, browser):
        assert rerunIfFail(function=browser.check_local_filter(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Local_Filter.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C359383"])
    @pytest.mark.regression
    def test_local_search(self, testid, browser):
        assert rerunIfFail(function=browser.check_local_search(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Local_Search.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C355156"])
    def test_inventory_entries_all_pages(self, testid, browser):
        assert rerunIfFail(function=browser.checkEntries(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_InventoryEntries.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C359384"])
    @pytest.mark.regression
    def test_sort(self, testid, browser):
        assert rerunIfFail(function=browser.checkSort(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_Sort.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
        assert rerunIfFail(function=browser.check_view_columns_reset(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_view_columns_reset.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C359385"])
    @pytest.mark.regression
    def test_create_policy_from_device_inventory(self, testid, browser):
        assert rerunIfFail(function=browser.check_create_policy_from_tooltip(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_create_policy_from_device_inventory.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    #@pytest.mark.regression   temporarily comment this case because of AP-14250
    @pytest.mark.parametrize("testid", ["C355158"])
    # @pytest.mark.skipif("kaiyihuang" not in getHostname() and "zbat003" not in getHostname(), reason="Not in zbat003")
    def test_DownloadInventory(self, testid, browser):
        assert rerunIfFail(function=browser.checkDownload(),
                           selenium=browser.selenium,
                           number=1,
                           delay=DELAY_SECONDS)

    def test_TrafficSeries_FullRange(self, browser):
        assert rerunIfFail(function=browser.checkDeviceInventoryTimeSeries(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_TrafficSeries.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C359386"])
    def test_SelectedDeviceInventoryExport(self, testid, browser):
        assert rerunIfFail(function=browser.checkInventoryExport(True),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_SelectedDeviceInventoryExport.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

@pytest.mark.bugs
class Test_BulkEdit:
    #First test case - Open menu, make edits check edits
    def test_BulkEditMenuDefault(self, browserBulkEdit):
        assert rerunIfFail(function=browserBulkEdit.checkDefault(),
                           selenium=browserBulkEdit.selenium,
                           number=NUMBER_RETRIES,
                           testname=zbathome+'artifacts/test_BulkEditMenuDefault.png',
                           screenshot=SCREENSHOT_ON_FAIL,
                           delay=DELAY_SECONDS)

    def test_BulkEditMenuTable(self, browserBulkEdit):
        assert rerunIfFail(function=browserBulkEdit.checkTable(),
                           selenium=browserBulkEdit.selenium,
                           number=NUMBER_RETRIES,
                           testname=zbathome+'artifacts/test_BulkEditMenuTable.png',
                           screenshot=SCREENSHOT_ON_FAIL, delay=DELAY_SECONDS)

    @pytest.mark.slowtest
    def test_BulkEditChange(self, browserBulkEdit):
        assert rerunIfFail(function=browserBulkEdit.checkBulkEditChange(),
                           selenium=browserBulkEdit.selenium,
                           number=NUMBER_RETRIES,
                           testname=zbathome+'artifacts/test_BulkEditChange.png',
                           screenshot=SCREENSHOT_ON_FAIL, delay=DELAY_SECONDS)
