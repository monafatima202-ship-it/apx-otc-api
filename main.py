from flask import Flask, request, jsonify
from pyquotex.stable_api import Quotex
import asyncio
import threading
import os

app = Flask(__name__)

# 🔴 YAHAN APNA QUOTEX DEMO ACCOUNT DAALEIN 🔴
QX_EMAIL = "your_demo_email@gmail.com" 
QX_PASSWORD = "your_demo_password"

client = Quotex(email=QX_EMAIL, password=QX_PASSWORD)
server_status = "INITIALIZING_ENGINE..."

# Yeh hamari memory hai jahan real candles save hongi
active_pairs = set(["USDINR_OTC"])
market_data = {}

async def quotex_background_engine():
    global server_status
    print("🚀 Connecting to Quotex Core Servers...")
    
    # 1. Quotex se connection banana
    check_connect, message = await client.connect()
    
    if check_connect:
        print("✅ 100% SUCCESS: Quotex Connected!")
        server_status = "100%_REAL_LIVE_DATA"
    else:
        print(f"⚠️ Login Failed: {message}")
        server_status = f"LOGIN_ERROR: {message}"

    # 2. Har 2 second baad asli candles mangwana
    while True:
        if check_connect:
            for pair in list(active_pairs):
                try:
                    # Direct Quotex se 1-Minute ki candles fetch karna!
                    candles = await client.get_candles(pair, 60)
                    if candles:
                        market_data[pair] = candles
                except Exception as e:
                    print(f"⚠️ Error fetching {pair}: {e}")
        
        await asyncio.sleep(2)

def start_engine():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(quotex_background_engine())

# Background engine shuru
threading.Thread(target=start_engine, daemon=True).start()

@app.route('/')
def get_data():
    pair = request.args.get('pair', request.args.get('pairs', 'USDINR_OTC')).upper()
    
    if pair not in active_pairs:
        active_pairs.add(pair)
        print(f"📡 Naya Pair Add Hua: {pair}")

    data = market_data.get(pair, [])
    current_status = "FETCHING_REAL_CANDLES... WAIT_5_SECONDS" if len(data) == 0 and "REAL" in server_status else server_status

    return jsonify({
        "developer": "@MMQUOBOT",
        "telegram": "https://t.me/vectabot1",
        "market": pair,
        "status": current_status,
        "total_candles": len(data),
        "data": data
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
