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

# ✅ Load ML Model & Scaler
model = joblib.load("model/model.pkl")
scaler = joblib.load("model/scaler.pkl")

# ✅ Get Chrome & Chromedriver Paths from Environment Variables
CHROME_PATH = os.getenv("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

# ✅ Configure Chrome Options
options = webdriver.ChromeOptions()
options.binary_location = CHROME_PATH  # Use Chrome from environment variable
options.add_argument("--headless=new")  # Headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

def scrape_instagram(username):
    try:
        service = Service(CHROMEDRIVER_PATH)  # Use correct Chromedriver path
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(f"https://socialblade.com/instagram/user/{username}")
        wait = WebDriverWait(driver, 10)

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

    features = np.array([[scraped_data["uploads"], scraped_data["followers"], scraped_data["following"]]])
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
