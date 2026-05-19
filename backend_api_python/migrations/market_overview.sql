-- =============================================================================
-- Market Overview - 市场概览数据表
-- 管理员上传 Excel 数据自动入库，按日期和标的记录时序
-- =============================================================================

-- 市场概览数据表（时序数据）
CREATE TABLE IF NOT EXISTS market_overview_data (
    id SERIAL PRIMARY KEY,
    data_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    data_type VARCHAR(20) NOT NULL DEFAULT 'us_market',  -- us_market / core / betting_tool
    relative_strength DECIMAL(10,2),
    strength_momentum DECIMAL(10,2),
    early_reversal DECIMAL(10,2),
    relative_price_status VARCHAR(20),      -- lead / Improving / Weakening / Lag
    relative_price_duration INTEGER,
    relative_price_return DECIMAL(10,4),
    prev_relative_price_status VARCHAR(20),
    prev_relative_price_duration INTEGER,
    d_trend VARCHAR(10),                     -- 上行趋势 / 下行趋势 / 无趋势
    d_trend_duration INTEGER,
    w_trend VARCHAR(10),
    w_trend_duration INTEGER,
    m_trend VARCHAR(10),
    m_trend_duration INTEGER,
    price_position_60d DECIMAL(10,4),        -- 0~1
    leverage_status VARCHAR(10),             -- 加杠杆 / 去杠杆
    leverage_duration INTEGER,
    leverage_return DECIMAL(10,4),
    prev_leverage_status VARCHAR(10),
    leverage_value DECIMAL(10,4),            -- 0~100
    leverage_change DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 唯一索引：(data_date, symbol) 支持 UPSERT
CREATE UNIQUE INDEX IF NOT EXISTS idx_market_overview_data_date_symbol_unique
    ON market_overview_data(data_date, symbol);
CREATE INDEX IF NOT EXISTS idx_market_overview_data_date
    ON market_overview_data(data_date);
CREATE INDEX IF NOT EXISTS idx_market_overview_data_symbol
    ON market_overview_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_overview_data_type
    ON market_overview_data(data_type);

-- 市场概览上传历史表
CREATE TABLE IF NOT EXISTS market_overview_uploads (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    data_date DATE,
    data_type VARCHAR(20),
    total_rows INTEGER DEFAULT 0,
    new_rows INTEGER DEFAULT 0,
    updated_rows INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',    -- pending / processing / completed / failed
    error_message TEXT,
    admin_id INTEGER,
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_overview_uploads_date
    ON market_overview_uploads(data_date);
CREATE INDEX IF NOT EXISTS idx_market_overview_uploads_status
    ON market_overview_uploads(status);
CREATE INDEX IF NOT EXISTS idx_market_overview_uploads_created_at
    ON market_overview_uploads(created_at);
