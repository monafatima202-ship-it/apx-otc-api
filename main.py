from flask import Flask, request, Response
import json
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_data():
    pair_param = request.args.get('pair', request.args.get('pairs', 'USDINR_OTC'))
    pair = pair_param.upper()
    count = request.args.get('count', '100')

    if not pair.endswith('_OTC'):
        api_pair = f"{pair}_OTC"
    else:
        api_pair = pair

    external_url = f"https://zentraapi.site/api/Qx.php?pair={api_pair}&timeframe=M1&count={count}"

    try:
        response = requests.get(external_url, timeout=15)
        json_resp = response.json()

        # --- CLEANING PROCESS ---
        # Sirf asli candles nikalna (baqi developer details chor dena)
        actual_candles = json_resp.get('data', [])
        
        # Agar data list ke bajaye dictionary hai, toh usko handle karna
        if isinstance(actual_candles, dict):
            # Kuch APIs data key ke andar mazeed nested hoti hain
            actual_candles = list(actual_candles.values())

        custom_response = {
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+6",
            "market": api_pair,
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(actual_candles),
            "data": actual_candles  # Yahan ab sirf candles aayengi, unka naam nahi
        }

        final_json = json.dumps(custom_response, indent=4)
        return Response(final_json, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"status": "ERROR", "message": str(e)}), mimetype='application/json', status=500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
