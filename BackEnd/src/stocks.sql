-- stocks.sql
CREATE TABLE bvl_stocks (
    id SERIAL PRIMARY KEY,
    company_code INT NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    short_name VARCHAR(50),
    nemonico VARCHAR(10),
    sector_code VARCHAR(10),
    sector_description VARCHAR(100),
    last_date TIMESTAMP,
    previous_date TIMESTAMP,
    buy_price DECIMAL(15, 4),
    sell_price DECIMAL(15, 4),
    last_price DECIMAL(15, 4),
    minimum_price DECIMAL(15, 4),
    maximum_price DECIMAL(15, 4),
    opening_price DECIMAL(15, 4),
    previous_price DECIMAL(15, 4),
    negotiated_quantity INT,
    negotiated_amount DECIMAL(20, 4),
    negotiated_national_amount DECIMAL(20, 4),
    operations_number INT,
    exderecho DECIMAL(15, 4),
    percentage_change DECIMAL(10, 4),
    currency VARCHAR(10),
    unity INT,
    segment VARCHAR(50),
    created_date TIMESTAMP,
    num_neg INT,
    scrape_timestamp TIMESTAMP NOT NULL,
    -- Índices para búsquedas frecuentes
    CONSTRAINT idx_company_name UNIQUE (company_name, scrape_timestamp)
);

-- Índices adicionales para mejorar rendimiento
CREATE INDEX idx_scrape_timestamp ON bvl_stocks (scrape_timestamp);
CREATE INDEX idx_company_code ON bvl_stocks (company_code);