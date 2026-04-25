const express = require('express');
const WebSocket = require('ws');
const app = express();
const port = process.env.PORT || 3000;

let liveData = {
  price: "0.00000",
  time: ""
};

// Quotex Connection
function connectQuotex() {
    const ws = new WebSocket('wss://ws2.market-qx.trade/socket.io/?EIO=3&transport=websocket', {
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Origin': 'https://market-qx.trade'
        },
        rejectUnauthorized: false
    });

    ws.on('open', () => {
        console.log("✅ Quotex Connected!");
        ws.send('40');
    });

    ws.on('message', (data) => {
        const message = data.toString();
        const match = message.match(/[\[:,]\s*(\d+\.\d{3,6})\b/);
        if (match) {
            const price = parseFloat(match[1]);
            if(price < 200000) { 
                liveData.price = price.toString();
            }
        }
        if(message === '2') ws.send('3');
    });

    ws.on('error', (err) => console.error("⚠️ Error: ", err.message));
    ws.on('close', () => setTimeout(connectQuotex, 3000));
}

connectQuotex();

// API Endpoint (100 Candles History Generator)
app.get('/', (req, res) => {
    const pair = req.query.pairs || "OTC_MARKET";
    let basePrice = parseFloat(liveData.price) || 100.0000;
    
    let historyCandles = [];
    
    // Pichli 100 candles banane ka loop (Taa ke bot JSON read kar sake)
    for (let i = 99; i >= 0; i--) {
        let candleTime = new Date(Date.now() - (i * 60000)); // Har candle 1 minute purani
        let timeString = `${candleTime.getFullYear()}-${String(candleTime.getMonth() + 1).padStart(2, '0')}-${String(candleTime.getDate()).padStart(2, '0')} ${String(candleTime.getHours()).padStart(2, '0')}:${String(candleTime.getMinutes()).padStart(2, '0')}:00 — +05:00 🇵🇰`;

        if (i === 0) {
            // Aakhri (0) candle Live Candle hogi
            historyCandles.push({
                time: timeString,
                open: basePrice.toFixed(5),
                high: (basePrice + 0.00010).toFixed(5),
                low: (basePrice - 0.00010).toFixed(5),
                close: basePrice.toFixed(5),
                color: "Green",
                volume: Math.floor(Math.random() * 1000) + 500
            });
        } else {
            // Pichli 99 candles ka data (Bot testing ke liye)
            let o = basePrice + ((Math.random() - 0.5) * 0.0050);
            let c = o + ((Math.random() - 0.5) * 0.0050);
            let h = Math.max(o, c) + (Math.random() * 0.0020);
            let l = Math.min(o, c) - (Math.random() * 0.0020);
            
            historyCandles.push({
                time: timeString,
                open: o.toFixed(5),
                high: h.toFixed(5),
                low: l.toFixed(5),
                close: c.toFixed(5),
                color: c >= o ? "Green" : "Red",
                volume: Math.floor(Math.random() * 1000) + 500
            });
        }
    }

    const responseData = {
      developer: "@MMQUOBOT",
      telegram: "https://t.me/vectabot1",
      market: pair.toUpperCase(),
      data: historyCandles // Yahan 100 candles ka poora array bhej diya
    };

    res.json(responseData);
});

app.listen(port, () => {
    console.log(`🚀 API is running on port ${port}`);
});
