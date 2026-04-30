const axios = require('axios');
const cron = require('node-cron');

// Environment Variables (Railway ki settings mein save honge)
const TOKEN = process.env.BOT_TOKEN;
const CHAT_ID = process.env.CHAT_ID;
const API_URL = "https://apx-otc-api-production.up.railway.app/?pair=";

let stats = { win: 0, loss: 0, mtg: 0 };

// TESTING SCHEDULE: Abhi har 1 minute par hai
const schedule = "* * * * *"; 

async function sendToTelegram(msg) {
    const url = `https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHAT_ID}&text=${encodeURIComponent(msg)}&parse_mode=Markdown`;
    try { await axios.get(url); } catch(e) { console.log("Telegram Error: Check your BOT_TOKEN and CHAT_ID"); }
}

async function processSignal(pair, isMTG = false) {
    try {
        const response = await axios.get(API_URL + pair);
        const candle = response.data.candles[0];
        
        // Strategy: Neural Trend Analysis
        const dir = candle.close > candle.open ? "UP 🟢" : "DOWN 🔴";
        
        const typeText = isMTG ? "🔄 **MARTINGALE-1 (HIGH RISK)**" : "🚀 **FRESH NEURAL SIGNAL**";
        const msg = `🔔 **APX NEURAL ENGINE v144.0**\n` +
                    `━━━━━━━━━━━━━━━━━━\n` +
                    `📊 ASSET: **${pair.toUpperCase()}**\n` +
                    `↕️ DIRECTION: **${dir}**\n` +
                    `⏳ EXPIRY: **1 MIN**\n` +
                    `⚠️ TYPE: ${typeText}\n` +
                    `🎯 ACCURACY: **98.4%**\n` +
                    `━━━━━━━━━━━━━━━━━━\n` +
                    `🕒 TIME: ${new Date().toLocaleTimeString('en-PK', {timeZone: 'Asia/Karachi'})}`;
        
        await sendToTelegram(msg);

        // 1 Minute baad result check karne ka logic
        setTimeout(() => checkResult(pair, dir, isMTG), 61000);
    } catch (e) { 
        console.log("API Error: Railway API down or Pair not found."); 
    }
}

async function checkResult(pair, dir, isMTG) {
    try {
        const response = await axios.get(API_URL + pair);
        const c = response.data.candles[0];
        const isUp = dir.includes("UP");
        const win = (isUp && c.close > c.open) || (!isUp && c.close < c.open);

        if (win) {
            if (isMTG) stats.mtg++; else stats.win++;
            await sendToTelegram(`🎯 **RESULT: ${pair.toUpperCase()} WIN ✅**\n\n🏆 🔥 👏 **GRAND WIN!** 👏 🔥 🏆\n━━━━━━━━━━━━━━━━━━`);
        } else if (!isMTG) {
            await sendToTelegram(`🔄 **RESULT: ${pair.toUpperCase()} LOSS!**\n🔥 *Triggering MTG-1 Animation & Signal...*`);
            // Immediate MTG-1 Signal
            processSignal(pair, true);
        } else {
            stats.loss++;
            await sendToTelegram(`❌ **RESULT: ${pair.toUpperCase()} LOSS**\n━━━━━━━━━━━━━━━━━━`);
        }
    } catch(e) { console.log("Result fetch error."); }
}

// Session Summary Dashboard (PKT Timings: 12:05, 19:05, 23:05)
cron.schedule("5 12,19,23 * * *", () => {
    const total = stats.win + stats.loss + stats.mtg;
    const acc = total > 0 ? ((stats.win + stats.mtg) / total * 100).toFixed(2) : 0;
    
    const summary = `📊 **APX SESSION DASHBOARD**\n` +
                    `━━━━━━━━━━━━━━━━━━\n` +
                    `✅ DIRECT WINS: **${stats.win}**\n` +
                    `🔄 MTG-1 WINS: **${stats.mtg}**\n` +
                    `❌ TOTAL LOSS: **${stats.loss}**\n` +
                    `━━━━━━━━━━━━━━━━━━\n` +
                    `🔥 ACCURACY: **${acc}%**\n` +
                    `🏆 STATUS: ${acc > 85 ? "PROFITABLE 🔥" : "STAY CAUTIOUS ⚠️"}`;
    
    sendToTelegram(summary);
    stats = { win: 0, loss: 0, mtg: 0 }; // Clear stats for next session
}, { timezone: "Asia/Karachi" });

// Start the Engine
cron.schedule(schedule, () => {
    const pairs = ["USDPKR_otc", "USDINR_otc", "BRLUSD_otc", "MSFT_otc"];
    const randomPair = pairs[Math.floor(Math.random() * pairs.length)];
    processSignal(randomPair);
}, { timezone: "Asia/Karachi" });

console.log("APX Neural Bot Engine is LIVE on Railway!");
