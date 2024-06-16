def rebalance_portfolio(update: Update, context: CallbackContext):
    """Rebalances the portfolio to maintain equal allocations across selected assets."""
    try:
        # Fetch current prices and balances for all coins
        tickers = exchange.fetch_tickers()
        balance = exchange.fetch_balance()

        # Calculate total portfolio value (excluding ETH used for fees)
        total_value_eth = 0
        for symbol in coins_to_trade:
            total_value_eth += (balance[symbol]['free'] + balance[symbol]['used']) * tickers[f"{symbol}/ETH"]['last']  # Use ETH as base currency

        # Calculate target amount for each asset
        target_allocation = 1 / len(coins_to_trade)  # Equal allocation for each asset
        target_amount_eth = total_value_eth * target_allocation

        # Rebalance each asset
        for symbol in coins_to_trade:
            current_amount_eth = (balance[symbol]['free'] + balance[symbol]['used']) * tickers[f"{symbol}/ETH"]['last']
            difference_eth = target_amount_eth - current_amount_eth

            if abs(difference_eth) > 0.001:  # Avoid dust trades
                if difference_eth > 0:  # Buy more of the asset
                    # Calculate amount to buy (consider slippage and gas fees)
                    amount_to_buy = difference_eth / tickers[f"{symbol}/ETH"]['last']
                    execute_trade('ETH', symbol, amount_to_buy)  # Assuming ETH is used as input
                    logging.info(f"Rebalancing: Buying {amount_to_buy:.6f} of {symbol}")
                else:  # Sell some of the asset
                    amount_to_sell = -difference_eth / tickers[f"{symbol}/ETH"]['last']
                    execute_trade(symbol, 'ETH', amount_to_sell)  # Assuming ETH is used as output
                    logging.info(f"Rebalancing: Selling {amount_to_sell:.6f} of {symbol}")
        
        update.message.reply_text("Portfolio rebalancing completed.")

    except Exception as e:
        logging.error(f"Error during rebalancing: {e}")
        update.message.reply_text("An error occurred during rebalancing.")
