from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def get_market_data():
    # User se pair ka naam lena (Default: USDINR_OTC)
    pair = request.args.get('pairs', 'USDINR_OTC').upper()
    
    # Abhi hum basic server start kar rahe hain taake Railway Python par shift ho jaye.
    # Agle step mein hum Quotex library ka direct data yahan connect karenge.
    
    return jsonify({
        "developer": "@MMQUOBOT",
        "telegram": "https://t.me/vectabot1",
        "market": pair,
        "status": "PYTHON_SERVER_RUNNING",
        "message": "Railway has successfully switched to Python Engine! Ready for Quotex integration."
    })

if __name__ == '__main__':
    # Railway khud port assign karta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
