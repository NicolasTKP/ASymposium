from selenium import webdriver
from bs4 import BeautifulSoup
import json
import re
import time

driver = webdriver.Chrome()
driver.get('https://publicinfobanjir.water.gov.my/wp-content/themes/enlighten/query/searchstationWL.php?name=12&language=en')

# Wait for page to fully load (use WebDriverWait if necessary)
html = driver.page_source
time.sleep(12)  # Optional: wait for dynamic content to load
soup = BeautifulSoup(html, 'html.parser')

# Regex to find JSON block in HTML
pattern = re.compile(r'\{.*?"name": ?"Empangan Batu".*?\}', re.DOTALL)
match = pattern.search(html)
if match:
    data = json.loads(match.group())
    print(data)

driver.quit()
