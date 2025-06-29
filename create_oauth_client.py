#!/usr/bin/env python3
"""
Script to automate OAuth2 client creation in Google Cloud Console
"""

import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def create_oauth_client():
    """Create OAuth2 client in Google Cloud Console"""
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    
    # Setup Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        project_id = "youtube-playlist-creator-oauth"
        
        # Navigate to Google Cloud Console credentials page
        url = f"https://console.cloud.google.com/apis/credentials?project={project_id}"
        print(f"🌐 Opening: {url}")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 30)
        
        print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        # Look for "CREATE CREDENTIALS" button
        print("🔍 Looking for CREATE CREDENTIALS button...")
        create_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'CREATE CREDENTIALS') or contains(text(), 'Create credentials')]"))
        )
        create_button.click()
        print("✅ Clicked CREATE CREDENTIALS")
        
        # Wait for dropdown and click "OAuth 2.0 Client IDs"
        print("🔍 Looking for OAuth 2.0 Client IDs option...")
        oauth_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'OAuth 2.0 Client IDs') or contains(text(), 'OAuth client ID')]"))
        )
        oauth_option.click()
        print("✅ Selected OAuth 2.0 Client IDs")
        
        # Wait for form to load
        time.sleep(3)
        
        # Select "Web application" from dropdown
        print("🔍 Looking for application type dropdown...")
        app_type_dropdown = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(@aria-label, 'Application type')]"))
        )
        app_type_dropdown.click()
        
        # Select Web application
        web_app_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Web application')]"))
        )
        web_app_option.click()
        print("✅ Selected Web application")
        
        # Enter name
        print("📝 Entering name...")
        name_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Name' or @placeholder='Name']"))
        )
        name_input.clear()
        name_input.send_keys("YouTube Playlist Creator Web App")
        print("✅ Entered name")
        
        # Add authorized redirect URIs
        print("📝 Adding redirect URIs...")
        
        # Click "ADD URI" button
        add_uri_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ADD URI')]"))
        )
        add_uri_button.click()
        
        # Add first URI
        uri_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'https://')]"))
        )
        uri_input.send_keys("https://f9f5-93-103-183-142.ngrok-free.app/oauth/callback")
        
        # Add second URI
        add_uri_button.click()
        uri_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'https://')]")
        uri_inputs[-1].send_keys("http://localhost:3000/oauth/callback")
        
        print("✅ Added redirect URIs")
        
        # Click CREATE button
        print("🔄 Creating OAuth client...")
        create_final_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'CREATE')]"))
        )
        create_final_button.click()
        
        # Wait for success dialog
        print("⏳ Waiting for creation to complete...")
        time.sleep(5)
        
        # Look for client ID and secret in the success dialog
        try:
            client_id_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '.apps.googleusercontent.com')]"))
            )
            client_id = client_id_element.text
            
            client_secret_element = driver.find_element(By.XPATH, "//div[contains(text(), 'GOCSPX-')]")
            client_secret = client_secret_element.text
            
            print(f"✅ OAuth client created successfully!")
            print(f"📋 Client ID: {client_id}")
            print(f"🔐 Client Secret: {client_secret}")
            
            # Create the credentials file
            credentials = {
                "web": {
                    "client_id": client_id,
                    "project_id": project_id,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": client_secret,
                    "redirect_uris": [
                        "https://f9f5-93-103-183-142.ngrok-free.app/oauth/callback",
                        "http://localhost:3000/oauth/callback"
                    ]
                }
            }
            
            # Save to file
            with open("web_client_secrets.json", "w") as f:
                json.dump(credentials, f, indent=2)
            
            print("💾 Saved credentials to web_client_secrets.json")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not extract credentials automatically: {e}")
            print("📋 Please manually copy the Client ID and Client Secret from the dialog")
            input("Press Enter after copying the credentials...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔍 Current page title:", driver.title)
        print("🔍 Current URL:", driver.current_url)
        
        # Take screenshot for debugging
        driver.save_screenshot("oauth_creation_error.png")
        print("📸 Screenshot saved as oauth_creation_error.png")
        
        return False
        
    finally:
        print("🔄 Keeping browser open for 30 seconds for manual verification...")
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    print("🚀 Starting OAuth2 client creation automation...")
    print("📋 This will create a Web Application OAuth2 client with:")
    print("   - Name: YouTube Playlist Creator Web App")
    print("   - Redirect URIs:")
    print("     * https://f9f5-93-103-183-142.ngrok-free.app/oauth/callback")
    print("     * http://localhost:3000/oauth/callback")
    print()
    
    success = create_oauth_client()
    
    if success:
        print("🎉 OAuth2 client created successfully!")
        print("✅ Credentials saved to web_client_secrets.json")
        print("🔄 You can now test the OAuth flow at: http://localhost:3000/oauth/demo")
    else:
        print("⚠️  Automation failed, but you can create it manually at:")
        print("   https://console.cloud.google.com/apis/credentials?project=youtube-playlist-creator-oauth") 