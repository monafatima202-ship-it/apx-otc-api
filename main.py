from flask import Flask, request, Response
import json
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# Retry and Timeout settings
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def convert_to_utc5(time_str):
    """BD (+06:00) time ko PK (+05:00) mein convert karna"""
    try:
        # Time string se raw date aur time nikalna: "2026-05-01 03:00:00"
        clean_time_str = time_str.split(' \u2014 ')[0]
        
        # BD Time format: "%Y-%m-%d %H:%M:%S"
        bd_time = datetime.strptime(clean_time_str, "%Y-%m-%d %H:%M:%S")
        
        # 1 ghanta piche karna (BD 03:00 -> PK 02:00)
        pk_time = bd_time - timedelta(hours=1)
        
        # Pakistan Waving Flag effect
        pak_flag_waving = "🇵🇰👋" # Static flag with movement emoji
        
        return pk_time.strftime(f"%Y-%m-%d %H:%M:%S — +05:00 {pak_flag_waving}")
    except Exception:
        return time_str # Agar fail ho to asli time hi bhej do

@app.route('/')
def get_data():
    pair_param = request.args.get('pair', request.args.get('pairs', 'USDINR_otc'))
    pair = pair_param.lower() 

    external_url = f"https://qbtxpoghen-candeldata.poghen.workers.dev/?pairs={pair}"

    try:
        response = session.get(external_url, timeout=30)
        json_resp = response.json()

        if isinstance(json_resp, list):
            raw_candles = json_resp
        else:
            raw_candles = json_resp.get('data', json_resp.get('candles', []))

        # --- PROCESS CANDLES (Time Conversion) ---
        processed_candles = []
        for candle in raw_candles:
            new_candle = candle.copy()
            if 'time' in new_candle:
                # BD time ko PK time mein badalna aur Pakistani Flag lagana
                new_candle['time'] = convert_to_utc5(new_candle['time'])
            processed_candles.append(new_candle)

        custom_response = {
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+5", # PK Timezone
            "market": pair.upper(),
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(processed_candles),
            "data": processed_candles 
        }

        # ensure_ascii=False ensures emojis appear correctly
        final_json = json.dumps(custom_response, indent=4, ensure_ascii=False)
        return Response(final_json, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"status": "ERROR", "message": str(e)}), mimetype='application/json', status=500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
