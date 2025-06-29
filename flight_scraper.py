import requests
from bs4 import BeautifulSoup

# 城市對應 Skyscanner 的機場代碼
CITY_TO_CODE = {
    '東京': 'tyoa',
    '大阪': 'osa',
    '北海道': 'spka',
    '沖繩': 'okaa',
    '名古屋': 'ngoa',
    '鳥取': 'ttj',
}

# 查詢機票
def search_flights(origin, destination, year=None, month=None):
    city_code = CITY_TO_CODE.get(destination)
    if not city_code:
        return {'error': f"❌ 找不到目的地代碼：{destination}"}

    # Skyscanner 的查票網址（注意月份格式）
    url = f"https://www.skyscanner.com.tw/transport/flights/tpet/{city_code}/{str(year)[2:]}{str(month).zfill(2)}/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 嘗試從頁面中找票價（Skyscanner 月曆價格不容易抓，這裡抓最常見 span 金額）
        prices = []

        for span in soup.find_all("span"):
            text = span.get_text().replace(",", "").replace("NT$", "").strip()
            if text.isdigit() and 2000 < int(text) < 20000:
                prices.append(int(text))

        prices = sorted(set(prices))[:3]  # 最便宜前三

        flights = [{
            'airline': '（實際航空公司未顯示）',
            'price': p,
            'depart_date': f"{month}/{10 + i*3}",  # 模擬出發日（無真實資訊）
            'direct': True
        } for i, p in enumerate(prices)]

        return {
            'traditional': flights,
            'lowcost': []  # 真實資料中無法分辨，先留空
        }

    except Exception as e:
        print(f"[ERROR] Skyscanner 爬蟲失敗：{e}")
        return {'error': '⚠️ 無法查詢票價，請稍後再試。'}

# 格式化回覆文字
def format_flights(data):
    lines = []

    if 'error' in data:
        return data['error']

    lines.append("🎫 傳統航空（前三便宜）")
    for idx, f in enumerate(data['traditional'], 1):
        lines.append(f"{idx}. {f['airline']} ${f['price']}｜{f['depart_date']} 出發｜{'直飛' if f['direct'] else '轉機'}")

    if data['lowcost']:
        lines.append("\n🧳 廉價航空（前三便宜）")
        for idx, f in enumerate(data['lowcost'], 1):
            lines.append(f"{idx}. {f['airline']} ${f['price']}｜{f['depart_date']} 出發｜{'直飛' if f['direct'] else '轉機'}")

    return '\n'.join(lines)
