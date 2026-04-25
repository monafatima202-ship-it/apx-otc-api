const express = require('express');
const WebSocket = require('ws');
const app = express();
const port = process.env.PORT || 3000;

let rawQuotexPrice = null;

// Background WebSocket (Sirf connection zinda rakhne ke liye)
function connectQuotex() {
    const ws = new WebSocket('wss://ws2.market-qx.trade/socket.io/?EIO=3&transport=websocket', {
        headers: { 'User-Agent': 'Mozilla/5.0', 'Origin': 'https://market-qx.trade' },
        rejectUnauthorized: false
    });

    ws.on('open', () => { ws.send('40'); });
    ws.on('message', (data) => {
        const msg = data.toString();
        const match = msg.match(/[\[:,]\s*(\d+\.\d{3,6})\b/);
        if (match && parseFloat(match[1]) > 1) { 
            rawQuotexPrice = parseFloat(match[1]); 
        }
        if(msg === '2') ws.send('3');
    });
    ws.on('error', () => {});
    ws.on('close', () => setTimeout(connectQuotex, 3000));
}
connectQuotex();

// API Endpoint (100 Perfect Candles for Bot Testing)
app.get('/', (req, res) => {
    const pairParam = req.query.pairs || "USDMXN_OTC";
    const pair = pairParam.toUpperCase();
    
    // Pair ke hisaab se realistic price set karna (Taa ke bot theek kaam kare)
    let basePrice = 1.08500; // Default (EUR/USD jaisa)
    if (pair.includes("USDMXN")) basePrice = 19.89800;
    if (pair.includes("USDINR")) basePrice = 83.50000;
    if (pair.includes("JPY")) basePrice = 155.200;
    
    // Agar background se koi milti julti price aayi ho toh wo lelo
    if (rawQuotexPrice && Math.abs(rawQuotexPrice - basePrice) < 5) {
        basePrice = rawQuotexPrice;
    }

    let historyCandles = [];
    let currentCandlePrice = basePrice;
    
    // 100 Candles ka Loop (Perfect Math ke sath)
    for (let i = 99; i >= 0; i--) {
        let candleTime = new Date(Date.now() - (i * 60000));
        let timeString = `${candleTime.getFullYear()}-${String(candleTime.getMonth() + 1).padStart(2, '0')}-${String(candleTime.getDate()).padStart(2, '0')} ${String(candleTime.getHours()).padStart(2, '0')}:${String(candleTime.getMinutes()).padStart(2, '0')}:00 — +05:00 🇵🇰`;

        // Price variation logic (Market ki tarah random movement)
        let volatility = currentCandlePrice * 0.0001; // Price ke hisaab se movement
        let o = currentCandlePrice;
        let c = o + ((Math.random() - 0.5) * volatility);
        let h = Math.max(o, c) + (Math.random() * volatility * 0.5);
        let l = Math.min(o, c) - (Math.random() * volatility * 0.5);
        
        // Agli candle pichli ke close se shuru hogi
        currentCandlePrice = c;

        historyCandles.push({
            time: timeString,
            open: o.toFixed(5),
            high: h.toFixed(5),
            low: l.toFixed(5),
            close: c.toFixed(5),
            color: c >= o ? "Green" : "Red",
            volume: Math.floor(Math.random() * 500) + 300
        });
    }

    // Aakhri candle (Live) ko array ke aakhir mein rakhna
    historyCandles.reverse(); // Latest time sabse upar laane ke liye

    const responseData = {
      developer: "@MMQUOBOT",
      telegram: "https://t.me/vectabot1",
      market: pair,
      data: historyCandles
    };

    res.json(responseData);
});

app.listen(port, () => console.log(`🚀 API is running on port ${port}`));
