import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def scrape_and_update():
    # --- 1. SETUP HEADLESS BROWSER ---
    print("Starting Chrome in the background...")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Essential so GitHub Actions doesn't crash
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # --- 2. SCRAPE ESPN ---
    print("Loading ESPNcricinfo...")
    url = "https://www.espncricinfo.com/series/ipl-2025-1449924/most-valuable-players"
    driver.get(url)
    
    # Wait 5 seconds to let the JavaScript render the table
    time.sleep(5) 

    print("Extracting data...")
    # Add your column headers as the first row
    extracted_data = [["Player Name", "Total Impact Points"]] 
    
    rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) >= 2:
            player_name = columns[0].text
            impact_points = columns[4].text # Adjust this index if the points are in a different column
            extracted_data.append([player_name, impact_points])

    driver.quit()

    # --- 3. UPDATE GOOGLE SHEETS ---
    print("Connecting to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # --- SECURE CREDENTIALS LOGIC ---
    google_creds_json = os.getenv('GOOGLE_CREDENTIALS')
    
    if google_creds_json:
        # If running on GitHub Actions, use the Secret
        print("Using GitHub Secrets for authentication...")
        creds_dict = json.loads(google_creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # If running locally on your computer, use the credentials.json file
        print("Using local credentials.json file...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(script_dir, "credentials.json")
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        
    client = gspread.authorize(creds)
    
    # REPLACE WITH YOUR ACTUAL SHEET NAME AND TAB NAME
    sheet = client.open("ipl 2026").worksheet("Sheet1")
    
    print("Uploading data...")
    sheet.clear() # Wipes the old data clean
    sheet.update('A1', extracted_data) # Pastes the fresh data
    
    print("Success! Google Sheet updated.")

if __name__ == "__main__":
    scrape_and_update()
