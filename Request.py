import requests

url = "https://publicinfobanjir.water.gov.my/wl-graph/?stationid=3216005_&datefrom=01/12/2024%2022:00&dateto=12/06/2025%2022:00&ymax=&ymin=&xfreq=6&datafreq=60&lang=en"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers, verify=False)
print(response.text)
