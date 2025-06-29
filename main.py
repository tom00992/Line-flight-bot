import os, re
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from flight_scraper import search_flights, format_flights

load_dotenv()
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    reply = ""

    if text == "好想出國":
        origin = "台北"
        destinations = ["東京", "大阪", "北海道", "沖繩", "名古屋"]
        for city in destinations:
            res = search_flights(origin, city, 2025, 7)
            if res:
                reply += format_flights(res, origin, city, 2025, 7) + "\n\n"
            else:
                reply += f"{origin} → {city} 查無資料\n\n"

    elif re.match(r"\d{6}", text):
        year = int(text[:4])
        month = int(text[4:6])
        dest = text[6:]
        origin = "台北"
        res = search_flights(origin, dest, year, month)
        if res:
            reply = format_flights(res, origin, dest, year, month)
        else:
            reply = "⚠️ 無法查詢該目的地，請再確認城市名稱。"

    elif "到" in text and "內" in text:
        origin = "台北"
        dest = text.split("到")[-1]
        res = search_flights(origin, dest, 2025, 7)
        if res:
            reply = format_flights(res, origin, dest, 2025, 7)
        else:
            reply = "⚠️ 查詢失敗，請再試一次或確認輸入格式"

    else:
        reply = "請輸入關鍵字，例如：\n• 好想出國\n• 半年內台北到東京\n• 202601東京"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
