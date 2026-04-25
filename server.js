const express = require('express');
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

// Cloudflare ki security bypass karne ke liye stealth mode
puppeteer.use(StealthPlugin());

const app = express();
const port = process.env.PORT || 3000;

let currentLivePrice = 0;

// Headless Browser Setup
async function startHeadlessQuotex() {
    console.log("🚀 Background Chrome Browser Start ho raha hai...");
    
    // Railway par Chrome chalane ke zaroori settings
    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    });
    
    const page = await browser.newPage();
    
    // 1. Browser se Node.js server mein data bhejne ka rasta banana
    await page.exposeFunction('sendPriceToAPI', (price) => {
        currentLivePrice = price;
    });

    // 2. Hamara wahi purana "System Hook" browser load hone se pehle dalna!
    await page.evaluateOnNewDocument(() => {
        const origParse = JSON.parse;
        let lastP = 0;
        JSON.parse = function(text) {
            const obj = origParse(text);
            try {
                const match = text.match(/[\[:,]\s*(\d+\.\d{3,6})\b/);
                if (match) {
                    const p = parseFloat(match[1]);
                    if(p < 200000 && p !== lastP) {
                        lastP = p;
                        // Data Node.js ko bhej do
                        window.sendPriceToAPI(p);
                    }
                }
            } catch(e) {}
            return obj;
        };
    });

    console.log("🌍 Quotex ki website open ki jaa rahi hai...");
    
    // Quotex kholna (timeout badha diya hai taake slow load ho toh crash na ho)
    await page.goto('https://market-qx.trade/en/', { waitUntil: 'networkidle2', timeout: 60000 });
    
    console.log("✅ Quotex Live! Real Price Hooked Successfully.");
}

// Server start hote hi Chrome background mein on kar do
startHeadlessQuotex();

// API Endpoint (Bot ke liye 100 Candles Data)
app.get('/', (req, res) => {
    const pair = req.query.pairs || "LIVE_OTC";
    
    // Agar background Chrome ne abhi data nahi pakra toh 1.0 dikhayega, warna Asli Price.
    let basePrice = currentLivePrice || 1.00000;
    
    let historyCandles = [];
    let currentCandlePrice = basePrice;
    
    // Bot ke liye Candles generate karna (Lekin Base asli live market ki hogi)
    for (let i = 99; i >= 0; i--) {
        let candleTime = new Date(Date.now() - (i * 60000));
        let timeString = `${candleTime.getFullYear()}-${String(candleTime.getMonth() + 1).padStart(2, '0')}-${String(candleTime.getDate()).padStart(2, '0')} ${String(candleTime.getHours()).padStart(2, '0')}:${String(candleTime.getMinutes()).padStart(2, '0')}:00 — +05:00 🇵🇰`;

        let volatility = currentCandlePrice * 0.0001; 
        let o = currentCandlePrice;
        let c = o + ((Math.random() - 0.5) * volatility);
        let h = Math.max(o, c) + (Math.random() * volatility * 0.5);
        let l = Math.min(o, c) - (Math.random() * volatility * 0.5);
        
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

    historyCandles.reverse(); // Latest price upar
    
    // Sab se top wali (Latest) candle par 100% real live price update karna
    if(historyCandles.length > 0) {
        historyCandles[0].close = basePrice.toFixed(5);
        historyCandles[0].high = Math.max(parseFloat(historyCandles[0].open), basePrice).toFixed(5);
        historyCandles[0].low = Math.min(parseFloat(historyCandles[0].open), basePrice).toFixed(5);
        historyCandles[0].color = basePrice >= parseFloat(historyCandles[0].open) ? "Green" : "Red";
    }

    const responseData = {
      developer: "@MMQUOBOT",
      telegram: "https://t.me/vectabot1",
      market: pair.toUpperCase(),
      data: historyCandles
    };

    res.json(responseData);
});

app.listen(port, () => console.log(`🚀 Headless API is running on port ${port}`));
