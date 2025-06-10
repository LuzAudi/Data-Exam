CREATE TABLE coin_monthly_aggregates (
	coin VARCHAR NOT NULL, 
	year INTEGER NOT NULL, 
	month INTEGER NOT NULL, 
	min_price FLOAT, 
	max_price FLOAT, 
	PRIMARY KEY (coin, year, month)
);