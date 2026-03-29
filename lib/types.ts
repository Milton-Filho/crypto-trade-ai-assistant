/**
 * TypeScript interfaces para o Crypto Trade AI Assistant.
 * Alinhadas com o contrato da API definido no agents.md.
 */

export interface ScoreBreakdown {
  rsi: number;
  bollinger: number;
  macd: number;
  sma: number;
  fear_greed: number;
  onchain: number;
}

export interface DailyAnalysis {
  id: string;
  date: string;                                          // "YYYY-MM-DD"
  symbol: string;
  signal: "VERDE" | "AMARELO" | "VERMELHO";
  confluence_score: number;                              // 0–9
  score_breakdown: ScoreBreakdown;
  price_close: number;
  price_entry: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  rr_ratio: number | null;
  sl_percent: number | null;
  tp_percent: number | null;
  rsi_14: number;
  sma_20: number;
  sma_50: number;
  macd_value: number | null;
  macd_signal: number | null;
  bb_upper: number;
  bb_lower: number;
  atr_14: number;
  fear_greed_score: number;
  fear_greed_label: string;
  network_health: string;
  news_headlines: string[];
  tx_volume: number;
  tx_count: number;
  hash_rate: number;
  mempool_fee: number;
  ai_report_technical: string;
  ai_report_onchain: string;
  ai_report_sentiment: string;
  ai_report_verdict: string;
  outcome: "TP_HIT" | "SL_HIT" | "MANUAL" | "OPEN" | "N/A";
  outcome_price: number | null;
  outcome_note: string | null;
  outcome_source: string | null;
  error_log: string | null;
  telegram_sent: boolean;
  created_at: string;
}

export interface Settings {
  id?: string;
  intraday_threshold: number;
  symbol: string;
  cron_time_utc: string;
}
