CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    amazon_url TEXT NOT NULL UNIQUE,
    asin VARCHAR(20),
    title TEXT,
    price_text VARCHAR(100),
    price_numeric NUMERIC(12,2),
    currency_code VARCHAR(10),
    availability_text TEXT,
    stock_status VARCHAR(50),
    description TEXT,
    main_image_url TEXT,
    checked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ml_item_id VARCHAR(50),
    ml_status VARCHAR(50),
    ml_price NUMERIC(12,2),
    ml_available_quantity INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS product_images (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scrape_logs (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    log_type VARCHAR(30),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);