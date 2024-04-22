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
    """Check if a new file has started downloading."""
    start_time = time.time()
    while time.time() - start_time < 30:  # wait for 30 seconds
        current_files = get_download_directory_files(download_path)
        new_files = [f for f in current_files if f not in previous_files]
        if len(current_files) > len(previous_files):
            return True
        time.sleep(1)  # check every second
    return False


def crawl_information():
    download_path = r"C:\Users\lily\Downloads"
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,  # To auto download without asking
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    # Open the pre-set search results page
    driver.get(
        "http://www38.swfwmd.state.fl.us/Erp/Erp/Search/ERPSearch.aspx?r=n&function=return&UniquePageID=f1d6239a-1bb9-4b0b-bcdc-de6011659ea1")

    # Click on 'View All' and scroll to the bottom to load all links
    view_all_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "View All")))
    view_all_button.click()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Wait for all elements to load

    # Wait for the 'View Details' links to be visible and count them
    detail_links = wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "View Details")))
    total_links = len(detail_links)
    print(f"Total 'View Details' links found: {total_links}")

    for i in range(total_links):
        # Only click 'View All' again if it's not the first iteration
        if i > 0:
            view_all_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "View All")))
            view_all_button.click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait for the page to load completely

        # Get a fresh set of 'View Details' links
        detail_links = wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "View Details")))

        detail_links[i].click()

        documents_tab_xpath = '//*[@id="__tab_Detail1_AjaxPermitTabs_TabPanel8"]'
        documents_tab = wait.until(EC.element_to_be_clickable((By.XPATH, documents_tab_xpath)))
        documents_tab.click()

        permit_number_element = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="Detail1_LabelPermitNumberExt"]')))
        permit_number = permit_number_element.text.strip()

        try:
            plans_row_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[contains(., 'Plans')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", plans_row_element)
            time.sleep(3)  # Adjust time as needed for the page to stabilize

            download_buttons = plans_row_element.find_elements(By.XPATH,
                                                               ".//img[contains(@onclick, 'DownloadDocument')]")
            for button in download_buttons:
                previous_files = get_download_directory_files(download_path)
                button.click()

                if file_started_downloading(download_path, previous_files):
                    print(f"Download started for document under ERP permit number {permit_number}")
                else:
                    print(f"Download failed for document under ERP permit number {permit_number}")

        except TimeoutException:
            print(f"No 'Plans' under ERP permit number {permit_number}")

        # Navigate back or perform other end-of-loop actions here
        back_to_search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PageHeaderMain_BackTo"]')))
        back_to_search_button.click()

    driver.quit()


# Call the function from the main block
if __name__ == "__main__":
    crawl_information()
