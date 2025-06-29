import requests
from bs4 import BeautifulSoup
import random

# 模擬：實際應該用 headless browser or API，這裡先回傳假資料
def search_flights(origin, destination, months=2):
    # 模擬資料（實際版本將用爬蟲或快取查詢）
    traditional_airlines = ['華航', '長榮航空', '星宇航空', '全日空', '日航']
    lowcost_airlines = ['虎航', '樂桃航空', '捷星', '香草航空']

    def gen_flight(airline_list):
        flights = []
        for name in airline_list:
            flights.append({
                'airline': name,
                'price': random.randint(4500, 7800),
                'depart_date': f'07/{random.randint(5,25)}',
                'direct': random.choice([True, False])
            })
        flights = sorted(flights, key=lambda x: x['price'])[:3]
        return flights

    return {
        'traditional': gen_flight(traditional_airlines),
        'lowcost': gen_flight(lowcost_airlines)
    }

def format_flights(data):
    lines = []

    lines.append("🎫 傳統航空（前三便宜）")
    for idx, f in enumerate(data['traditional'], 1):
        lines.append(f"{idx}. {f['airline']} ${f['price']}｜{f['depart_date']} 出發｜{'直飛' if f['direct'] else '轉機'}")

    lines.append("\n🧳 廉價航空（前三便宜）")
    for idx, f in enumerate(data['lowcost'], 1):
        lines.append(f"{idx}. {f['airline']} ${f['price']}｜{f['depart_date']} 出發｜{'直飛' if f['direct'] else '轉機'}")

    return '\n'.join(lines)
