Const express = require('express');
const WebSocket = require('ws');
const app = express();
const port = process.env.PORT || 3000;

// Yeh variable live price store karega
let liveData = {
  price: "Connecting...",
  time: ""
};

// Quotex ke WebSocket se 24/7 connection banayein
function connectQuotex() {
    const ws = new WebSocket('wss://ws2.market-qx.trade/socket.io/?EIO=3&transport=websocket', {
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Origin': 'https://market-qx.trade'
        },
        rejectUnauthorized: false // <--- YEH LINE SSL ERROR KO FIX KAREGI
    });

    ws.on('open', () => {
        console.log("✅ Quotex Server Se Connect Ho Gaya!");
        ws.send('40'); // Socket.io Handshake
    });

    ws.on('message', (data) => {
        const message = data.toString();
        
        // Data pakarne ka logic
        const match = message.match(/[\[:,]\s*(\d+\.\d{3,6})\b/);
        if (match) {
            const price = parseFloat(match[1]);
            if(price < 200000) { // Timestamp ko block karne ke liye filter
                liveData.price = price.toString();
                
                const now = new Date();
                liveData.time = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:00 — +05:00 🇵🇰`;
            }
        }
        
        // Heartbeat
        if(message === '2') {
            ws.send('3');
        }
    });

    // Error aane par server crash hone se bachane ke liye
    ws.on('error', (err) => {
        console.error("⚠️ WebSocket Error: ", err.message);
    });

    ws.on('close', () => {
        console.log("⚠️ Connection toota, 3 second me dobara connect kar raha hoon...");
        setTimeout(connectQuotex, 3000);
    });
}

// Server start hote hi piche Quotex se connect ho jao
connectQuotex();

// Jab koi API link khole toh usay current live data de do
app.get('/', (req, res) => {
    const pair = req.query.pairs || "OTC_MARKET";
    
    const responseData = {
      developer: "@MMQUOBOT",
      telegram: "https://t.me/vectabot1 ",
      market: pair.toUpperCase(),
      data: [
        {
          time: liveData.time,
          open: liveData.price,
          high: liveData.price,
          low: liveData.price,
          close: liveData.price,
          color: "Green", 
          volume: Math.floor(Math.random() * 1000) + 500 // Dummy volume
        }
      ]
    };

    res.json(responseData);
});

app.listen(port, () => {
    console.log(`🚀 API is running on port ${port}`);
});


