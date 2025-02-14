from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import joblib
import numpy as np

app = Flask(__name__)


model = joblib.load("model/model.pkl")
scaler = joblib.load("model/scaler.pkl")


CHROMEDRIVER_PATH = "D:/resources/New folder/Instagram-Fake-Profile-Detector/chromedriver.exe"
CHROME_PROFILE_PATH = "C:/Users/hp/AppData/Local/Google/Chrome/User Data/default"


options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
options.add_argument("--headless=new")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors=yes")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

def scrape_instagram(username):
    if not os.path.exists(CHROMEDRIVER_PATH):
        return {"error": "ChromeDriver not found! Check the path."}
    
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f"https://socialblade.com/instagram/user/{username}")
    wait = WebDriverWait(driver, 10)
    
    try:
        followers = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlock']/div[3]/span[2]"))).text
        following = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlock']/div[4]/span[2]"))).text
        uploads = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlock']/div[2]/span[2]"))).text
        name = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlockTop']/div[1]/h2"))).text
        username_extracted = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlockTop']/div[1]/h2/a"))).text
        
        name = name.split(username_extracted)[0].strip()
        
        driver.quit()
        return {
            "followers": int(followers.replace(',', '')),
            "following": int(following.replace(',', '')),
            "uploads": int(uploads.replace(',', '')),
            "name": name
        }
    except Exception as e:
        driver.quit()
        return {"error": f"Failed to scrape data: {e}"}

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
    
    features = np.array([[
    scraped_data["uploads"],
    scraped_data["followers"],
    scraped_data["following"],
]])
    features = scaler.transform(features)

    real_prob = (1 - model.predict_proba(features)[0][1]) * 100  # Real probability

    
    return jsonify({
    "username": username,
    "followers": scraped_data["followers"],
    "following": scraped_data["following"],
    "uploads": scraped_data["uploads"],
    "real_probability": round(real_prob, 2)  
})


if __name__ == "__main__":
    app.run(debug=True)
