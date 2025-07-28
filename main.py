import logging
import os
from telegram import Bot
from telegram.ext import CommandHandler, ApplicationBuilder
from flask import Flask, request
import threading

# === Load from Environment Variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = None  # Set after /start command

# Allowed Forex Pairs
ALLOWED_PAIRS = ["EURUSD", "NZDUSD", "GBPJPY", "USDJPY", "AUDUSD"]

# Enable logging
logging.basicConfig(level=logging.INFO)

# Flask App
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Telegram /start command
async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await context.bot.send_message(chat_id=CHAT_ID, text="✅ Bot is active and ready to receive SMC signals!")

# Setup Telegram bot handler
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route("/signal", methods=["POST"])
def signal():
    global CHAT_ID
    data = request.json

    if CHAT_ID is None:
        return "❌ Send /start in Telegram first.", 400

    pair = data.get("pair", "Unknown").replace("/", "").upper()
    if pair not in ALLOWED_PAIRS:
        return f"❌ Pair {pair} is not allowed.", 400

    signal_type = data.get("signal", "").upper()
    try:
        entry = float(data.get("entry", "0"))
        sl = float(data.get("sl", "0"))
        tp = float(data.get("tp", "0"))
    except ValueError:
        return "❌ Invalid entry, SL, or TP values.", 400

    reason = data.get("reason", "SMC Strategy")
    bos = data.get("bos", "")
    order_block = data.get("order_block", "")
    fvg = data.get("fvg", "")
    liquidity_sweep = data.get("liquidity_sweep", "")

    # Calculate TP and SL if missing
    risk_reward_ratio = 2.5
    if sl == 0:
        sl = entry - 0.0010 if signal_type == "BUY" else entry + 0.0010
    if tp == 0:
        risk = abs(entry - sl)
        tp = entry + (risk * risk_reward_ratio) if signal_type == "BUY" else entry - (risk * risk_reward_ratio)

    # Message formatting
    message = f"""
📊 *Forex Signal Alert*

Pair: {pair}
Signal: {signal_type}
Reason: {reason}
Entry: {entry:.5f}
SL: {sl:.5f}
TP: {tp:.5f}
Risk/Reward: 1:{risk_reward_ratio}

🔍 *SMC Details:*
Break of Structure: {bos}
Order Block: {order_block}
FVG: {fvg}
Liquidity Sweep: {liquidity_sweep}
"""

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
    return "✅ Signal sent", 200

# Run Flask and Telegram together
def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

def run_telegram():
    telegram_app.run_polling()

# Start both
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_telegram()
