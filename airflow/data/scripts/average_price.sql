SELECT
  coin,
  EXTRACT(YEAR FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  ROUND(AVG(price)::numeric, 2) AS average_price_usd
FROM
  coin_raw_data
GROUP BY
  coin, year, month
ORDER BY
  coin, year, month;
