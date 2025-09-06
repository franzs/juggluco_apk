#!/usr/bin/env python

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set download directory
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

# Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
chrome_options.add_argument("--headless")  # Optional
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    print("Opening versions page...")
    driver.get("https://juggluco.en.uptodown.com/android/versions")

    reject_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "cookiescript_reject"))
    )
    reject_btn.click()
    print("Cookies rejected successfully.")

    time.sleep(3)

    # Wait for versions list
    print("Looking for a '-phone-' version...")
    version_list = wait.until(EC.presence_of_element_located((By.ID, "versions-items-list")))
    version_items = version_list.find_elements(By.XPATH, "./div")

    # Find the first entry with "-phone-" in the version name
    target_url = None
    for item in version_items:
        try:
            version_text = item.find_element(By.CLASS_NAME, "version").text
            if "-phone-" in version_text:
                target_url = item.get_attribute("data-url")
                print(f"Found version: {version_text}")
                break
        except:
            continue

    if not target_url:
        raise Exception("No version containing '-phone-' was found.")

    # Navigate to that version's download page
    print(f"Navigating to: {target_url}")
    driver.get(target_url)

    # Wait for download button and click via JS
    print("Waiting for download button...")
    dl_button = wait.until(EC.presence_of_element_located((By.ID, "detail-download-button")))
    driver.execute_script("arguments[0].scrollIntoView(true);", dl_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", dl_button)
    print("Download button clicked!")

    print("Awaiting file download...")
    end_time = time.time() + 60
    while time.time() < end_time:
        files = os.listdir(download_dir)
        if any(f.lower().endswith(".apk") for f in files):
            print("Downloaded:", files)
            break
        time.sleep(1)
    else:
        print("Download did not appear within time.")

finally:
    driver.quit()
