from flask import Flask, request, Response
import json
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_data():
    # 1. User se pair aur candles ki tadad lena
    pair_param = request.args.get('pair', request.args.get('pairs', 'USDINR_OTC'))
    pair = pair_param.upper()
    
    # Default count 100 agar user ne kuch na likha ho
    count = request.args.get('count', '100')

    # 2. Pair name format check karna (_OTC lazmi hai)
    if not pair.endswith('_OTC'):
        api_pair = f"{pair}_OTC"
    else:
        api_pair = pair

    # 3. Zentra API Binding
    external_url = f"https://zentraapi.site/api/Qx.php?pair={api_pair}&timeframe=M1&count={count}"

    try:
        # Data fetch karna
        response = requests.get(external_url, timeout=15)
        json_resp = response.json()

        # 4. Candles ki sahi tadad (Count) nikalna
        # Zentra API ke andar 'data' key mein asli candles ki list hoti hai
        actual_candles_list = json_resp.get('data', [])
        total_count = len(actual_candles_list)

        # 5. --- APX PREMIUM BRANDING & STRICT ORDER ---
        custom_response = {
            "powered_by": "APX Premium",
            "channel_name": "@MMQUOBOT",
            "telegram_bot": "https://t.me/vectabot1",
            "timezone": "UTC+6",
            "market": api_pair,
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": total_count,
            "data": json_resp
        }

        # JSON ko beautify karke aur order maintain karke bhejba
        final_json = json.dumps(custom_response, indent=4)
        return Response(final_json, mimetype='application/json')

    except Exception as e:
        error_data = {
            "powered_by": "APX Premium",
            "status": "ERROR",
            "message": f"Connection Failed: {str(e)}"
        }
        return Response(json.dumps(error_data), mimetype='application/json', status=500)

if __name__ == '__main__':
    # Railway environment ke liye port setting
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
