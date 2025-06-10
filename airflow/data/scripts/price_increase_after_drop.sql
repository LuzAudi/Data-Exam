
-- Detect if the price has dropped compared to the previous day using LAG
WITH price_with_diff AS (
  SELECT
    coin,
    date,
    price,
    json,
    LAG(price) OVER (PARTITION BY coin ORDER BY date) AS previous_price
  FROM coin_raw_data
),

-- Mark if that day was a fall
marked_falls AS (
  SELECT *,
    CASE
      WHEN previous_price IS NOT NULL AND price < previous_price THEN 1
      ELSE 0
    END AS is_fall
  FROM price_with_diff
),

-- Assign a group to each sequence using a group counter
grouped_falls AS (
  SELECT *,
    SUM(CASE WHEN is_fall = 0 THEN 1 ELSE 0 END) OVER (PARTITION BY coin ORDER BY date ROWS UNBOUNDED PRECEDING) AS fall_group
  FROM marked_falls
),

-- Calculate how many days in a row each group fell into
fall_sequences AS (
  SELECT
    coin,
    fall_group,
    COUNT(*) AS days_falling,
    MAX(date) AS last_fall_date
  FROM grouped_falls
  WHERE is_fall = 1
  GROUP BY coin, fall_group
  HAVING COUNT(*) > 3
),

-- Find the day after the drop and calculate the increase
fall_with_increase AS (
  SELECT
    f.coin,
    f.last_fall_date,
    r.price AS price_after,
    g.price AS price_before,
    (r.price - g.price) AS price_increase
  FROM fall_sequences f
  JOIN grouped_falls g ON f.coin = g.coin AND f.last_fall_date = g.date
  JOIN grouped_falls r ON f.coin = r.coin AND r.date = f.last_fall_date + INTERVAL '1 day'
),

-- Get the current market_cap from the JSON (last date per coin)
latest_market_cap AS (
  SELECT DISTINCT ON (coin)
    coin,
    json -> 'market_data' -> 'market_cap' ->> 'usd' AS market_cap_usd
  FROM coin_raw_data
  ORDER BY coin, date DESC
)

-- Average the increase and combine it with the market cap
SELECT
  f.coin,
  ROUND(AVG(f.price_increase)::numeric, 2) AS avg_price_increase,
  lm.market_cap_usd
FROM fall_with_increase f
JOIN latest_market_cap lm ON f.coin = lm.coin
GROUP BY f.coin, lm.market_cap_usd
ORDER BY f.coin;
