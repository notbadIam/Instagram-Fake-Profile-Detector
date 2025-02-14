from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


CHROMEDRIVER_PATH = "D:/resources/New folder/Instagram-Fake-Profile-Detector/chromedriver.exe"  
CHROME_PROFILE_PATH = "C:/Users/hp/AppData/Local/Google/Chrome/User Data/default"  

# Chrome Options (Headless & User Profile)
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}") 
options.add_argument("--headless=new")  
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors=yes")
options.add_argument("--ssl-version-min=tls1.2")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--disable-blink-features=AutomationControlled") 
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")


if not os.path.exists(CHROMEDRIVER_PATH):
    print("ChromeDriver not found! Check the path.")
else:
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://socialblade.com/instagram/user/mr_.rathore___")  

    print("Chrome (Headless + Profile) is running!")

   
    wait = WebDriverWait(driver, 10)

    
    try:
        followers = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlock']/div[3]/span[2]"))).text
        following = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlock']/div[4]/span[2]"))).text
        uploads = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlock']/div[2]/span[2]"))).text
        name = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlockTop']/div[1]/h2"))).text
        username = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='YouTubeUserTopInfoBlockTop']/div[1]/h2/a"))).text
        
        

        print(f" Followers: {followers}")
        print(f"Following: {following}")
        print(f"Uploads: {uploads}")
        name = name.split(username)[0]
        print(f"Name: {name}")

    except Exception as e:
        print(f"Error extracting metrics: {e}")

    
    driver.quit()
