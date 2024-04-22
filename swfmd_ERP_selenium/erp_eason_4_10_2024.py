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
import re
import shutil


def sanitize_filename(filename):
    """Remove or replace invalid characters in the filename."""
    return re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)

def wait_for_download_completion(download_path, temp_file_name, timeout=60):
    """Wait until the temporary file is replaced with the final downloaded file."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_files = get_download_directory_files(download_path)
        if temp_file_name not in current_files:
            for file in current_files:
                if file.endswith('.pdf'):  # Assuming the file is a PDF
                    return file
            # If the temporary file is gone but no new PDF is found, wait a bit before retrying
            time.sleep(2)
        time.sleep(1)
    return None

def get_download_directory_files(download_path):
    """Get a list of files in the download directory."""
    return os.listdir(download_path)

def file_started_downloading(download_path, previous_files):
    """Check if a new file has started downloading."""
    start_time = time.time()
    while time.time() - start_time < 30:  # wait for 30 seconds
        current_files = get_download_directory_files(download_path)
        new_files = [f for f in current_files if f not in previous_files]
        if new_files:
            return True, new_files[0]  # Return the name of the new file
        time.sleep(1)  # check every second
    return False, None

def ensure_directory_exists(folder_path):
    """Ensure that the specified directory exists, and if not, create it."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def move_downloaded_file(download_path, original_file_name, target_folder, new_file_name):
    """Move the downloaded file to the target directory."""
    original_file_path = os.path.join(download_path, original_file_name)
    target_file_path = os.path.join(target_folder, new_file_name)
    try:
        shutil.move(original_file_path, target_file_path)
        print(f"File moved to {target_file_path}")
    except Exception as e:
        print(f"Error moving file from {original_file_path} to {target_file_path}: {e}")


def crawl_information():
    download_path = r"C:\Users\lily\Downloads"
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,  # To auto download without asking
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    driver.get("http://www38.swfwmd.state.fl.us/Erp/Erp/Search/ERPSearch.aspx?r=n&function=return&UniquePageID=27d6e44c-4759-4799-b34d-e325a494a1d1")

    view_all_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "View All")))
    view_all_button.click()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    detail_links = wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "View Details")))
    total_links = len(detail_links)
    print(f"Total 'View Details' links found: {total_links}")

    for i in range(total_links):
        if i > 0:
            view_all_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "View All")))
            view_all_button.click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

        detail_links = wait.until(EC.visibility_of_all_elements_located((By.LINK_TEXT, "View Details")))
        detail_links[i].click()

        documents_tab_xpath = '//*[@id="__tab_Detail1_AjaxPermitTabs_TabPanel8"]'
        documents_tab = wait.until(EC.element_to_be_clickable((By.XPATH, documents_tab_xpath)))
        documents_tab.click()

        permit_number_element = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="Detail1_LabelPermitNumberExt"]')))
        permit_number = sanitize_filename(permit_number_element.text.strip())
        permit_folder_path = os.path.join(download_path, permit_number)
        ensure_directory_exists(permit_folder_path)

        try:
            plans_row_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[contains(., 'Plans')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", plans_row_element)
            time.sleep(3)

            download_buttons = plans_row_element.find_elements(By.XPATH,
                                                               ".//img[contains(@onclick, 'DownloadDocument')]")
            for button in download_buttons:
                previous_files = get_download_directory_files(download_path)
                button.click()

                download_started, downloaded_file = file_started_downloading(download_path, previous_files)
                if download_started:
                    print(f"Download started for document under ERP permit number {permit_number}")
                    # Wait for the actual PDF to be ready
                    final_file_name = wait_for_download_completion(download_path, downloaded_file)
                    if final_file_name:
                        move_downloaded_file(download_path, final_file_name, permit_folder_path, final_file_name)
                    else:
                        print(f"Download did not complete or file was not found for ERP permit number {permit_number}")
                else:
                    print(f"Download failed for document under ERP permit number {permit_number}")

        except TimeoutException:
            print(f"No 'Plans' under ERP permit number {permit_number}")

        back_to_search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PageHeaderMain_BackTo"]')))
        back_to_search_button.click()

    driver.quit()

if __name__ == "__main__":
    crawl_information()
