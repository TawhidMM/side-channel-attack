import time
import json
import os
import signal
import sys
import random
import traceback
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import database
from database import Database

WEBSITES = [
    # websites of your choice
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com",
    "https://prothomalo.com",
]

TRACES_PER_SITE = 1
FINGERPRINTING_URL = "http://localhost:5000" 
OUTPUT_PATH = "dataset.json"

# Initialize the database to save trace data reliably
database.db = Database(WEBSITES)

""" Signal handler to ensure data is saved before quitting. """
def signal_handler(sig, frame):
    print("\nReceived termination signal. Exiting gracefully...")
    try:
        database.db.export_to_json(OUTPUT_PATH)
    except:
        pass
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


"""
Some helper functions to make your life easier.
"""

def is_server_running(host='127.0.0.1', port=5000):
    """Check if the Flask server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def setup_webdriver():
    """Set up the Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def retrieve_traces_from_backend(driver):
    """Retrieve traces from the backend API."""
    traces = driver.execute_script("""
        return fetch('/api/get_results')
            .then(response => response.ok ? response.json() : {traces: []})
            .then(data => data.traces || [])
            .catch(() => []);
    """)
    
    count = len(traces) if traces else 0
    print(f"  - Retrieved {count} traces from backend API" if count else "  - No traces found in backend storage")
    return traces or []

def clear_trace_results(driver, wait):
    """Clear all results from the backend by pressing the button."""
    clear_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear All Results')]")
    clear_button.click()

    wait.until(EC.text_to_be_present_in_element(
        (By.XPATH, "//div[@role='alert']"), "Cleared"))
    
def is_collection_complete():
    """Check if target number of traces have been collected."""
    current_counts = database.db.get_traces_collected()
    remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
                      for website, count in current_counts.items()}
    return sum(remaining_counts.values()) == 0

"""
Your implementation starts here.
"""
def interact_with_website(driver, website_url):
    """Interact with the website to trigger fingerprinting."""
    try:
        # Open the target website in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(website_url)
        print("  - Opened target website")

        # Interact with the target website (simple scroll as a sample interaction)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        print("  - Interacted with the website")

        # Close the tab and switch back
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print("  - Switched back to fingerprinting tab")

    except Exception as e:
        print("  [!] Error during trace collection:", e)
        traceback.print_exc()


def collect_single_trace(driver, wait, website_url):
    try:
        print(f"[+] Collecting trace for: {website_url}")

        # Step 1: Open the fingerprinting website
        driver.get(FINGERPRINTING_URL)
        time.sleep(1)

        # Step 2: Click the "Collect Trace Data" button
        collect_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Collect Trace Data')]"))
        )
        collect_button.click()
        print("  - Started trace collection")

        # step 3: interact with the website to collect traces
        interact_with_website(driver, website_url)

        # Step 6: Wait for the alert or status text indicating completion
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@role='alert']"), "Trace collected successfully")
        )
        print("  - Trace collection complete")

        # Step 7: Fetch the newly collected trace from the backend
        traces = retrieve_traces_from_backend(driver)
        if traces:
            # database.db.add_trace(website_url, traces[-1])  # Add last trace only
            return True
        else:
            print("  - No new traces found.")
            return False

    except Exception as e:
        print("  [!] Error during trace collection:", e)
        traceback.print_exc()
        return False


def collect_fingerprints(driver, target_counts=None):
    """ Implement the main logic to collect fingerprints.
    1. Calculate the number of traces remaining for each website
    2. Open the fingerprinting website
    3. Collect traces for each website until the target number is reached
    4. Save the traces to the database
    5. Return the total number of new traces collected
    """

def main():
    """ Implement the main function to start the collection process.
    1. Check if the Flask server is running
    2. Initialize the database
    3. Set up the WebDriver
    4. Start the collection process, continuing until the target number of traces is reached
    5. Handle any exceptions and ensure the WebDriver is closed at the end
    6. Export the collected data to a JSON file
    7. Retry if the collection is not complete
    """

if __name__ == "__main__":
    main()
