from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔴 YEH LINE ADD KAREIN: Is se order wahi rahega jo humne likha hai
app.config['JSON_SORT_KEYS'] = False 

@app.route('/')
def get_data():
    pair = request.args.get('pair', request.args.get('pairs', 'USDINR_OTC')).upper()
    count = request.args.get('count', '100')

    if not pair.endswith('_OTC'):
        api_pair = f"{pair}_OTC"
    else:
        api_pair = pair

    external_url = f"https://zentraapi.site/api/Qx.php?pair={api_pair}&timeframe=M1&count={count}"

    try:
        response = requests.get(external_url, timeout=10)
        data = response.json()

        # Ab order wahi aayega jo yahan likha hai
        return jsonify({
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+6",
            "market": api_pair,
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(data),
            "data": data
        })

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
