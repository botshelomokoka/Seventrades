import logging
import threading
import time

# Import necessary modules
from seven_bot import (
    exchange, 
    check_api_keys,
    check_internet_connection,
    get_total_portfolio_value_usdt,
    execute_dca,
    check_overall_stop_loss, 
    check_coin_stop_loss,
    execute_trades,
    log_and_report_progress,
    coins_to_trade,
    bought_prices,
    stop_loss_triggered,
    initial_portfolio_value
)
from crypto_dashboard import app  # Make sure this import is correct based on your dashboard file's name
from telegram_bot import updater 

# Logging setup 
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to run the trading bot
def run_bot():
    global stop_loss_triggered, initial_portfolio_value

    check_api_keys()
    check_internet_connection()

    initial_portfolio_value = get_total_portfolio_value_usdt()

    while True:
        try:
            check_overall_stop_loss()  
            for symbol in coins_to_trade:
                if symbol in bought_prices:
                    check_coin_stop_loss(symbol, bought_prices[symbol])

            execute_dca()
            if not stop_loss_triggered:
                execute_trades()
            log_and_report_progress()
            time.sleep(86400)  # Sleep for 24 hours (adjust as needed)
        except Exception as e:  
            logging.error(f"Unexpected error: {e}")
            time.sleep(60)

# Run bot and dashboard in separate threads
if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    dashboard_thread = threading.Thread(target=app.run_server, kwargs={'debug': True})

    bot_thread.start()
    dashboard_thread.start()
    bot_thread.join()
    dashboard_thread.join()
