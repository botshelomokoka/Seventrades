import logging
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Telegram Bot Setup
bot_token = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your actual bot token
updater = Updater(bot_token)
dispatcher = updater.dispatcher


# Import from other files
from seven_bot import (
    get_total_portfolio_value_usdt,
    coins_to_trade,
    rebalance_portfolio,
    start_trading,
    stop_trading,
    is_running  # Assuming you have this variable in seven_bot.py
)
from email_notifier import send_email

# Command Handlers
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    global is_running
    if not is_running:
        start_trading()
        update.message.reply_text("Bot started.")
    else:
        update.message.reply_text("Bot is already running.")


def stop(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /stop is issued."""
    global is_running
    if is_running:
        stop_trading()
        update.message.reply_text("Bot stopped.")
    else:
        update.message.reply_text("Bot is already stopped.")


def status(update: Update, context: CallbackContext) -> None:
    """Send a message with the current portfolio status."""
    portfolio_value = get_total_portfolio_value_usdt()
    active_coins_str = ", ".join(coins_to_trade)
    update.message.reply_text(
        f"Your current portfolio value is {portfolio_value:.2f} USDT.\n"
        f"Active coins: {active_coins_str}"
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)
    # Send email notification for errors
    send_email(
        "Crypto Trading Bot Error", f"Update '{update}' caused error '{context.error}'"
    )


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(CommandHandler("status", status))
dispatcher.add_handler(CommandHandler("rebalance", rebalance_portfolio))
dispatcher.add_error_handler(error)

