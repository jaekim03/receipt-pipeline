CREATE TABLE IF NOT EXISTS receipt (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    vendor VARCHAR(255),
    amount NUMERIC(10,2),
    currency VARCHAR(3),
    receipt_date DATE,
    submitted_by VARCHAR(255),
    raw_text TEXT
);