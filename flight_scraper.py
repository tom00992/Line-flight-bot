import random

# 城市對應 Skyscanner 的機場代碼
CITY_TO_CODE = {
    '東京': 'tyoa',
    '大阪': 'osa',
    '北海道': 'spka',
    '沖繩': 'okaa',
    '名古屋': 'ngoa',
    '鳥取': 'ttj',
}

# 查票主函式（目前模擬資料）
def search_flights(origin, destination, year=None, month=None):
    city_code = CITY_TO_CODE.get(destination)
    if not city_code:
        raise ValueError(f"找不到目的地代碼：{destination}")

    traditional_airlines = ['華航', '長榮航空', '星宇航空', '全日空', '日航']
    lowcost_airlines = ['虎航', '樂桃航空', '捷星', '香草航空']

    def gen_mock(airline_list):
        flights = []
        for name in airline_list:
            flights.append({
                'airline': name,
                'price': random.randint(4500, 7800),
                'depart_date': f"{month}/{random.randint(1, 28)}" if month else f"07/{random.randint(5,25)}",
                'direct': random.choice([True, False])
            })
        return sorted(flights, key=lambda x: x['price'])[:3]

    return {
        'traditional': gen_mock(traditional_airlines),
        'lowcost': gen_mock(lowcost_airlines)
    }

# 格式化輸出
def format_flights(data):
    lines = []

    if 'error' in data:
        return data['error']

    lines.append("🎫 傳統航空（前三便宜）")
    for idx, f in enumerate(data['traditional'], 1):
        lines.append(f"{idx}. {f['airline']} ${f['price']}｜{f['depart_date']} 出發｜{'直飛' if f['direct'] else '轉機'}")

    lines.append("\n🧳 廉價航空（前三便宜）")
    for idx, f in enumerate(data['lowcost'], 1):
        lines.append(f"{idx}. {f['airline']} ${f['price']}｜{f['depart_date']} 出發｜{'直飛' if f['direct'] else '轉機'}")

    return '\n'.join(lines)
