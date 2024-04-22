from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re  # Import regular expression module

def ensure_folder_exists(folder_path):
    """Ensure the folder exists, and create it if it does not."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print(f"Folder created: {folder_path}")

def move_files_to_folder(download_path, folder_name):
    """Move all files from the download directory to a specified folder named after the application."""
    folder_path = os.path.join(download_path, folder_name)
    ensure_folder_exists(folder_path)
    # Wait until there are no '.crdownload' files in the directory
    while any(file.endswith('.crdownload') for file in os.listdir(download_path)):
        print("Waiting for downloads to complete...")
        time.sleep(5)  # Check every 5 seconds
    # Move all completed download files in the directory to the new folder
    for file in os.listdir(download_path):
        file_path = os.path.join(download_path, file)
        if os.path.isfile(file_path):  # Ensure the item is a file
            shutil.move(file_path, os.path.join(folder_path, file))
    print(f"All files moved to {folder_path}")

def safe_click(driver, element, max_attempts=3, delay=1):
    """Attempts to click on a given element up to max_attempts times with a delay between tries."""
    attempts = 0
    while attempts < max_attempts:
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            # Attempt to click the element using ActionChains
            ActionChains(driver).move_to_element(element).click().perform()
            return True  # Click was successful
        except WebDriverException as e:
            print(f"Click failed on attempt {attempts + 1}: {str(e)}")
            time.sleep(delay)  # Wait before retrying
            attempts += 1
    return False  # Failed to click after max_attempts

def crawl_information():
    download_path = r"C:\Users\Yixuan Gong\Downloads"
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,  # To auto download without asking
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    checked_for_specific_page = False

    try:
        # Navigate to the website
        driver.get("https://my.sfwmd.gov/ePermitting/PopulateLOVs.do?flag=1")

        # Select Permit Type (ERP)
        permit_type_select = wait.until(EC.presence_of_element_located((By.NAME, "permitFamilyType")))
        Select(permit_type_select).select_by_visible_text('ERP')

        ###############################TESTING ONLY DONT DELETE########################################################
        # application_no_input = wait.until(EC.presence_of_element_located((By.NAME, "applicationNo")))
        # application_no_input.clear()
        # application_no_input.send_keys('240410-43291')
        ###############################TESTING ONLY DONT DELETE#####################################################

        # Select From Date (January 1, 2024)
        day_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateDate")))
        Select(day_from_select).select_by_value('02')

        month_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateMonth")))
        Select(month_from_select).select_by_visible_text('MAR')

        year_from_select = wait.until(EC.presence_of_element_located((By.NAME, "fromdateYear")))
        Select(year_from_select).select_by_visible_text('2024')

        # Select To Date (April 15, 2024)
        day_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateDate")))
        Select(day_to_select).select_by_visible_text('18')

        month_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateMonth")))
        Select(month_to_select).select_by_visible_text('APR')

        year_to_select = wait.until(EC.presence_of_element_located((By.NAME, "todateYear")))
        Select(year_to_select).select_by_visible_text('2024')

        # Click the Search button
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"][value="Search Records"]')))
        search_button.click()
        print("Search clicked")
        time.sleep(5)  # Allow time for the search results to load

        # Continuously process until no more pages are available
        while True:
            time.sleep(2)

            # Initialize a set to keep track of clicked links
            clicked_links = set()
            pages = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//td[@align='center']/strong[contains(text(), 'of 679')]")))
            if (pages):
                print('Current page: ' + pages[0].text)
            ####################################################翻页功能，仅在代码中断时使用#####################################################################
            while True:
                if not checked_for_specific_page:
                    while True:
                        try:
                            WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located(
                                        (By.XPATH, "//td[@align='center']/strong[text()='376 to 378 of 679']")))
                            print("Found the element with text '376 to 378 of 679'.")
                            checked_for_specific_page = True
                            break
                        except TimeoutException:
                            print("Text '376 to 378 of 679' not found on this page. Clicking next page.")
                            try:
                                next_page = driver.find_element(By.CSS_SELECTOR,
                                                                "a[href*='IterateReport.do?page=next'] img[src*='nextcal.gif']")
                                next_page.click()
                                print("Clicked next page. Waiting for page to load.")
                            except NoSuchElementException:
                                print("No more pages to process.")
                                break
                        except Exception as e:
                            print(f"An error occurred: {e}")
                            break
                    if checked_for_specific_page:
                        break
                if checked_for_specific_page:
                    break
            #########################################################################################################################

            # Find and process each application link
            applications = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a[href*='DetailedReport']")))

            # Filter out any applications where the 'href' attribute is null or empty
            filtered_applications = [app for app in applications if app.get_attribute('href')  and re.match(r'^\d+(-\d+)*$', app.text) and app.is_displayed()]

            # Capture current window handle before the click
            main_window = driver.current_window_handle
            all_windows_before_click = driver.window_handles

            for app in filtered_applications:
                driver.execute_script("arguments[0].scrollIntoView(true);", app)
                app_text = app.text
                if app_text not in clicked_links:
                    app.click()
                    print(f"'Handling Application# {app_text}'")
                    clicked_links.add(app_text)
                    time.sleep(2)
                    # Get new window handle and switch to it
                    new_windows = [window for window in driver.window_handles if window not in all_windows_before_click]
                    if new_windows:
                        driver.switch_to.window(new_windows[0])

                        # Now interact in the new window
                        calculation_element = driver.find_elements(By.XPATH,
                                                                   "//*[starts-with(normalize-space(text()), 'Calculations - Design Plans')]")
                        if not calculation_element or not calculation_element[0].is_displayed():
                            print("No calculation element found, or it is not visible. Skipping to next application.")
                            driver.close()  # Close the current window
                            driver.switch_to.window(main_window)  # Switch back to the main window
                            continue  # Skip to the next application

                        if calculation_element:
                            ActionChains(driver).move_to_element(calculation_element[0]).click().perform()
                            maps_elements = driver.find_elements(By.XPATH,
                                                                 "//*[starts-with(normalize-space(text()), 'Maps(')]")
                            if maps_elements:
                                driver.execute_script("arguments[0].scrollIntoView(true);", maps_elements[0])
                                safe_click(driver, maps_elements[0])
                            plans_elements = driver.find_elements(By.XPATH,
                                                                  "//*[starts-with(normalize-space(text()), 'Plans(')]")
                            if plans_elements:
                                driver.execute_script("arguments[0].scrollIntoView(true);", plans_elements[0])
                                safe_click(driver, plans_elements[0])
                            sealed_elements = driver.find_elements(By.XPATH,
                                                                   "//*[starts-with(normalize-space(text()), 'Sealed Document Authentication(')]")
                            if sealed_elements:
                                driver.execute_script("arguments[0].scrollIntoView(true);", sealed_elements[0])
                                safe_click(driver, sealed_elements[0])
                            reports_elements = driver.find_elements(By.XPATH,
                                                                  "//*[starts-with(normalize-space(text()), 'Reports(')]")
                            if reports_elements:
                                driver.execute_script("arguments[0].scrollIntoView(true);", reports_elements[0])
                                safe_click(driver, reports_elements[0])
                            photos_elements = driver.find_elements(By.XPATH,
                                                                  "//*[starts-with(normalize-space(text()), 'Photos(')]")
                            if photos_elements:
                                driver.execute_script("arguments[0].scrollIntoView(true);", photos_elements[0])
                                safe_click(driver, photos_elements[0])
                            # After clicking 'Maps and plans', find all <a> links that include 'docdownload' in their href attribute
                            doc_links = driver.find_elements(By.XPATH,
                                                             "//span[contains(@style, 'display: block;')]//a[contains(@href, 'docdownload')]")
                            print(f"Found {len(doc_links)} document download link(s).")

                            # Iterate through each found link and click
                            for link in doc_links:
                                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                                time.sleep(0.5)  # Small pause to ensure scrolling has completed
                                current_handles = driver.current_window_handle  # Existing window handles before click
                                link.click()  # Perform the click action
                                time.sleep(1)
                                driver.switch_to.window(current_handles)
                                time.sleep(2)  # Wait 5 seconds after each click

                        time.sleep(1)
                        # Move downloaded files to a new folder named after the application
                        move_files_to_folder(download_path, app_text)  # This is where you call the folder management
                        # Close the new window and switch back to the original window
                        driver.close()
                        driver.switch_to.window(main_window)
                    else:
                        print("No new window opened")
                time.sleep(1)  # Wait for folder contents to load
            try:
                print("clicking next page")
                next_page = driver.find_element(By.CSS_SELECTOR,
                                               "a[href*='IterateReport.do?page=next'] img[src*='nextcal.gif']")
                next_page.click()
                time.sleep(2)  # Wait for the next page of results to load
            except:
                print("No more pages to process.")
                break
    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    crawl_information()
