import requests
from bs4 import BeautifulSoup
from datetime import datetime

CITY_TO_CODE = {
    '東京': 'tyoa',
    '大阪': 'osa',
    '北海道': 'spka',
    '沖繩': 'okaa',
    '名古屋': 'ngoa',
    '鳥取': 'ttj',
}

def search_flights(origin, destination, year=None, month=None):
    city_code = CITY_TO_CODE.get(destination)
    if not city_code:
        return {'error': f"找不到目的地代碼：{destination}"}

    # 台北的 Skyscanner 代碼固定用 tpet
    url = f"https://www.skyscanner.com.tw/transport/flights/tpet/{city_code}/{str(year)[2:]}{str(month).zfill(2)}/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Skyscanner 的月曆票價在某些版本會嵌入 script/json，這裡我們以 fallback 處理
        # 我們先簡單從網頁中抓最低票價區塊
        prices = []

        for span in soup.find_all("span"):
            text = span.get_text().replace(",", "").replace("NT$", "").strip()
            if text.isdigit() and 2000 < int(text) < 20000:
                prices.append(int(text))

        prices = sorted(set(prices))[:3]  # 取前三個最低票價

        flights = [{
            'airline': '不明',
            'price': p,
            'depart_date': f"{month}/{10 + i*3}",  # 模擬出發日
            'direct': True  # 預設為直飛
        } for i, p in enumerate(prices)]

        return {
            'traditional': flights,
            'lowcost': []
        }

    except Exception as e:
        print(f"[ERROR] 查詢 Skyscanner 錯誤: {e}")
        return {'error': '⚠️ 無法查詢票價，可能是 Skyscanner 格式變動或網頁阻擋。'}
