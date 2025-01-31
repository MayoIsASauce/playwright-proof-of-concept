import re, os
from dotenv import load_dotenv
from playwright.sync_api import expect, Page
from pytest import fixture
from time import sleep

from utils.helper_methods import element_type, element_click, element_hover, element_type_d, is_loading
from utils.data_compare import DataComp

load_dotenv("IntegrationLogin.env") # the login credentials

DEFAULT_URL = "https://imgdev.mcdaltametrics.com/ers/login/MCD_AC_SBOX.html" # url to navigate to
is_worker_syncd = False

@fixture(scope="function", autouse=True) # runs before and after each test is called
def before_and_after(page: Page):
    page.goto(DEFAULT_URL) # navigate to the url

    yield page # allow test to execute

    pass # clean up

def test_alta(page: Page):
    global is_worker_syncd
    # NAVIGATION -=-=-=-=-=-=-=-=-=-=-=-
    element_type(page, "input[name='userName']", os.getenv('LOGIN_USER')) # fill username
    element_type(page, "input[name='password']", os.getenv('LOGIN_PASS')) # fill password
    element_click(page, "input[value='Login']") # submit

    page.wait_for_selector("h3") # wait for store selection

    # I attempted to bypass having to click here but alta did not like me
    element_click(page, 'a[class="selectBox selectBox-dropdown"]') # open the dropdown
    element_click(page, "a[rel='0']") # select the store

    element_click(page, 'input[value="GO "]') # go on

    page.wait_for_selector("#loading_layer") # wait for loading screen

    while is_loading(page): # timeout while the page loads
        sleep(0.5)

    # navigate through the homepage to the employee page ---
    element_hover(page, "a[class='dropdown-toggle js-activated']")
    element_hover(page, "#page-container > div.navbar.navbar-inverse.navbar-fixed-top > div > div > div > ul > li:nth-child(1) > ul > li:nth-child(1) > a")
    element_click(page, "#page-container > div.navbar.navbar-inverse.navbar-fixed-top > div > div > div > ul > li:nth-child(1) > ul > li:nth-child(1) > ul > li:nth-child(2) > a")
    # ---

    # wait for employee page
    page.wait_for_selector("#ribbon_cont > ul > li > a > div > div.ribbon-data > span")
    sleep(1.5) # short timeout for loading screen to appear
    while is_loading(page): # timeout while the page loads
        sleep(0.5)

    SEARCH = "Harris" # this pulls the employees with this name
    # type_d is a slow type so the javascript can update the search
    element_type_d(page, "#NEW_EMP_DETAIL_tbl_filter > label > input[type=text]", SEARCH, delay=0.1)

    # END NAVIGATION -=-=-=-=-=-=-=-=-=-

    # locate the employee table
    table = page.locator("#NEW_EMP_DETAIL_tbl > tbody").locator("tr").all()
    len(table) > 0 # tests if there is any employees

    for row in table:
        link = row.locator('a') # find the geid
        print(row.locator('a').inner_text()) 

        # test all of the employee data
        # -> TODO split employee features into seperate tests
        link.click() # move to the employee page

        # wait for the page to load
        page.wait_for_selector("#genral_information > table:nth-child(1) > tbody > tr > td > div.modulHeader")
        while is_loading(page):
            sleep(0.5)

        # get the infotable
        general_table = page.locator("#genral_information > table:nth-child(2)")

        # create a new DataComp to compare our test results
        data_comparer = DataComp(open("employee.json", "+r")) # feed it the employee.json
        data_comparer.data_import(general_table.locator('tr').all()) # import the rows into the class
        
        data_comparer.data_export() # export the employee
        data_comparer.data_test() # test the employee

        is_worker_syncd = True


def test_worker_syncd(page: Page):
    global is_worker_syncd

    print(f"Expected 'Worker sync'd' is Actual {"'Worker sync'd'" if is_worker_syncd else "'Worker not sync'd'"}")
    assert is_worker_syncd