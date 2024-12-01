import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import pandas as pd
import talib

# دریافت توکن از متغیر محیطی
TELEGRAM_TOKEN = os.getenv("7699913349:AAFdvgmoiKbV81ynjgJajAQzVkfop24VJfc")
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

# دریافت قیمت لحظه‌ای
def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT"
    response = requests.get(url)
    data = response.json()
    return float(data['price'])

# دریافت داده‌های تاریخی
def get_historical_data(symbol, interval="1h", limit=100):
    params = {
        "symbol": f"{symbol.upper()}USDT",
        "interval": interval,
        "limit": limit
    }
    response = requests.get(BINANCE_API_URL, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'])
    df['close'] = df['close'].astype(float)
    return df

# محاسبه RSI
def calculate_rsi(symbol, period=14):
    df = get_historical_data(symbol)
    rsi = talib.RSI(df['close'], timeperiod=period)
    return rsi.iloc[-1]

# دستور /price
def price(update: Update, context: CallbackContext):
    symbol = context.args[0].upper() if context.args else "BTC"
    try:
        price = get_price(symbol)
        update.message.reply_text(f"The current price of {symbol} is ${price:.2f}")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

# دستور /rsi
def rsi(update: Update, context: CallbackContext):
    symbol = context.args[0].upper() if context.args else "BTC"
    period = int(context.args[1]) if len(context.args) > 1 else 14
    try:
        rsi_value = calculate_rsi(symbol, period)
        update.message.reply_text(f"The RSI of {symbol} (Period: {period}) is {rsi_value:.2f}")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

# شروع ربات
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("price", price))
    dispatcher.add_handler(CommandHandler("rsi", rsi))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()