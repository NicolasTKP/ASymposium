from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import json
import time
import pandas as pd

CHROMEDRIVER_PATH = "chromedriver.exe" 
param = {
    'station': '3216005_',
    'from': '07/06/2025%2022:00',
    'to': '08/06/2025%2022:00',
    'datafreq': '60'
}

def readings_populated(driver):
    try:
        readings = driver.execute_script("return readings;")
        return bool(readings and readings.get('labels'))
    except Exception:
        return False

def main():
    global param
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode

    driver = webdriver.Chrome(service=service, options=options)
    df = pd.DataFrame()
    try:
        url = f"https://publicinfobanjir.water.gov.my/wl-graph/?stationid={param['station']}&datefrom={param['from']}&dateto={param['to']}&ymax=&ymin=&xfreq=6&datafreq={param['datafreq']}&lang=en"
        driver.get(url)

        wait = WebDriverWait(driver,9999999999)
        wait.until(readings_populated)

        readings_json = driver.execute_script("return JSON.stringify(readings);")

        readings = json.loads(readings_json)

        print("Readings data extracted:")
        new_df = pd.DataFrame(readings)
        new_df.insert(0, 'station_id', param['station'])
        new_df = new_df.drop('QueryCnt', axis=1)
        df = pd.concat([df, new_df], ignore_index=True)
        print(df)
        # df.to_csv('waterlevels.csv', index=False)

    except TimeoutException:
        print("Timed out waiting for readings to populate")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
