from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

driver_path ="C:/WebDrivers/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)

driver = webdriver.Chrome(service = service)

#Opens google
driver.get("https://www.google.com")

# Wait a bit for the page to load
time.sleep(2)

# Find the search box and enter a query
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("NVIDIA RTX 3060")
search_box.submit()

# Wait to see results
time.sleep(5)

# Close browser
driver.quit()