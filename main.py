smc_bot.py - FULL CODE with Environment Variables and Always-On Hosting Support

import logging import os from telegram import Bot from telegram.ext import CommandHandler, ApplicationBuilder from flask import Flask, request import threading

=== Load from Environment Variables ===

BOT_TOKEN = os.getenv("BOT_TOKEN") CHAT_ID = None  # This will be set when you send /start

Enable logging

logging.basicConfig(level=logging.INFO)

Flask App for receiving signals from TradingView

app = Flask(name) bot = Bot(token=BOT_TOKEN)

Command /start for Telegram bot

async def start(update, context): global CHAT_ID CHAT_ID = update.effective_chat.id await context.bot.send_message(chat_id=CHAT_ID, text="✅ Bot is active and ready to receive SMC signals!")

Set up bot command handler

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build() telegram_app.add_handler(CommandHandler("start", start))

Webhook for TradingView signals

@app.route("/signal", methods=["POST"]) def signal(): global CHAT_ID data = request.json

if CHAT_ID is None:
    return "❌ Send /start in Telegram first.", 400

pair = data.get("pair", "Unknown")
signal_type = data.get("signal", "")
entry = data.get("entry", "")
sl = data.get("sl", "")
tp = data.get("tp", "")
reason = data.get("reason", "SMC Strategy")

message = f"""

📊 Forex Signal Alert

Pair: {pair} Signal: {signal_type} Reason: {reason} Entry: {entry} SL: {sl} TP: {tp} Risk/Reward: 1:2.5"""

bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
return "✅ Signal sent", 200

Run Flask and Telegram together

def run_flask(): app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

def run_telegram(): telegram_app.run_polling()

Start both apps

if name == "main": threading.Thread(target=run_flask).start() run_telegram()

