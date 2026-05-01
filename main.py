from flask import Flask, request, Response
import json
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_data():
    # Pair parameters handle karna (USDPKR_otc etc)
    pair_param = request.args.get('pair', request.args.get('pairs', 'USDINR_otc'))
    # Is API ke liye lowercase ya uppercase dono chalte hain, lekin hum standardize rakhenge
    pair = pair_param.lower() 

    # --- NAYA STABLE SOURCE ---
    external_url = f"https://qbtxpoghen-candeldata.poghen.workers.dev/?pairs={pair}"

    try:
        response = requests.get(external_url, timeout=15)
        json_resp = response.json()

        # Is API ka data direct list mein hota hai ya 'data' key mein
        if isinstance(json_resp, list):
            actual_candles = json_resp
        else:
            actual_candles = json_resp.get('data', json_resp.get('candles', []))

        # --- AAPKA PURANA FORMAT (Wahi details jo aapne mangi thin) ---
        custom_response = {
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+6",
            "market": pair.upper(),
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(actual_candles),
            "data": actual_candles  # Bot is 'data' key se candles read karega
        }

        final_json = json.dumps(custom_response, indent=4)
        return Response(final_json, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"status": "ERROR", "message": str(e)}), mimetype='application/json', status=500)

if __name__ == '__main__':
    # Railway settings ke mutabiq port set karna
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
