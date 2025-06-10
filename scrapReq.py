import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import pandas as pd
import ssl
from requests.adapters import HTTPAdapter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
import os
from datetime import datetime
from datetime import datetime, timedelta


class UnsafeTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE 
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
session.mount("https://", UnsafeTLSAdapter(max_retries=retries))

params = {
#    'station': ['3317004_','26409', '26419', '27370', '27371', '3117082_', '3117180_', '3216001_', '3216005_', '3217001_', '3217002_','3217003_', 
#                '3217004_', '3117003_', '3217117_', '3217117_', '240901410223', '241101361117', '244201011017', '244401290318', '244903240721', '26380', 
#                '26383', '26400', '26521', '26531', '27553', '27710', 'JPSA0001', ],
    'station': ['27233','27234','3013003_', '3014080_','3015084_','3015089_', 'DESAKEMUNING', 'PANDAMARAN', 'PEKANMERU', 'SELATMUARA', '26558'],
    'from': '02/03/2024%2000:00',
    'to': '09/06/2025%2022:00',
    'datafreq': '60'
}

def getWL():
    if os.path.exists('klangWL.csv') and os.path.getsize('klangWL.csv') > 0:
        df = pd.read_csv('klangWL.csv')
    else:
        df = pd.DataFrame()

    print("Initial DataFrame loaded with shape:", df)

    try:
        unique_ids = df["station_id"].unique()
    except KeyError:
        unique_ids = []
    print("Unique station IDs in DataFrame:", unique_ids)

    for station in params['station']:
        if station in unique_ids:
            print(f"Skipping {station}, already exists in the DataFrame.")
            continue
        else:
            url = f"https://publicinfobanjir.water.gov.my/wp-content/themes/enlighten/query/searchresultwaterleveldtlead.php?station={station}&from={params['from']}&to={params['to']}&datafreq={params['datafreq']}"

            urllib3.disable_warnings(InsecureRequestWarning)
            response = session.get(url, verify=False)
            print("Status:", response.status_code)
            
            try:
                data = response.json()
                print("Parsed JSON:", data["info"])
                new_df = pd.DataFrame(data["values"])
                print("New DataFrame created with values:\n", new_df)
                new_df.insert(0, 'station_id', station)
                new_df.insert(1, 'station_name', data["info"]["name"])
                new_df.insert(5, 'normal', data["info"]["normal"])
                new_df.insert(6, 'alert', data["info"]["alert"])
                new_df.insert(7, 'warning', data["info"]["warning"])
                new_df.insert(8, 'danger', data["info"]["danger"])
                df = pd.concat([df, new_df], ignore_index=True)
                print(df)
            except ValueError:
                print("Response not JSON:\n", response.text)
            finally:
                df.to_csv('klangWL.csv', index=False)

def getRF():
    start_date = datetime.strptime("02/03/2024", "%d/%m/%Y")
    end_date = datetime.strptime("09/06/2025", "%d/%m/%Y")

    if os.path.exists('klangWL.csv') and os.path.getsize('klangWL.csv') > 0:
        df = pd.read_csv('klangWL.csv')
    else:
        df = pd.DataFrame()

    print("WL DataFrame loaded with shape:\n", df)

    try:
        station_ids = df["station_id"].unique()
    except KeyError:
        station_ids = []
    print("Station IDs:", station_ids)

    if os.path.exists('klangRF.csv') and os.path.getsize('klangRF.csv') > 0:
        df = pd.read_csv('klangRF.csv')
    else:
        df = pd.DataFrame()

    print("Initial DataFrame loaded with shape:\n", df)

    try:
        unique_ids = df["station_id"].unique()
    except KeyError:
        unique_ids = []
    print("Unique station IDs in DataFrame:", unique_ids)

    for station in params['station']:
        if station in unique_ids:
            print(f"Skipping {station}, already exists in the DataFrame.")
            continue
        else:
            date_list = []
            current_date = start_date

            while current_date <= end_date:
                formatted_date = current_date.strftime("%d/%m/%Y")
                date_list.append(formatted_date)
                current_date += timedelta(days=1)

            start_date_str = start_date.strftime("%d/%m/%Y")+ "%2000:00"
            for d in date_list:
                end_date_str = d + "%2000:00"
                now = datetime.now()
                url = f"https://publicinfobanjir.water.gov.my/wp-content/themes/enlighten/query/searchresultrainfalldthourlylead.php?station={station}&from={start_date_str}&to={end_date_str}&datafreq={params['datafreq']}"

                urllib3.disable_warnings(InsecureRequestWarning)
                response = session.get(url, verify=False)
                print("Status:", response.status_code)
                
                try:
                    data = response.json()
                    print("Parsed JSON:", data["info"])
                    new_df = pd.DataFrame(data["values"])
                    print("New DataFrame created with values:\n", new_df)
                    new_df.insert(0, 'station_id', station)
                    new_df.insert(1, 'station_name', data["info"]["name"])
                    new_df.insert(10, 'light', data["info"]["light"])
                    new_df.insert(11, 'moderate', data["info"]["moderate"])
                    new_df.insert(12, 'heavy', data["info"]["heavy"])
                    new_df.insert(13, 'veryheavy', data["info"]["veryheavy"])
                    df = pd.concat([df, new_df], ignore_index=True)
                    print(df)
                except ValueError:
                    print("Response not JSON")
                finally:
                    df.to_csv('klangRF.csv', index=False)
                    difference = datetime.now() - now
                    print(f"Time taken for {station}: {difference.total_seconds()} seconds")
                start_date_str = end_date_str.replace("00:00", "00:01")  



if __name__ == "__main__":
    getRF()
    session.close()
    print("Session closed.")

    
