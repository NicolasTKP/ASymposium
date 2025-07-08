import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class UnsafeTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE 
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount("https://", UnsafeTLSAdapter())

url = "https://publicinfobanjir.water.gov.my/rf-graph/?stationid=3216001_&lang=en"
headers = {"User-Agent": "Mozilla/5.0"}

response = session.get(url, headers=headers, verify=False)
print(response.text)
