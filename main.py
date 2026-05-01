from flask import Flask, request, Response
import json
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# Retry Logic setup (Agar timeout ho toh 3 baar khud koshish karega)
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

@app.route('/')
def get_data():
    pair_param = request.args.get('pair', request.args.get('pairs', 'USDINR_otc'))
    pair = pair_param.lower() 

    # Stable Source URL
    external_url = f"https://qbtxpoghen-candeldata.poghen.workers.dev/?pairs={pair}"

    try:
        # Timeout ko 15s se barha kar 30s kar diya hai
        response = session.get(external_url, timeout=30)
        json_resp = response.json()

        if isinstance(json_resp, list):
            actual_candles = json_resp
        else:
            actual_candles = json_resp.get('data', json_resp.get('candles', []))

        custom_response = {
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+6",
            "market": pair.upper(),
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(actual_candles),
            "data": actual_candles 
        }

        return Response(json.dumps(custom_response, indent=4), mimetype='application/json')

    except requests.exceptions.Timeout:
        return Response(json.dumps({"status": "ERROR", "message": "Source server is too slow (Timeout)"}), mimetype='application/json', status=504)
    except Exception as e:
        return Response(json.dumps({"status": "ERROR", "message": str(e)}), mimetype='application/json', status=500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
