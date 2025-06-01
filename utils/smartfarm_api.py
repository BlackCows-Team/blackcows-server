# utils/smartfarm_api.py

import requests

def fetch_cows_from_api(farm_id: str):
    url = f"https://www.smartfarmkorea.net/openapi/...?farmId={farm_id}&ServiceKey=당신의API키"
    res = requests.get(url)
    return res.json()
