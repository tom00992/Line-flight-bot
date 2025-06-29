from amadeus_search import search_flights_amadeus

TRADITIONAL_AIRLINES = ["CI", "BR", "JX", "JL", "NH"]
LOWCOST_AIRLINES = ["IT", "GK", "JW", "MM", "7C", "VZ", "TZ", "TR"]

CITY_CODES = {
    "台北": "TPE",
    "東京": "TYO",
    "大阪": "OSA",
    "沖繩": "OKA",
    "北海道": "CTS",
    "名古屋": "NGO",
    "鳥取": "TTJ"
}

def classify_airline(iata_code):
    if iata_code in TRADITIONAL_AIRLINES:
        return "traditional"
    else:
        return "lowcost"

def search_flights(origin_city, dest_city, year, month):
    origin = CITY_CODES.get(origin_city)
    destination = CITY_CODES.get(dest_city)
    if not origin or not destination:
        return None

    results = {"traditional": [], "lowcost": []}
    for day in ["05", "10", "15", "20", "25"]:
        date_str = f"{year}-{month:02d}-{day}"
        flights = search_flights_amadeus(origin, destination, date_str)
        for f in flights:
            category = classify_airline(f["airline"])
            results[category].append(f)

    for k in results:
        results[k] = sorted(results[k], key=lambda x: x["price"])[:3]
    return results

def format_flights(result, origin_city, dest_city, year=None, month=None):
    lines = [f"📍 查詢 {origin_city} → {dest_city}："]
    if year and month:
        lines.append(f"出發月份：{year} 年 {month:02d} 月")

    lines.append("🎫 傳統航空（前三便宜）")
    if result["traditional"]:
        for i, f in enumerate(result["traditional"], 1):
            lines.append(f"{i}. {f['airline']} ${f['price']}｜{f['depart_time'][5:10]} → {f['arrive_time'][5:10]}｜{'直飛' if f['direct'] else '轉機'}")
    else:
        lines.append("查無航班")

    lines.append("\n🧳 廉價航空（前三便宜）")
    if result["lowcost"]:
        for i, f in enumerate(result["lowcost"], 1):
            lines.append(f"{i}. {f['airline']} ${f['price']}｜{f['depart_time'][5:10]} → {f['arrive_time'][5:10]}｜{'直飛' if f['direct'] else '轉機'}")
    else:
        lines.append("查無航班")

    return '\n'.join(lines)
