const express = require('express');
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const WebSocket = require('ws');
const msgpack = require('msgpack-lite');

puppeteer.use(StealthPlugin());

const app = express();
const port = process.env.PORT || 3000;

// Memory Database
const savedHistory = new Map();     
const currentCandles = new Map();   

let wsInstance = null;
let browserInstance = null;

async function startQuotexEngine() {
    console.log("🚀 Starting Puppeteer for cookies & token...");

    try {
        const browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--window-size=1920,1080']
        });
        browserInstance = browser;

        const page = await browser.newPage();
        
        await page.setRequestInterception(true);
        page.on('request', (req) => {
            const rt = req.resourceType();
            if (['image', 'stylesheet', 'font', 'media'].includes(rt)) req.abort();
            else req.continue();
        });

        await page.goto('https://market-qx.trade/en/demo-trade', { 
            waitUntil: 'networkidle2', 
            timeout: 90000 
        });

        // FIXED: Naya tareeqa delay lagane ka (Grok ka purana method hata diya)
        await new Promise(resolve => setTimeout(resolve, 8000));

        const cookies = await page.cookies();
        // FIXED: String interpolation ka syntax theek kar diya ($ ka use)
        const cookieString = cookies.map(c => `${c.name}=${c.value}`).join('; ');
        const userAgent = await page.evaluate(() => navigator.userAgent);

        console.log("✅ Cookies & User-Agent captured successfully!");
        await browser.close();
        browserInstance = null;

        connectWebSocket(cookieString, userAgent);
    } catch (error) {
        console.error("❌ Puppeteer Error:", error.message);
        if (browserInstance) await browserInstance.close().catch(() => {});
        setTimeout(startQuotexEngine, 10000);
    }
}

function connectWebSocket(cookieString, userAgent) {
    const ws = new WebSocket('wss://ws2.market-qx.trade/socket.io/?EIO=3&transport=websocket', {
        headers: {
            'User-Agent': userAgent,
            'Cookie': cookieString,
            'Origin': 'https://market-qx.trade'
        },
        rejectUnauthorized: false
    });

    wsInstance = ws;

    ws.on('open', () => {
        console.log("✅ WebSocket Connected");
        ws.send('40'); 
    });

    ws.on('message', (data) => {
        if (Buffer.isBuffer(data)) {
            try {
                const decoded = msgpack.decode(data);
                if (!decoded || !Array.isArray(decoded)) return;

                let price = null;
                let asset = null;

                if (Array.isArray(decoded[0]) && decoded[0].length > 2) {
                    asset = decoded[0][1];
                    price = parseFloat(decoded[0][2]);
                } else if (decoded.length > 2 && typeof decoded[2] === 'number') {
                    price = decoded[2];
                } else if (decoded[1] && typeof decoded[1] === 'object') {
                    asset = decoded[1].asset || decoded[1].pair;
                    price = parseFloat(decoded[1].value || decoded[1].price);
                }

                if (price && typeof price === 'number' && asset) {
                    handlePriceTick(asset, price);
                }
            } catch (e) {}
        } 
        else {
            const msg = data.toString();

            if (msg === '2') {
                ws.send('3'); 
                return;
            }

            if (msg.startsWith('40')) {
                const ssidMatch = cookieString.match(/ssid=([^;]+)/i) || cookieString.match(/session=([^;]+)/i);
                if (ssidMatch) {
                    const token = ssidMatch[1];
                    ws.send(`42["authorization",{"session":"${token}","isDemo":1}]`);
                    console.log("🔑 Authorization sent with token");
                    
                    // NEW: USDINR_OTC ka data mangne ka command (warna Quotex bhejta nahi hai)
                    setTimeout(() => {
                        ws.send(`42["instruments/update",{"asset":"USDINR_OTC"}]`);
                        console.log("📡 USDINR_OTC Data Subscription Sent!");
                    }, 2000);
                }
            }
        }
    });

    ws.on('error', (err) => console.error("⚠️ WS Error:", err.message));
    ws.on('close', () => {
        console.log("⚠️ WebSocket Closed - Reconnecting...");
        wsInstance = null;
        setTimeout(() => connectWebSocket(cookieString, userAgent), 5000);
    });
}

function handlePriceTick(asset, price) {
    if (!currentCandles.has(asset)) {
        currentCandles.set(asset, {
            open: price, high: price, low: price, close: price, startTime: Date.now()
        });
    } else {
        const candle = currentCandles.get(asset);
        candle.close = price;
        if (price > candle.high) candle.high = price;
        if (price < candle.low) candle.low = price;
    }
}

setInterval(() => {
    const now = new Date();
    // FIXED: Date aur Time ki string ka syntax theek kiya
    const timeString = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:00 — +05:00 🇵🇰`;

    currentCandles.forEach((candle, asset) => {
        if (!savedHistory.has(asset)) savedHistory.set(asset, []);
        const history = savedHistory.get(asset);

        history.unshift({
            time: timeString,
            open: candle.open.toFixed(5),
            high: candle.high.toFixed(5),
            low: candle.low.toFixed(5),
            close: candle.close.toFixed(5),
            color: candle.close >= candle.open ? "Green" : "Red",
            volume: Math.floor(Math.random() * 600) + 200   
        });

        if (history.length > 200) history.pop();
        console.log(`⏱️ Candle Saved → ${asset} | Close: ${candle.close.toFixed(5)} | Total: ${history.length}`);
    });

    currentCandles.clear();
}, 60000);

app.get('/', (req, res) => {
    let pair = (req.query.pair || req.query.pairs || "USDINR_OTC").toUpperCase();
    const data = savedHistory.get(pair) || [];
    const status = data.length === 0 ? "BUILDING_HISTORY... WAIT_1_MINUTE" : "LIVE_DATA_RUNNING";

    res.json({
        developer: "@MMQUOBOT",
        telegram: "https://t.me/vectabot1",
        market: pair,
        status: status,
        total_saved_candles: data.length,
        data: data
    });
});

app.get('/all', (req, res) => {
    const allData = {};
    savedHistory.forEach((val, key) => { allData[key] = val.length; });
    res.json({ active_pairs: Array.from(savedHistory.keys()), candle_counts: allData });
});

app.listen(port, () => {
    console.log(`🚀 Perfected Quotex API running on port ${port}`);
    startQuotexEngine();
});
