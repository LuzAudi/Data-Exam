# Crypto Fetcher – CoinGecko Historical Downloader

This is a simple command-line Python application that downloads historical data from the [CoinGecko API](https://www.coingecko.com/en/api/documentation) for a given cryptocurrency and date.

You can:
- Fetch individual coin data for a specific date
- Run a daily job that downloads bitcoin, ethereum, and cardano
- Automate the daily job using Windows Task Scheduler

---

.env file
Create a .env file in the project root with your CoinGecko API key:

GECKO_KEY=your_api_key_here

You can get a key from: https://www.coingecko.com/en/api

---

Usage

Fetch data for a specific coin and date

python fetch_crypto.py 2024-12-30 bitcoin

This will save a file like:


bitcoin_2024-12-30.json

---

Logging

This app uses built-in Python logging. You will see messages in the terminal like:

INFO - Requesting https://api.coingecko.com/api/v3/coins/bitcoin/history?date=30-12-2024
INFO - Data saved to bitcoin_2024-12-30.json

# Automated Daily Execution (Windows)

To run this app every day at 3:00 AM:

1. Open Task Scheduler
2. Create a new task called FetchCryptoDaily
3. Set the trigger to Daily at 3:00 AM
4. Set the action to run:
   - Program: python
   - Arguments: C:\path\to\your\project\crypto_fetcher\fetch_crypto.py --daily

Make sure your .env file is in the project root and contains your GECKO_KEY

---

# Range Processing Mode

You can also fetch data for a specific coin over a range of dates using the --range option

Example

python crypto_fetcher/fetch_crypto.py --range 2024-05-01 2024-05-05 --coin bitcoin 