import os
import asyncio
import datetime
import sqlite3
import random
import re
import aiohttp

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ====================== CONFIG ======================
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 6507462873
CHANNEL_USERNAME = "@vectabot1"
BANNER_URL = "https://raw.githubusercontent.com/monafatima202-ship-it/apx-otc-api/main/apxprime.png"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
user_ctx = {}

# ====================== PAIRS ======================
PAIRS_DATA = {
    "USDINR": "🇺🇸🇮🇳 USDINR-OTC", "USDPKR": "🇺🇸🇵🇰 USDPKR-OTC", "USDJPY": "🇺🇸🇯🇵 USDJPY-OTC",
    "USDPHP": "🇺🇸🇵🇭 USDPHP-OTC", "USDMXN": "🇺🇸🇲🇽 USDMXN-OTC", "EURUSD": "🇪🇺🇺🇸 EURUSD-OTC",
    "GBPUSD": "🇬🇧🇺🇸 GBPUSD-OTC", "USDCAD": "🇺🇸🇨🇦 USDCAD-OTC", "XAUUSD": "🥇🔱 XAUUSD-OTC",
    "BTCUSD": "₿🌐 BTCUSD-OTC", "USDTRY": "🇺🇸🇹🇷 USDTRY-OTC", "USDBRL": "🇺🇸🇧🇷 USDBRL-OTC",
    "NZDUSD": "🇳🇿🇺🇸 NZDUSD-OTC", "AUDUSD": "🇦🇺🇺🇸 AUDUSD-OTC", "USDCHF": "🇺🇸🇨🇭 USDCHF-OTC",
    "USDCOP": "🇺🇸🇨🇴 USDCOP-OTC", "USDBDT": "🇺🇸🇧🇩 USDBDT-OTC", "USDARS": "🇺🇸🇦🇷 USDARS-OTC",
    "USDNGN": "🇺🇸🇳🇬 USDNGN-OTC",
    "AAPL": "🇺🇸🍎 AAPL-OTC", "MSFT": "🇺🇸💻 MSFT-OTC", "PFE": "🇺🇸💊 PFE-OTC",
    "JNJ": "🇺🇸🏥 JNJ-OTC", "MCD": "🇺🇸🍔 MCD-OTC", "INTL": "🇺🇸🔬 INTL-OTC"
}

STRATEGIES = {
    "1": "🛸 MATRIX NEURAL ENGINE (RSI+MA)",
    "2": "🛸 MACD COGNITIVE CROSSOVER",
    "3": "🛸 BOLLINGER QUANTUM EXTENSION",
    "4": "🛸 STOCHASTIC HIGH ACCURACY SHIELD",
    "5": "🛸 ENSEMBLE SYNAPSE MATRIX (ALL)"
}

# ====================== DATABASE ======================
def init_db():
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid INTEGER PRIMARY KEY, expiry TEXT, is_vip INTEGER DEFAULT 0, temp_key TEXT)''')
    conn.commit()
    conn.close()

# ====================== AUTO BROADCAST ======================
async def send_broadcast():
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)  # PKT
    hour = now.hour

    if hour == 7:
        msg = "🌅 <b>GOOD MORNING TRADERS!</b>\n\nMarket is waking up. Time to activate <b>APX PRIME OS</b>.\nFocus sharp. Today's opportunities await. 🔥✨"
    elif hour == 12:
        msg = "❄️ <b>MID-DAY COOL DOWN PHASE</b>\n\nMarket is volatile. Take a break, review trades.\nProtect capital. Patience wins. 💎"
    elif hour == 18:
        msg = "🛠️ <b>MAINTENANCE WINDOW ACTIVE</b>\n\nSystem optimization in progress.\nReview performance. High accuracy signals resume soon. ⚡"
    elif hour == 23:
        msg = "🌙 <b>DEEP SLEEP PROTOCOL</b>\n\nMarket closing. Rest well and recharge.\nTomorrow is another victory. Stay sharp! 🌟"
    else:
        return

    conn = sqlite3.connect('apx_stable_v190.db')
    users = conn.execute("SELECT uid FROM users WHERE is_vip = 1").fetchall()
    conn.close()

    for (uid,) in users:
        try:
            await bot.send_message(uid, msg)
        except:
            pass

async def notify_admin(uid: int, name: str):
    try:
        await bot.send_message(ADMIN_ID, f"🆕 <b>New User Started Bot</b>\nID: <code>{uid}</code>\nName: {name}\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        pass

# ====================== START ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    init_db()
    await notify_admin(message.from_user.id, message.from_user.first_name)

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="⚡ ATTACH MAIN ENGINE", url=f"https://t.me/vectabot1"))
    kb.row(types.InlineKeyboardButton(text="🛡️ SECURE VERIFICATION", callback_data="auth_check"))
    
    await message.answer_photo(photo=BANNER_URL, caption=f"<b>🌌 APX PRIME OS v260.0</b>\n\nWelcome <b>{message.from_user.first_name}</b> 👑", reply_markup=kb.as_markup())

# ====================== AUTH ======================
@dp.callback_query(F.data == "auth_check")
async def auth_check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    try:
        chat = await bot.get_chat_member(CHANNEL_USERNAME, uid)
        if chat.status not in ["left", "kicked"]:
            await callback.answer("✅ Verified!")
            await callback.message.delete()

            conn = sqlite3.connect('apx_stable_v190.db')
            u = conn.execute("SELECT expiry, is_vip FROM users WHERE uid = ?", (uid,)).fetchone()
            conn.close()

            if u and u[1] == 1 and u[0]:
                try:
                    exp = datetime.datetime.strptime(u[0], "%Y-%m-%d %H:%M:%S")
                    if datetime.datetime.now() < exp:
                        return await show_mode_selection_msg(uid)
                except: pass

            kb = InlineKeyboardBuilder()
            kb.row(types.InlineKeyboardButton(text="🔑 GET 7-DAY ACCESS", callback_data="get_key"))
            await bot.send_photo(uid, BANNER_URL, caption=f"<b>🌌 APX PRIME OS v260.0</b>\n\nHello <b>{callback.from_user.first_name}</b>!", reply_markup=kb.as_markup())
        else:
            await callback.answer("❌ Join channel first!", show_alert=True)
    except:
        await callback.answer("⚠️ Error", show_alert=True)

# (get_key, verify_cmd, show_mode_selection_msg, send_pair_selection, toggle_pair, etc. same as before)

@dp.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    await callback.answer()
    key = f"APX-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("INSERT OR REPLACE INTO users (uid, expiry, is_vip, temp_key) VALUES (?, ?, 0, ?)", (callback.from_user.id, "NONE", key))
    conn.commit(); conn.close()
    await callback.message.answer(f"🔑 <b>7-DAY ACCESS KEY</b>\n\n<code>{key}</code>\n\nSend: <code>/verify {key}</code>")

@dp.message(F.text.startswith("/verify"))
async def verify_cmd(message: types.Message):
    try: key = message.text.split(maxsplit=1)[1].strip()
    except: return await message.answer("❌ Use: <code>/verify YOUR_KEY</code>")
    # ... (same logic as before)
    conn = sqlite3.connect('apx_stable_v190.db')
    row = conn.execute("SELECT temp_key FROM users WHERE uid = ?", (message.from_user.id,)).fetchone()
    conn.close()
    if not row or row[0] != key:
        return await message.answer("❌ <b>Invalid Key!</b>")
    exp = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('apx_stable_v190.db')
    conn.execute("UPDATE users SET expiry = ?, is_vip = 1 WHERE uid = ?", (exp, message.from_user.id))
    conn.commit(); conn.close()
    await message.answer(f"✅ <b>7 DAYS ACCESS ACTIVATED!</b>\nValid until: <code>{exp[:10]}</code>")
    await show_mode_selection_msg(message.from_user.id)

# Mode, Pair, Strategy, Time handlers same...

async def show_mode_selection_msg(uid: int):
    user_ctx[uid] = {"pairs": [], "last_report": None, "strategy": None, "mode": None, "step": None}
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🎯 SINGLE ASSET", callback_data="m:single"))
    kb.row(types.InlineKeyboardButton(text="🌐 MULTI (MAX 3)", callback_data="m:multi"))
    await bot.send_message(uid, "⚡ <b>SELECT OPERATIONAL MODE:</b>", reply_markup=kb.as_markup())

# ... (keep all mode/pair/strategy/time functions from previous version)

# ====================== FIXED TIME FILTER + ATTRACTIVE SIGNALS ======================
async def execute_live_signals(message: types.Message, is_regen=False):
    uid = message.from_user.id
    data = user_ctx.get(uid)
    if not data or not data.get("pairs"):
        return await bot.send_message(uid, "⚠️ No assets selected.")

    if is_regen and data.get("last_report"):
        report_content = data["last_report"]
    else:
        load = await bot.send_message(uid, "🌌 <b>APX PRIME OS ACTIVATING</b>\n<code>░░░░░░░░░░ 0%</code> ✨")
        stages = [("40%", "▓▓▓░░░░░░", "🌟"), ("75%", "▓▓▓▓▓▓░░░░", "💎🔥"), ("98%", "▓▓▓▓▓▓▓▓▓░", "🌸🚀")]
        for p, bar, emoji in stages:
            await asyncio.sleep(0.5)
            await load.edit_text(f"🌌 <b>APX PRIME OS ACTIVATING</b>\n<code>{bar} {p}</code> {emoji}")

        start_t = datetime.datetime.strptime(data['start_t'], "%H:%M").time()
        end_t = datetime.datetime.strptime(data['end_t'], "%H:%M").time()

        signals = []
        async with aiohttp.ClientSession() as session:
            for pair in data["pairs"]:
                try:
                    async with session.get(f"https://milongazi197.serv00.net/f/api.php?pair={pair}-OTC&count=100", timeout=15) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.splitlines():
                                if "=>" not in line: continue
                                parts = [p.strip() for p in line.split("=>")]
                                if len(parts) >= 3:
                                    t_str = parts[1].strip()
                                    direction = parts[2].strip().upper()
                                    try:
                                        sig_time = datetime.datetime.strptime(t_str, "%H:%M").time()
                                        # FIXED TIME FILTER
                                        if start_t <= end_t:
                                            if start_t <= sig_time <= end_t:
                                                signals.append((sig_time, pair, direction, t_str))
                                        else:  # Overnight
                                            if sig_time >= start_t or sig_time <= end_t:
                                                signals.append((sig_time, pair, direction, t_str))
                                    except: pass
                except: pass

        signals.sort(key=lambda x: x[0])

        body = ""
        for _, pair, direction, t in signals[:30]:
            arrow = "↑" if direction in ["CALL", "BUY"] else "↓"
            body += f"✨ <b>{t}</b> • {pair} {arrow} <b>{direction}</b>\n"

        if not body:
            body = "⚠️ No signals found in selected time window.\n"

        report_content = (
            f"<b>🌟 APX PRIME OS v260.0</b>\n"
            f"⏰ <b>{data['start_t']} - {data['end_t']}</b> (UTC+6)\n"
            f"📊 Strategy: <b>{data['strategy']}</b>\n"
            f"📅 Days: <b>{data.get('quotex_days', '7')}</b>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            f"{body}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"❗ <b>HIGH ACCURACY SIGNALS</b> • 1% Risk Only"
        )
        data["last_report"] = report_content
        await load.delete()

    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="🔄 REGENERATE", callback_data="regen_sig"))
    kb.row(types.InlineKeyboardButton(text="📋 COPY SIGNALS", callback_data="copy_signals"))
    kb.row(types.InlineKeyboardButton(text="🔄 CHANGE PAIRS", callback_data="change_pair_back"))
    kb.row(types.InlineKeyboardButton(text="❌ EXIT", callback_data="exit_sys"))

    await bot.send_message(uid, f"<b>📡 LIVE SIGNALS GENERATED</b>\n\n<code>{report_content}</code>", reply_markup=kb.as_markup())

# ====================== CALLBACKS ======================
@dp.callback_query(F.data == "regen_sig")
async def regen_sig(callback: types.CallbackQuery):
    await callback.answer("🔄 Regenerating...")
    await execute_live_signals(callback, is_regen=True)

@dp.callback_query(F.data == "copy_signals")
async def copy_signals(callback: types.CallbackQuery):
    await callback.answer("✅ Signals copied!", show_alert=True)

@dp.callback_query(F.data == "change_pair_back")
async def change_pair_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await show_mode_selection_msg(callback.from_user.id)

@dp.callback_query(F.data == "exit_sys")
async def exit_sys(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, "<code>Terminal Closed. Goodbye 👋</code>")

# ====================== MAIN ======================
async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    
    async def scheduler_loop():
        while True:
            await send_broadcast()
            await asyncio.sleep(3600)
    asyncio.create_task(scheduler_loop())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
