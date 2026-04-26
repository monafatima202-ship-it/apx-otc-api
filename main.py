from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_data():
    # 1. User se pair aur candles ki tadad lena
    pair = request.args.get('pair', request.args.get('pairs', 'USDINR_OTC')).upper()
    count = request.args.get('count', '100') # Default 100 candles

    # 2. External API ka URL (Binding the link you found)
    # Note: Humein pair ke sath '_otc' lagana hoga agar user ne nahi lagaya
    if not pair.endswith('_OTC'):
        api_pair = f"{pair}_OTC"
    else:
        api_pair = pair

    external_url = f"https://zentraapi.site/api/Qx.php?pair={api_pair}&timeframe=M1&count={count}"

    try:
        # 3. Data fetch karna
        response = requests.get(external_url, timeout=10)
        data = response.json()

        # 4. Asli data wapas bhej dena
        return jsonify({
            "developer": "@MMQUOBOT",
            "market": api_pair,
            "status": "100%_REAL_DATA_FETCHED",
            "total_candles": len(data),
            "data": data
        })

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": f"Could not fetch data: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
