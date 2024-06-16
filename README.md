Seven Bot - Binance Crypto Trading Bot

Seven Bot is an advanced cryptocurrency trading bot designed to automate your trading strategies on Binance. It combines technical analysis, machine learning, and risk management techniques to optimize your investment decisions.

Features:

* Dollar-Cost Averaging (DCA): Regularly invests a fixed amount of USDT into your chosen assets.
* Dynamic Top Coin Selection: Analyzes the top 10 coins on Binance and selects up to 3 with the highest potential for gains.
* MACD and Ichimoku Cloud Trading Strategy: Executes trades based on a combination of MACD crossovers, Ichimoku Cloud signals, and moving average trends.
* Volume Analysis: Incorporates volume spikes into the trading decision-making process.
* Dynamic Stop-Loss and Take-Profit: Adapts stop-loss and take-profit levels dynamically based on volatility and projected growth.
* Portfolio Rebalancing: Maintains your desired asset allocation by periodically rebalancing your portfolio.
* Profit Protection: Automatically sells a portion of your holdings when certain profit thresholds are reached.
* Comprehensive Reporting: Generates monthly and quarterly reports detailing your portfolio performance.
* Interactive Dashboard: Provides a real-time overview of your portfolio, performance metrics, and bot controls (using Plotly Dash).
* Telegram Bot: Offers convenient access to portfolio status updates and the ability to trigger rebalancing manually.
* Email Notifications: Sends email alerts for errors and periodic performance reports.

Installation:

1. Clone the Repository:
  git clone 
https://github.com/botshelomokoka/Seventrades

2. Create Virtual Environment:
  python3 -m venv venv
  source venv/bin/activate

3. Install Dependencies:
  pip install -r requirements.txt

4. Configure User Settings:
  - Edit the 'user.py' file to replace the placeholders with your actual Binance API keys.
  - Customize other parameters in the files (stop-loss, take-profit, risk percentage, etc.) to match your preferences.

Usage:

1. Run the Bot:
  python3 index.py

2. Access Dashboard:
  - Open the provided URL (usually http://127.0.0.1:8050/) in your web browser.

3. Telegram Commands:
  - /start: Starts the trading bot.
  - /stop: Stops the trading bot.
  - /status: Get a summary of your current portfolio.
  - /rebalance: Manually trigger portfolio rebalancing.

Important Notes:

- This bot is for educational purposes only and should not be used for actual trading without thorough testing and understanding of the risks involved.
- Cryptocurrency markets are highly volatile, and you could lose money. Always invest responsibly and never risk more than you can afford to lose.
- Review and adjust the bot's parameters and strategies based on your risk tolerance and investment goals.
- Monitor the bot's performance regularly and keep an eye on the logs for any errors.
- This bot assumes you have USDT available in your Binance account for trading.
- Ensure that your API keys have the necessary permissions for trading and withdrawals.

Contributing:

If you find any bugs or have suggestions for improvements, feel free to open an issue or create a pull request.

Disclaimer:

This bot is not financial advice. Use at your own risk. The author is not responsible for any losses incurred due to the use of this bot.


