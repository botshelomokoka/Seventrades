import logging
from user import exchange

def rebalance_portfolio(update, context):
    """Rebalances the portfolio to maintain equal allocations across selected assets."""
    try:
        # Fetch current prices and balances for all coins
        tickers = exchange.fetch_tickers()
        balance = exchange.fetch_balance()

        # Calculate total portfolio value (excluding USDT)
        total_value_usdt = 0
        from seven_bot import coins_to_trade  # Import coins_to_trade
        for symbol in coins_to_trade:
            total_value_usdt += balance[symbol]['free'] * tickers[f"{symbol}/USDT"]['last']

        # Calculate target amount for each asset
        target_allocation = 1 / len(coins_to_trade)  # Equal allocation for each asset
        target_amount_usdt = total_value_usdt * target_allocation

        # Rebalance each asset
        for symbol in coins_to_trade:
            current_amount_usdt = balance[symbol]['free'] * tickers[f"{symbol}/USDT"]['last']
            difference_usdt = target_amount_usdt - current_amount_usdt

            if abs(difference_usdt) > 0.1:  # Avoid dust trades (adjust threshold as needed)
                if difference_usdt > 0:  # Buy more of the asset
                    # Calculate amount to buy (consider slippage and fees)
                    amount_to_buy = difference_usdt / tickers[f"{symbol}/USDT"]['last']
                    exchange.create_market_buy_order(f"{symbol}/USDT", amount_to_buy)
                    logging.info(f"Rebalancing: Buying {amount_to_buy:.6f} of {symbol}")
                else:  # Sell some of the asset
                    exchange.create_market_sell_order(f"{symbol}/USDT", -difference_usdt)
                    logging.info(f"Rebalancing: Selling {-difference_usdt:.6f} of {symbol}")
        
        if update: # Only send telegram update if the function is called by Telegram bot 
            update.message.reply_text("Portfolio rebalancing completed.")

    except Exception as e:
        logging.error(f"Error during rebalancing: {e}")
        if update:
            update.message.reply_text("An error occurred during rebalancing.")
