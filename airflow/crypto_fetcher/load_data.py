import os
import json
from datetime import datetime
from crypto_fetcher.db import SessionLocal, CoinRawData, CoinMonthlyAggregates
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

DATA_DIR = "data" 

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_price(json_data):
    try:
        return json_data["market_data"]["current_price"]["usd"]
    except:
        return None

def get_date_from_filename(filename):
    parts = filename.replace(".json", "").split("_")
    return parts[0], datetime.strptime(parts[1], "%Y-%m-%d").date()

def load_all_jsons():
    session = SessionLocal()
    for file in os.listdir(DATA_DIR):
        if file.endswith(".json"):
            full_path = os.path.join(DATA_DIR, file)
            data = load_json_file(full_path)
            coin, date = get_date_from_filename(file)
            price = extract_price(data)

            stmt = insert(CoinRawData).values(
                coin=coin,
                date=date,
                price=price,
                json=data
            ).on_conflict_do_nothing()

            session.execute(stmt)
    session.commit()
    session.close()

def update_monthly_aggregates():
    session = SessionLocal()
    result = session.query(
        CoinRawData.coin,
        func.extract('year', CoinRawData.date).label('year'),
        func.extract('month', CoinRawData.date).label('month'),
        func.max(CoinRawData.price).label('max_price'),
        func.min(CoinRawData.price).label('min_price')
    ).group_by(CoinRawData.coin, 'year', 'month')

    for row in result:
        stmt = insert(CoinMonthlyAggregates).values(
            coin=row.coin,
            year=int(row.year),
            month=int(row.month),
            max_price=row.max_price,
            min_price=row.min_price
        ).on_conflict_do_update(
            index_elements=['coin', 'year', 'month'],
            set_={"max_price": row.max_price, "min_price": row.min_price}
        )
        session.execute(stmt)

    session.commit()
    session.close()

if __name__ == "__main__":
    load_all_jsons()
    update_monthly_aggregates()
