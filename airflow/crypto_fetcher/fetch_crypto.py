import os
import requests
import click
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from db import SessionLocal, CoinRawData, CoinMonthlyAggregates

# Load environment variables from .env
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("GECKO_KEY")

# Set request headers with API key
HEADERS = {"x-cg-demo-api-key": API_KEY}

# Base URL for the CoinGecko API
BASE_URL = "https://api.coingecko.com/api/v3/coins"

# Set up logging format
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def fetch_single_date(coin, date_str, store=False):
    """
    Helper function that fetches and saves data for a given coin and date.
    If --store is used, it will also insert the data into PostgreSQL.
    """
    try:
        # Parse and reformat the date for API usage
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted = dt.strftime("%d-%m-%Y")
        url = f"{BASE_URL}/{coin}/history?date={formatted}"
        logging.info(f"Fetching {coin} for {date_str} → {url}")

        # Make request
        response = requests.get(url, headers=HEADERS)

        # Save result if successful
        if response.status_code == 200:
            filename = f"{coin}_{dt.date()}.json"
            json_data = response.json()
            price = json_data.get("market_data", {}).get("current_price", {}).get("usd")

            # Save file locally
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logging.info(f"Saved to {filename}")

            # If store flag is set, insert into database
            if store:
                session = SessionLocal()

                # Insert into coin_raw_data
                stmt = insert(CoinRawData).values(
                    coin=coin,
                    date=dt.date(),
                    price=price,
                    json=json_data
                ).on_conflict_do_nothing()
                session.execute(stmt)

                # Aggregate: update monthly min and max
                year = dt.year
                month = dt.month
                result = session.query(
                    func.max(CoinRawData.price).label("max_price"),
                    func.min(CoinRawData.price).label("min_price")
                ).filter(
                    CoinRawData.coin == coin,
                    func.extract("year", CoinRawData.date) == year,
                    func.extract("month", CoinRawData.date) == month
                ).one()

                stmt2 = insert(CoinMonthlyAggregates).values(
                    coin=coin,
                    year=year,
                    month=month,
                    max_price=result.max_price,
                    min_price=result.min_price
                ).on_conflict_do_update(
                    index_elements=["coin", "year", "month"],
                    set_={
                        "max_price": result.max_price,
                        "min_price": result.min_price
                    }
                )
                session.execute(stmt2)
                session.commit()
                session.close()

        else:
            logging.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        logging.exception(f"Failed fetching {coin} on {date_str}")


@click.command()
@click.option('--daily', is_flag=True, help='Fetch data for bitcoin, ethereum, and cardano for today')
@click.option('--range', nargs=2, help='Fetch data for a coin within a date range (start_date end_date)')
@click.option('--coin', default=None, help='Coin ID to be used with --range (e.g. bitcoin)')
@click.option('--store', is_flag=True, help='Store the fetched data in PostgreSQL and update aggregates')
@click.argument('date', required=False)     # Date format: YYYY-MM-DD
@click.argument('coin_id', required=False)  # Coin identifier (e.g. bitcoin)
def fetch(daily, range, coin, store, date, coin_id):
    """
    Main function to fetch CoinGecko historical data.

    Modes of use:
    - --daily → fetch bitcoin, ethereum, and cardano for today
    - --range START_DATE END_DATE --coin bitcoin → fetch coin data for multiple dates
    - date + coin_id → fetch specific coin for specific date
    - --store → store the result in PostgreSQL and update aggregates
    """

    # Mode: Daily fetch for multiple coins
    if daily:
        coins = ["bitcoin", "ethereum", "cardano"]
        date = datetime.today().strftime("%Y-%m-%d")
        for c in coins:
            fetch_single_date(c, date, store)

    # Mode: Range fetch (loop through all dates)
    elif range:
        if not coin:
            logging.error("You must specify --coin when using --range.")
            return

        # Parse date range
        start_date = datetime.strptime(range[0], "%Y-%m-%d")
        end_date = datetime.strptime(range[1], "%Y-%m-%d")
        current = start_date

        # Loop through each day in the range
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            fetch_single_date(coin, date_str, store)
            current += timedelta(days=1)

    # Mode: Single date and coin fetch
    elif date and coin_id:
        fetch_single_date(coin_id, date, store)

    # Catch invalid usage
    else:
        logging.error("Invalid arguments. Use --help for usage instructions.")

# Entry point
if __name__ == '__main__':
    fetch()
