const axios = require('axios');
const cron = require('node-cron');

const TOKEN = "8304350866:AAE7v8Fjk7UFE8YnVKQmaKE9ohQ4d_tMeDA";
const CHAT_ID = "-1003725733226";
const API_URL = "https://apx-otc-api-production.up.railway.app/?pair=";

let stats = { win: 0, loss: 0, mtg: 0 };

// TESTING SCHEDULE: Har 1 minute baad (Isko baad mein 10-12 wale se badal lena)
const testSchedule = "* * * * *"; 

async function sendToTelegram(msg) {
    const url = `https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}&text=${encodeURIComponent(msg)}&parse_mode=Markdown`;
    try { await axios.get(url); } catch(e) { console.log("Telegram Error"); }
}

async function processSignal(pair, isMTG = false) {
    try {
        const response = await axios.get(API_URL + pair);
        const candle = response.data.candles[0];
        
        // Advanced Logic: Last candle movement check
        const dir = candle.close > candle.open ? "UP 🟢" : "DOWN 🔴";
        
        const typeText = isMTG ? "🔄 **MARTINGALE-1**" : "🚀 **FRESH SIGNAL**";
        const msg = `🔔 **APX NEURAL ENGINE**\n` +
                    `━━━━━━━━━━━━━━━━━━\n` +
                    `📊 ASSET: **${pair.toUpperCase()}**\n` +
                    `↕️ DIRECTION: **${dir}**\n` +
                    `⏳ EXPIRY: **1 MIN**\n` +
                    `⚠️ TYPE: ${typeText}\n` +
                    `━━━━━━━━━━━━━━━━━━\n` +
                    `🕒 TIME: ${new Date().toLocaleTimeString('en-PK', {timeZone: 'Asia/Karachi'})}`;
        
        await sendToTelegram(msg);

        // Result check logic
        setTimeout(() => checkResult(pair, dir, isMTG), 61000);
    } catch (e) { console.log("API Error: Fetching candles failed."); }
}

async function checkResult(pair, dir, isMTG) {
    try {
        const response = await axios.get(API_URL + pair);
        const c = response.data.candles[0];
        const isUp = dir.includes("UP");
        const win = (isUp && c.close > c.open) || (!isUp && c.close < c.open);

        if (win) {
            stats.win++;
            await sendToTelegram(`🎯 **RESULT: ${pair.toUpperCase()} WIN ✅**\n🏆 BARI CLAPPING! 👏 🔥 🏆`);
        } else if (!isMTG) {
            stats.mtg++;
            await sendToTelegram(`🔄 **RESULT: ${pair.toUpperCase()} LOSS!**\n🔥 Sending MTG-1 Now...`);
            processSignal(pair, true); // Immediate MTG-1
        } else {
            stats.loss++;
            await sendToTelegram(`❌ **RESULT: ${pair.toUpperCase()} LOSS**\nMoving to next trade.`);
        }
    } catch(e) { console.log("Result check failed."); }
}

// Start Testing
console.log("Bot Test Engine Started... Waiting for next minute tick.");
cron.schedule(testSchedule, () => {
    const pairs = ["USDPKR_otc", "USDINR_otc", "BRLUSD_otc"];
    const randomPair = pairs[Math.floor(Math.random() * pairs.length)];
    processSignal(randomPair);
}, { timezone: "Asia/Karachi" });
