import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from flight_scraper import search_flights, format_flights

# 載入 .env
load_dotenv()
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 初始化 LINE
line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 初始化 Flask
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

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    print(f"[DEBUG] 使用者傳來的訊息：{text}")

    reply = ""

    # 關鍵字2：「好想出國」
    if '好想出國' in text:
        origin = '台北'
        destinations = ['東京', '大阪', '北海道', '沖繩', '名古屋']
        reply = "📢 為你查詢未來兩個月內從台北出發的日本城市機票：\n"

        for dest in destinations:
            result = search_flights(origin, dest)
            section = f"\n📍 台北 → {dest}\n" + format_flights(result)
            reply += section

    # 關鍵字3：「202601沖繩」這類年月查詢
    elif len(text) > 6 and text[:6].isdigit():
        print(f"[DEBUG] 偵測到年月格式查詢：{text}")
        try:
            year = text[:4]
            month = text[4:6]
            destination = text[6:].strip()
            origin = '台北'
            result = search_flights(origin, destination, year, month)
            reply = f"📍 查詢 {origin} → {destination}：\n出發月份：{year} 年 {month} 月\n" + format_flights(result)
        except Exception as e:
            print(f"[ERROR] 查詢年月格式失敗：{e}")
            reply = "⚠️ 無法解析你輸入的時間與地點，請再確認格式是否為『YYYYMM目的地』"

    # 關鍵字1：「半年內台北到東京」
    elif '到' in text:
        try:
            parts = text.replace('內', '').replace('月內', '').split('到')
            time_range = parts[0].strip()
            location = parts[1].strip()
            origin = '台北'
            result = search_flights(origin, location)
            reply = f"📍 查詢 {origin} → {location}：\n" + format_flights(result)
        except Exception as e:
            print(f"[ERROR] 關鍵字1解析錯誤：{e}")
            reply = "⚠️ 無法解析你的目的地，請再確認輸入格式。"

    else:
        reply = ("請輸入關鍵字，例如：\n"
                 "•『好想出國』\n"
                 "•『半年內台北到東京』\n"
                 "•『202601沖繩』")

    # 回覆使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# 啟動伺服器
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
