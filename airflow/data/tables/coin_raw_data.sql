CREATE TABLE coin_raw_data (
	coin VARCHAR NOT NULL, 
	date DATE NOT NULL, 
	price FLOAT, 
	json JSON, 
	PRIMARY KEY (coin, date)
);