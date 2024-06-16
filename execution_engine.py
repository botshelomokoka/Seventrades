import logging
import time
import datetime

from user import exchange
from seven_bot import (
    coins_to_trade,
    bought_prices,
    stop_loss_triggered,
    check_stop_loss,
    execute_macd_ichimoku_strategy,
    select_top_coins,
)

# --- EXECUTION FUNCTIONS ---

def execute_dca():
    global transaction_count, last_bnb_check_date

    # Check if USDT accumulation target is reached
    usdt_balance = exchange.fetch_balance()['USDT']['free']
    if usdt_balance >= btc_accumulation_target:
        logging.info("USDT accumulation target reached. Stopping DCA.")
        return  # Stop DCA if target is reached

    # Check if initial investment is sufficient
    total_portfolio_value_usdt = get_total_portfolio_value_usdt()
    if total_portfolio_value_usdt < 100:
        logging.error("Insufficient initial funds. Please deposit more USDT.")
        return

    # Buy top coin
    usdt_amount = 3000  # Your combined monthly investment in USDT
    try:
        top_coin = coins_to_trade[0]
        order = exchange.create_market_buy_order(f"{top_coin}/USDT", usdt_amount)
        bought_prices[top_coin] = order["average"]

        today = datetime.date.today()
        if today.day == 1:
            last_month_end_value = get_total_portfolio_value_usdt()

    except InsufficientFunds as e:
        logging.error(f"Insufficient funds for DCA: {e}")
        # Retry logic for insufficient funds
        if "last_dca_retry" not in globals():
            global last_dca_retry
            last_dca_retry = time.time()  # Initialize the first retry time
        elif time.time() - last_dca_retry < retry_interval:
            return  # Not enough time has passed for the next retry

        if transaction_count < (max_bnb_transactions + 2):
            logging.info(f"Retrying DCA after {retry_interval // 86400} days...")
            last_dca_retry = time.time()
            time.sleep(retry_interval)  
            execute_dca()
        else:
            logging.warning("Maximum DCA retries reached. Waiting for next month.")
            transaction_count = 0
            last_dca_retry = None

    except (ExchangeError, NetworkError, RequestTimeout) as error:
        logging.error(f"Error during DCA execution: {error}")
        time.sleep(60)


def check_overall_stop_loss():
    """Checks if the overall portfolio value dropped by 10% and liquidates to USDT."""
    global stop_loss_triggered
    current_value = get_total_portfolio_value_usdt()
    if current_value <= initial_portfolio_value * 0.9:
        for symbol in coins_to_trade:
            asset_amount = exchange.fetch_balance()[symbol]["free"]
            if asset_amount > 0:
                exchange.create_market_sell_order(f"{symbol}/USDT", asset_amount)  # Sell for USDT
        stop_loss_triggered = True
        logging.warning("Overall stop-loss triggered. Liquidating all holdings to USDT.")
        return True
    return False

def execute_trades():
    # Check if it's time to re-evaluate top coins
    today = datetime.date.today()
    if today.day == 1 and (today.month in [1, 4, 7, 10] or today.month == 1 and today.day == 1):  # Quarterly or yearly
        select_top_coins()

    projections = project_portfolio_value() # Get projections before trading
    for symbol in coins_to_trade:  # Trade selected coins against USDT
        check_coin_stop_loss(symbol, bought_prices.get(symbol, 0))
        if not stop_loss_triggered:
            try:
                execute_macd_ichimoku_strategy(symbol, projections)
            except (ExchangeError, NetworkError, RequestTimeout, InsufficientFunds, InvalidOrder, RateLimitExceeded) as error:
                if handle_exchange_errors(error):
                    execute_trades()  # Retry trades if recoverable error
                else:
                    raise  # Raise the error for other types of exceptions
