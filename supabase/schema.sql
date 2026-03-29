-- ============================================================
-- Crypto Trade AI Assistant — Schema SQL (Supabase/PostgreSQL)
-- Conforme PRD.md seção 12
-- ============================================================

-- Análise diária completa
CREATE TABLE IF NOT EXISTS daily_analysis (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at          TIMESTAMPTZ DEFAULT now(),
  date                DATE UNIQUE NOT NULL,
  symbol              TEXT DEFAULT 'BTCUSDT',

  -- Preços calculados
  price_close         NUMERIC NOT NULL,
  price_entry         NUMERIC,
  stop_loss           NUMERIC,
  take_profit         NUMERIC,
  rr_ratio            NUMERIC,
  sl_percent          NUMERIC,
  tp_percent          NUMERIC,
  atr_14              NUMERIC,

  -- Indicadores técnicos
  rsi_14              NUMERIC,
  sma_20              NUMERIC,
  sma_50              NUMERIC,
  macd_value          NUMERIC,
  macd_signal         NUMERIC,
  bb_upper            NUMERIC,
  bb_lower            NUMERIC,

  -- On-Chain
  tx_volume           NUMERIC,
  tx_count            BIGINT,
  hash_rate           NUMERIC,
  mempool_fee         NUMERIC,
  network_health      TEXT,

  -- Sentimento
  fear_greed_score    INTEGER,
  fear_greed_label    TEXT,
  news_headlines      JSONB,

  -- Sinal
  confluence_score    INTEGER NOT NULL,
  signal              TEXT CHECK (signal IN ('VERDE', 'AMARELO', 'VERMELHO')),
  score_breakdown     JSONB,

  -- Output da IA
  ai_report_technical TEXT,
  ai_report_onchain   TEXT,
  ai_report_sentiment TEXT,
  ai_report_verdict   TEXT,
  ai_model            TEXT DEFAULT 'gemini-2.0-flash',

  -- Resultado (performance tracking)
  outcome             TEXT CHECK (outcome IN ('TP_HIT', 'SL_HIT', 'MANUAL', 'OPEN', 'N/A')),
  outcome_price       NUMERIC,
  outcome_note        TEXT,
  outcome_source      TEXT CHECK (outcome_source IN ('AUTO', 'MANUAL')) DEFAULT 'AUTO',

  -- Sistema
  telegram_sent       BOOLEAN DEFAULT false,
  error_log           TEXT
);

-- Índice para consultas rápidas por data
CREATE INDEX IF NOT EXISTS idx_daily_analysis_date ON daily_analysis(date DESC);

-- ============================================================
-- Configurações do utilizador
-- ============================================================
CREATE TABLE IF NOT EXISTS settings (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  intraday_threshold  NUMERIC DEFAULT 5.0,
  symbol              TEXT DEFAULT 'BTCUSDT',
  cron_time_utc       TEXT DEFAULT '01:00',
  updated_at          TIMESTAMPTZ DEFAULT now()
);
