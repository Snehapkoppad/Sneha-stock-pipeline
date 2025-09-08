CREATE TABLE IF NOT EXISTS stock_data (
    timestamp TIMESTAMP PRIMARY KEY,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);
