import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import pandas as pd

params = {
    'station': '3216005_',
    'from': '01/03/2024%2022:00',
    'to': '08/06/2025%2022:00',
    'datafreq': '60'
}
url = f"https://publicinfobanjir.water.gov.my/wp-content/themes/enlighten/query/searchresultwaterleveldtlead.php?station={params['station']}&from={params['from']}&to={params['to']}&datafreq={params['datafreq']}"


urllib3.disable_warnings(InsecureRequestWarning)
response = requests.get(url, verify=False)
print("Status:", response.status_code)
df = pd.DataFrame()
try:
    data = response.json()
    print("Parsed JSON:", data["info"])
    new_df = pd.DataFrame(data["values"])
    new_df.insert(0, 'station_id', params['station'])
    new_df.insert(1, 'station_name', data["info"]["name"])
    new_df.insert(5, 'normal', data["info"]["normal"])
    new_df.insert(6, 'alert', data["info"]["alert"])
    new_df.insert(7, 'warning', data["info"]["warning"])
    new_df.insert(8, 'danger', data["info"]["danger"])
    df = pd.concat([df, new_df], ignore_index=True)
    print(df)
    df.to_csv('waterlevels.csv', index=False)
except ValueError:
    print("Response not JSON:\n", response.text)
