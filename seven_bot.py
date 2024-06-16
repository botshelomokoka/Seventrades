import ccxt
import datetime
import time
from ccxt.base.errors import ExchangeError, NetworkError, RequestTimeout, InsufficientFunds, InvalidOrder, RateLimitExceeded

# Import functions from other modules
from email_notifier import send_email
from portfolio_management import rebalance_portfolio
from risk_management import check_stop_loss, check_take_profit, check_overall_stop_loss
from trade_strategy import execute_macd_ichimoku_strategy, select_top_coins, is_high_confidence_signal
from utils import calculate_trade_amount, predict_trend, get_total_portfolio_value_usdt

# --- LOGGING ---
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- BINANCE SETUP ---
from user import exchange

# --- TRADING BOT VARIABLES ---
transaction_count = 0
coins_to_trade = select_top_coins("quarter")  # Initialize with initial coins
last_month_end_value = None
bought_prices = {}  # Store average bought price for each asset
btc_accumulation_target = 10
initial_portfolio_value = get_total_portfolio_value_usdt()
stop_loss_triggered = False
profit_protection_threshold = 0.50  
profit_protection_increment = 0.25 
last_profit_protection_trigger = None
is_profit_protection_active = False
is_running = False

# --- EXECUTION FUNCTIONS ---
def execute_dca():
    global transaction_count, last_month_end_value

    usdt_amount = 3000  # Your combined monthly investment in USDT
    
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
    try:
        top_coin = coins_to_trade[0]
        order = exchange.create_market_buy_order(f"{top_coin}/USDT", usdt_amount)  
        bought_prices[top_coin] = order['average']

        today = datetime.date.today()
        if today.day == 1:
            last_month_end_value = get_total_portfolio_value_usdt()

    except InsufficientFunds as e:
        logging.error(f"Insufficient funds for DCA: {e}")

        # Retry logic for insufficient funds
        if 'last_dca_retry' not in globals():
            global last_dca_retry
            last_dca_retry = time.time()  # Initialize the first retry time
        elif time.time() - last_dca_retry < retry_interval:
            return  # Not enough time has passed for the next retry

        if transaction_count < 2: 
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

def execute_trades():
    # Check if it's time to re-evaluate top coins
    today = datetime.date.today()
    if today.day == 1 and (today.month in [1, 4, 7, 10] or (today.month == 1 and today.day == 1)):
        global coins_to_trade  # Declare as global to modify it
        coins_to_trade = select_top_coins()

    # Get projections before trading
    projections = project_portfolio_value() 
    for symbol in coins_to_trade:
        if check_stop_loss(symbol, bought_prices.get(symbol, 0)):
            continue  # Skip to the next coin if stop-loss is triggered
        if not stop_loss_triggered:
            try:
                execute_macd_ichimoku_strategy(symbol, projections)
            except (
                ExchangeError,
                NetworkError,
                RequestTimeout,
                InsufficientFunds,
                InvalidOrder,
                RateLimitExceeded,
            ) as error:
                logging.error(f"Error during trading {symbol}: {error}")
                time.sleep(15)  # Wait for 15 seconds before retrying

# --- REPORTING ---
def calculate_future_value(current_value, monthly_investment, annual_growth_rate, num_years, withdrawal_start_age, monthly_withdrawal):
    """Calculates the projected future value, accounting for withdrawals."""
    total_months = num_years * 12
    future_value = current_value
    withdrawal_start_month = (withdrawal_start_age - 42) * 12  # Assuming you're 42 now
    for month in range(total_months):
        future_value += monthly_investment
        future_value *= (1 + annual_growth_rate / 12)
        if month >= withdrawal_start_month:
            future_value -= monthly_withdrawal
    return future_value

def project_portfolio_value():
    """
    Calculate and return projected growth for each asset in the portfolio.
    """
    current_value = get_total_portfolio_value_usdt()
    monthly_investment = 3000  
    annual_growth_rates = [0.10, 0.15, 0.20]  
    projection_years = [8, 18]  
    withdrawal_scenarios = {
        50: {"withdrawal": 30000, "label": "Optimistic"}, 
