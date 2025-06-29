import os
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

    print(f"使用者傳來的訊息：{text}")
   
    reply = ""

    if '好想出國' in text:
        origin, dest = '台北', '日本'
        result = search_flights(origin, dest)
        reply = format_flights(result)

    elif '到' in text:
        # 簡單解析：半年內台北到東京
        try:
            parts = text.replace('內', '').replace('月內', '').split('到')
            time_range = parts[0].strip()  # e.g., 半年
            location = parts[1].strip()    # e.g., 東京
            origin = '台北'
            result = search_flights(origin, location)
            reply = f"📍 查詢 {origin} → {location}：\n" + format_flights(result)
        except:
            reply = "⚠️ 無法解析你的目的地，請再確認輸入格式。"

    else:
        reply = ("請輸入關鍵字，例如：\n"
                 "•『好想出國』\n"
                 "•『半年內台北到東京』")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
