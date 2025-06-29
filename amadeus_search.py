import requests

API_KEY = "GfIGAnG2Ibq5yzHA1GF6NwLZn813VAFn"
API_SECRET = "AXFkt56k1vjGMGRF"
TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }
    response = requests.post(TOKEN_URL, data=payload)
    return response.json().get("access_token")

def search_flights_amadeus(origin, destination, date_str):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date_str,
        "adults": 1,
        "currencyCode": "TWD",
        "max": 10
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    if response.status_code != 200:
        print("Amadeus API error:", response.json())
        return []

    results = []
    for offer in response.json().get("data", []):
        segments = offer["itineraries"][0]["segments"]
        airline = segments[0]["carrierCode"]
        price = int(float(offer["price"]["total"]))
        depart = segments[0]["departure"]["at"]
        arrive = segments[-1]["arrival"]["at"]
        is_direct = len(segments) == 1
        results.append({
            "airline": airline,
            "price": price,
            "depart_time": depart,
            "arrive_time": arrive,
            "direct": is_direct
        })

    return sorted(results, key=lambda x: x["price"])[:3]
