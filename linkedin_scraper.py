# linkedin_applied_scraper_stable.py

import time
import json
import re
import os
from db.db_functions import add_applications_batch, job_already_processed
from datetime import datetime, timedelta
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

# -----------------------------
# Paths Setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # Automated-Job-Tracker folder
ROOT_DIR = os.path.dirname(BASE_DIR)                       # Job_Tracker folder
CREDS_DIR = os.path.join(ROOT_DIR, "creds")               # creds folder

# Load config.json from creds
CONFIG_PATH = os.path.join(CREDS_DIR, "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

LINKEDIN_EMAIL = config.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = config.get("LINKEDIN_PASSWORD")
DB_PATH = config.get("DB_PATH", os.path.join(BASE_DIR, "data", "job_tracker.db"))

# -----------------------------
# Date parsing helper
# -----------------------------
def parse_applied_text(text):
    now = datetime.now().date()
    if not text:
        return str(now)

    text = text.lower().strip()
    match = re.search(r"(\d+)\s*([dwmy])", text)
    if not match:
        return str(now)

    val, unit = int(match.group(1)), match.group(2)
    if unit == "d":
        result_date = now - timedelta(days=val)
    elif unit == "w":
        result_date = now - timedelta(weeks=val)
    elif unit == "m":
        result_date = now - timedelta(days=val * 30)
    elif unit == "y":
        result_date = now - timedelta(days=val * 365)
    else:
        result_date = now

    return str(result_date)

# -----------------------------
# Selenium setup
# -----------------------------
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
# options.add_argument("--headless")  # Uncomment for silent run

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# -----------------------------
# Helpers
# -----------------------------
def clean_text(text: str) -> str:
    if not text:
        return "Unknown"
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().title()

def valid_entry(company: str, position: str) -> bool:
    if len(position) < 2 or "linkedin" in position.lower():
        return False
    if "no jobs" in company.lower():
        return False
    return True

def linkedin_login():
    driver.get("https://www.linkedin.com/login")
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print("✅ Logged into LinkedIn")
    time.sleep(4)

def smooth_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, window.innerHeight/2);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# -----------------------------
# Main Scraper
# -----------------------------
def scrape_applied_jobs():
    driver.get("https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED")
    print("🌐 Navigating to applied jobs page...")
    time.sleep(6)

    all_jobs = []
    seen_urls = set()
    page_num = 1

    while True:
        print(f"\n📄 Scraping page {page_num}...")

        smooth_scroll()
        time.sleep(2)

        job_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-chameleon-result-urn]")

        for job in job_cards:
            try:
                urn = job.get_attribute("data-chameleon-result-urn")
                if not urn:
                    continue

                job_url = f"https://www.linkedin.com/jobs/view/{urn.split(':')[-1]}"
                full_text = job.text.strip().split("\n")
                if len(full_text) < 2:
                    continue

                position = clean_text(full_text[0])
                company = clean_text(full_text[1])
                if not valid_entry(company, position):
                    continue
                if job_url in seen_urls or job_already_processed(job_url):
                    continue

                try:
                    applied_info = job.find_element(
                        By.CSS_SELECTOR,
                        "span.reusable-search-simple-insight__text--small"
                    ).text.strip()
                    date_applied = parse_applied_text(applied_info)
                except Exception:
                    date_applied = datetime.now().date().isoformat()

                all_jobs.append({
                    "date_applied": date_applied,
                    "platform": "LinkedIn",
                    "company": company,
                    "position": position,
                    "job_url": job_url,
                    "notes": "Auto-imported from LinkedIn Applied Jobs",
                    "application_status": "Applied",
                    "email_id": None
                })
                seen_urls.add(job_url)

            except StaleElementReferenceException:
                continue
            except Exception:
                continue

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
            if "disabled" in next_button.get_attribute("class"):
                print("🟡 No more pages.")
                break
            old_urns = [job.get_attribute("data-chameleon-result-urn") for job in job_cards]
            next_button.click()
            print("⏳ Clicking Next to load more jobs...")
            WebDriverWait(driver, 15).until(
                lambda d: any(
                    el.get_attribute("data-chameleon-result-urn") not in old_urns
                    for el in d.find_elements(By.CSS_SELECTOR, "div[data-chameleon-result-urn]")
                )
            )
            page_num += 1
            time.sleep(1.5)
        except Exception:
            print("🟡 Next button not found or no more pages.")
            break

    if all_jobs:
        add_applications_batch(all_jobs)
        print(f"✅ Added {len(all_jobs)} new job applications to DB.")
    else:
        print("ℹ️ No new unique applications found.")

    print(f"✅ Done: {len(all_jobs)} total collected from {page_num} pages.")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    try:
        linkedin_login()
        scrape_applied_jobs()
    finally:
        driver.quit()
        print("✅ Scraper finished and browser closed")
