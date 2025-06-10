from sqlalchemy import create_engine, Column, String, Date, Float, JSON, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# Connection settings
POSTGRES_USER = os.getenv("POSTGRES_USER", "airflow")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")
POSTGRES_DB = os.getenv("POSTGRES_DB", "airflow")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class CoinRawData(Base):
    __tablename__ = 'coin_raw_data'
    coin = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Float)
    json = Column(JSON)
    __table_args__ = (PrimaryKeyConstraint('coin', 'date'),)


class CoinMonthlyAggregates(Base):
    __tablename__ = 'coin_monthly_aggregates'
    coin = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    min_price = Column(Float)
    max_price = Column(Float)
    __table_args__ = (PrimaryKeyConstraint('coin', 'year', 'month'),)
