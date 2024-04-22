import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_download_directory_files(download_path):
    """Get a list of files in the download directory."""
    return os.listdir(download_path)

def file_started_downloading(download_path, previous_files):
    time.sleep(5)  # Wait a few seconds to ensure the download starts
    current_files = get_download_directory_files(download_path)
    return len(current_files) > len(previous_files)

def crawl_information():
    download_path = r"C:\Users\lily\Downloads"  # Set your download directory here

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,  # To auto download without asking
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    # Open the pre-set search results page
    driver.get("http://www38.swfwmd.state.fl.us/Erp/Erp/Search/ERPSearch.aspx?r=n&function=return&UniquePageID=1d64e34f-b28b-42ac-8d7d-63207d5860fc")

    view_all_button_xpath = '//*[@id="TabContainer1_TabPanel5_SearchWupResults1_FlexGridResults_lblPaging"]/a[2]'
    view_all_button = wait.until(EC.element_to_be_clickable((By.XPATH, view_all_button_xpath)))
    view_all_button.click()

    detail_links = wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "View Details")))

    for i in range(len(detail_links)):
        detail_links = wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "View Details")))
        detail_links[i].click()

        documents_tab_xpath = '//*[@id="__tab_Detail1_AjaxPermitTabs_TabPanel8"]'
        documents_tab = wait.until(EC.element_to_be_clickable((By.XPATH, documents_tab_xpath)))
        documents_tab.click()

        permit_number_element = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="Detail1_LabelPermitNumberExt"]')))
        permit_number = permit_number_element.text.strip()

        # Scroll to the specific element
        target_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="row$1783016200772"]')))
        actions = ActionChains(driver)
        actions.move_to_element(target_element).perform()

        download_buttons = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="row$1783016188854"]/td[4]')))

        for button in download_buttons:
            previous_files = get_download_directory_files(download_path)
            main_window = driver.current_window_handle
            button.click()

            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(
                [window_handle for window_handle in driver.window_handles if window_handle != main_window][0])

            if file_started_downloading(download_path, previous_files):
                print(f"Download started for document under ERP permit number {permit_number}")
            else:
                print(f"Download failed for document under ERP permit number {permit_number}")

            driver.close()
            driver.switch_to.window(main_window)

        back_to_search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PageHeaderMain_BackTo"]')))
        back_to_search_button.click()

    driver.quit()

crawl_information()