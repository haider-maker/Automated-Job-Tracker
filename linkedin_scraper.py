# linkedin_scraper.py (CLEAN + FIXED PATH VERSION)

import time
import json
import re
import os
from pathlib import Path
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from db.db_functions import add_applications_batch, job_already_processed


# -----------------------------------------------------
# PATHS (Unified across the entire project)
# -----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent                # Automated-Job-Tracker
ROOT_DIR = BASE_DIR.parent                                # Job_Tracker
CREDS_DIR = ROOT_DIR / "creds"                            # creds folder
DATA_DIR = BASE_DIR / "data"                              # /Automated-Job-Tracker/data
DB_PATH = DATA_DIR / "job_tracker.db"                     # Final Database Path (Correct)

# Load config
CONFIG_PATH = CREDS_DIR / "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

LINKEDIN_EMAIL = config.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = config.get("LINKEDIN_PASSWORD")

# -----------------------------------------------------
# Helpers
# -----------------------------------------------------

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
        result = now - timedelta(days=val)
    elif unit == "w":
        result = now - timedelta(weeks=val)
    elif unit == "m":
        result = now - timedelta(days=val * 30)
    elif unit == "y":
        result = now - timedelta(days=val * 365)
    else:
        result = now

    return str(result)


def clean_text(text):
    if not text:
        return "Unknown"
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().title()


def valid_entry(company, position):
    if len(position) < 2:
        return False
    if "linkedin" in position.lower():
        return False
    if "no jobs" in company.lower():
        return False
    return True


# -----------------------------------------------------
# Selenium Setup
# -----------------------------------------------------
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)


# -----------------------------------------------------
# Login
# -----------------------------------------------------
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
        driver.execute_script("window.scrollBy(0, window.innerHeight/1.5);")
        time.sleep(1.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# -----------------------------------------------------
# Main Scraper
# -----------------------------------------------------
def scrape_applied_jobs():
    driver.get("https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED")
    time.sleep(5)

    print("🌐 Scraping LinkedIn Applied Jobs...")

    all_jobs = []
    seen_urls = set()

    smooth_scroll()
    time.sleep(2)

    job_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-chameleon-result-urn]")

    print(f"🔍 Found {len(job_cards)} jobs on screen...")

    for job in job_cards:
        try:
            urn = job.get_attribute("data-chameleon-result-urn")
            if not urn:
                continue

            job_id = urn.split(":")[-1]
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}"

            # Skip duplicates
            if job_url in seen_urls or job_already_processed(job_url):
                continue

            lines = job.text.strip().split("\n")
            if len(lines) < 2:
                continue

            position = clean_text(lines[0])
            company = clean_text(lines[1])

            if not valid_entry(company, position):
                continue

            try:
                applied_info = job.find_element(
                    By.CSS_SELECTOR,
                    "span.reusable-search-simple-insight__text--small"
                ).text.strip()
                date_applied = parse_applied_text(applied_info)
            except:
                date_applied = datetime.now().date().isoformat()

            all_jobs.append({
                "date_applied": date_applied,
                "platform": "LinkedIn",
                "company": company,
                "position": position,
                "job_url": job_url,
                "notes": "Imported from LinkedIn Applied Jobs",
                "application_status": "Applied",
                "email_id": None
            })

            seen_urls.add(job_url)

        except StaleElementReferenceException:
            continue
        except Exception:
            continue

    # Save to DB
    if all_jobs:
        add_applications_batch(all_jobs)
        print(f"✅ Added {len(all_jobs)} new applications to DB.")
    else:
        print("ℹ️ No new applications found.")

    print("🎉 Done scraping.")


# -----------------------------------------------------
# MAIN
# -----------------------------------------------------
if __name__ == "__main__":
    try:
        linkedin_login()
        scrape_applied_jobs()
    finally:
        driver.quit()
        print("🚪 Chrome closed. Scraper finished.")
