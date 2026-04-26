from flask import Flask, request, Response
import json
import requests
import os

app = Flask(__name__)

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

        # --- YAHAN HUM KHUD ORDER SET KAR RAHE HAIN (Strict Order) ---
        custom_response = {
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+6",
            "market": api_pair,
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(data),
            "data": data
        }

        # JSON ko text mein convert karke bhejenge taake browser order na chhere
        json_data = json.dumps(custom_response, indent=4)
        return Response(json_data, mimetype='application/json')

    except Exception as e:
        error_resp = json.dumps({"status": "ERROR", "message": str(e)})
        return Response(error_resp, mimetype='application/json', status=500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
