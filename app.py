from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import joblib
import numpy as np
import time



app = Flask(__name__)


model = joblib.load("model/model.pkl")
scaler = joblib.load("model/scaler.pkl")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")  
options.add_argument("--window-size=1920,1080")  
options.add_argument("--start-maximized")  
options.add_argument("--disable-dev-shm-usage")  
options.add_argument("--no-sandbox") 
options.add_argument("--log-level=3")  
options.add_argument("--disable-extensions")  
options.add_argument("--disable-infobars")  

# Automatically download and use ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)




def convert_to_number(value):
    value = value.replace(',', '')  

    if 'M' in value:
        return int(float(value.replace('M', '')) * 1_000_000)  
    elif 'K' in value:
        return int(float(value.replace('K', '')) * 1_000)  
    else:
        return int(value) 


def clean_and_convert(text, remove_word):
    cleaned_text = text.replace(remove_word, "").strip() 
    return int(cleaned_text.replace(",", ""))  


def scrape_instagram(username):
    """Scrapes Instagram profile data using Selenium."""
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f"https://app.iqhashtags.com/preview?profile={username}&referrer=webstagram")
    time.sleep(5) 
    wait = WebDriverWait(driver, 180)  #
    

    try:
        # XPaths for Instagram metrics
        followers_xpath = "/html/body/ht-root/ht-profile-preview-routing/div/div[4]/ht-profile-preview/div/ht-profile-preview-result/div/div[2]/div/div[1]/div[1]/div[1]/ht-profile-preview-result-profile/div/div[2]/div[2]/div[1]"
        following_xpath = "/html/body/ht-root/ht-profile-preview-routing/div/div[4]/ht-profile-preview/div/ht-profile-preview-result/div/div[2]/div/div[1]/div[1]/div[1]/ht-profile-preview-result-profile/div/div[2]/div[3]/div[1]"
        uploads_xpath = "/html/body/ht-root/ht-profile-preview-routing/div/div[4]/ht-profile-preview/div/ht-profile-preview-result/div/div[2]/div/div[1]/div[1]/div[1]/ht-profile-preview-result-profile/div/div[2]/div[1]/div[1]"

        
        try:
            followers = wait.until(EC.presence_of_element_located((By.XPATH, followers_xpath))).text
        except:
            followers = "0"  # Default to 0 if not found

        try:
            following = wait.until(EC.presence_of_element_located((By.XPATH, following_xpath))).text
        except:
            following = "0"

        try:
            uploads = wait.until(EC.presence_of_element_located((By.XPATH, uploads_xpath))).text
        except:
            uploads = "0"

        driver.quit()
        
        return {
            "followers": convert_to_number(followers),
            "following": convert_to_number(following),
            "uploads": convert_to_number(uploads),
            "oldfollowers": followers,
            "oldfollowing": following,
            "olduploads": uploads
        }
    
    except Exception as e:
        driver.quit()
        return {"error": f"Failed to scrape data: {str(e)}"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    username = data.get("username")
    
    if not username:
        return jsonify({"error": "Username is required!"})
    
    scraped_data = scrape_instagram(username)
    if "error" in scraped_data:
        return jsonify(scraped_data)
    
    try:
        features = np.array([[ scraped_data["followers"], scraped_data["following"], scraped_data["uploads"]]])
        features = scaler.transform(features)  
        
        real_prob = (1 - model.predict_proba(features)[0][1]) * 100  

        return jsonify({
            "username": username,
            "followers": scraped_data["oldfollowers"],
            "following": scraped_data["oldfollowing"],
            "uploads": scraped_data["olduploads"],
            "real_probability": round(real_prob, 2)
        })
    
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
