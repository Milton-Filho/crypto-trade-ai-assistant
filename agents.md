# AGENT.md
## Crypto Trade AI Assistant

> Este ficheiro é lido automaticamente por agentes de IA (Claude Code, Cursor, Copilot, etc.)
> antes de qualquer interacção com o código. Define as regras absolutas do projecto.

---

## IDENTIDADE DO PROJECTO

**Nome:** Crypto Trade AI Assistant  
**Tipo:** Sistema pessoal de análise diária de Bitcoin para swing trade  
**Uso:** Estritamente pessoal — um único utilizador  
**Filosofia:** Cloud native, custo zero, sem dados fictícios, sem magia escondida  

---

## STACK

```
Backend   → Python 3.11 + FastAPI          → Render (free tier)
Cron Jobs → Render Cron Services           → Render (free tier)
Database  → PostgreSQL via supabase-py     → Supabase (free tier)
AI        → Gemini 2.0 Flash               → Google AI Studio (free tier)
Frontend  → Next.js 14 App Router          → Vercel (free tier)
Alerts    → Telegram Bot API               → Telegram (free)
```

---

## ESTRUTURA DO PROJECTO

```
crypto-trade-ai/
├── AGENT.md                          ← este ficheiro
├── PRD.md                            ← requisitos do produto
├── SPECS.md                          ← especificações técnicas detalhadas
├── PROMPT_PRINCIPAL.md               ← instrução mestra para sessões de desenvolvimento
├── PROMPTS_POR_FASE.md               ← prompts por fase de desenvolvimento
│
├── backend/
│   ├── engines/
│   │   ├── technical_engine.py       ← Binance API + pandas-ta
│   │   ├── onchain_engine.py         ← Blockchain.com + Mempool.space
│   │   └── sentiment_engine.py       ← Fear&Greed + NewsAPI
│   ├── core/
│   │   ├── signal_engine.py          ← score de confluência 0–9
│   │   ├── risk_manager.py           ← cálculo de Entrada, SL, TP, R/R
│   │   └── ai_analyst.py             ← integração Gemini 2.0 Flash
│   ├── integrations/
│   │   ├── supabase_client.py        ← persistência
│   │   └── telegram_bot.py           ← notificações
│   ├── prompts/
│   │   └── daily_report_v1.txt       ← prompt da IA (imutável em runtime)
│   ├── api/
│   │   ├── main.py                   ← FastAPI app
│   │   └── routes/
│   │       ├── analysis.py
│   │       ├── history.py
│   │       ├── settings.py
│   │       └── jobs.py               ← dev only
│   ├── jobs/
│   │   ├── daily_job.py              ← orquestrador 01:00 Lisboa
│   │   └── watcher_job.py            ← vigilância intraday cada 2h
│   ├── tests/
│   ├── config.py                     ← Pydantic Settings + validação de env vars
│   ├── requirements.txt
│   └── render.yaml
│
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                  ← Dashboard (hoje)
    │   ├── history/page.tsx          ← Histórico 30 dias
    │   └── settings/page.tsx         ← Configurações
    ├── components/ui/
    │   ├── SignalBadge.tsx
    │   ├── PriceCard.tsx
    │   ├── ScoreBar.tsx
    │   ├── ReportBlock.tsx
    │   ├── IndicatorCard.tsx
    │   └── EditModal.tsx
    ├── lib/
    │   ├── api.ts
    │   └── types.ts
    ├── tailwind.config.ts
    └── next.config.ts
```

---

## REGRAS ABSOLUTAS

### Nunca faças isto

```
❌ Dados fictícios ou hardcoded em produção (ex: return {"netflow": "Bullish"})
❌ Chaves de API, tokens ou URLs de produção no código fonte
❌ Lógica de negócio no frontend (cálculos, scores, indicadores)
❌ Construir o prompt da IA via f-string no código — ele vive em prompts/daily_report_v1.txt
❌ Silenciar erros com except: pass ou except Exception: return None
❌ Campos no banco não definidos no schema do Supabase
❌ Componentes React sem TypeScript interfaces
❌ Emojis como ícones de UI — usa Lucide React
❌ Fontes genéricas como primária (Arial, system-ui, Roboto)
❌ Cores hardcoded no CSS fora das CSS variables
❌ Saltar fases do roadmap — cada fase depende da anterior
```

### Sempre faças isto

```
✅ try/except com erro específico em toda chamada a API externa
✅ Retry automático com tenacity (3 tentativas, backoff 1s/2s/4s)
✅ Validar variáveis de ambiente no startup via config.py
✅ Documentar o fallback de cada integração nos comentários
✅ Type hints em todas as funções públicas Python
✅ Interfaces TypeScript para todos os dados da API
✅ JetBrains Mono para qualquer valor numérico no frontend
✅ Logs estruturados com: módulo, operação, duração, resultado
✅ Alerta Telegram em qualquer falha crítica do sistema
✅ Testar cada módulo isoladamente antes de integrar
```

---

## ARQUITECTURA DE SINAL

### Score de Confluência (0–9)

```python
score = 0
if rsi_14 < 35:                    score += 2   # Zona de sobrevenda
if price_close <= bb_lower:        score += 2   # Toque na banda inferior
if macd_cross_bullish:             score += 1   # Cruzamento bullish
if sma_20 > sma_50:                score += 1   # Tendência de alta
if fear_greed_score < 25:          score += 2   # Medo Extremo
if network_health == "SAUDAVEL":   score += 1   # Rede Bitcoin saudável
```

### Semáforo

```
Score 6–9  →  VERDE    →  Alerta Telegram disparado
Score 4–5  →  AMARELO  →  Silêncio total no Telegram
Score 0–3  →  VERMELHO →  Alerta Telegram disparado
```

### Gestão de Risco (ATR × multiplicadores)

```python
# VERDE (Compra)
stop_loss   = price_close - (atr_14 * 1.5)
take_profit = price_close + (atr_14 * 3.0)

# VERMELHO (Short)
stop_loss   = price_close + (atr_14 * 1.5)
take_profit = price_close - (atr_14 * 3.0)

# R/R mínimo esperado: 1:2
rr_ratio = abs(take_profit - price_close) / abs(stop_loss - price_close)
```

---

## FLUXO DO SISTEMA

### Job Diário (01:00 Lisboa = 01:00 UTC inverno)

```
TechnicalEngine.fetch()      → dict com RSI, MACD, Bollinger, ATR, SMAs
OnchainEngine.fetch()        → dict com hash_rate, tx_count, mempool_fee
SentimentEngine.fetch()      → dict com fear_greed_score, news_headlines
         ↓
SignalEngine.calculate()     → signal, confluence_score, score_breakdown
RiskManager.calculate()      → price_entry, stop_loss, take_profit, rr_ratio
         ↓
AIAnalyst.generate()         → {technical, onchain, sentiment, verdict}
         ↓
SupabaseClient.save()        → persiste tudo na tabela daily_analysis
         ↓
Se signal ≠ AMARELO → TelegramBot.send_execution_alert()
```

### Job Intraday (cada 2h, 07:00–23:00 Lisboa)

```
Binance ticker → preço actual
SupabaseClient.get_today() → price_entry do dia
abs((current - entry) / entry * 100) >= 5.0% → TelegramBot.send_intraday_alert()
current >= take_profit → SupabaseClient.update_outcome("TP_HIT")
current <= stop_loss   → SupabaseClient.update_outcome("SL_HIT")
```

---

## INTERFACES PRINCIPAIS

### Output do TechnicalEngine

```python
{
    "price_close": float,
    "rsi_14": float,
    "sma_20": float,
    "sma_50": float,
    "macd_value": float,
    "macd_signal": float,
    "macd_cross_bullish": bool,
    "bb_upper": float,
    "bb_lower": float,
    "atr_14": float,
}
```

### Output do OnchainEngine

```python
{
    "tx_volume_btc": float,
    "tx_count": int,
    "hash_rate_th": float,
    "mempool_fee_fastest": int,
    "network_health": str,   # "SAUDAVEL" | "CONGESTAO" | "LENTA" | "DESCONHECIDO"
    "partial": bool,         # True se algum endpoint falhou
}
```

### Output do SentimentEngine

```python
{
    "fear_greed_score": int,           # 0–100
    "fear_greed_label": str,
    "fear_greed_context": str,         # "COMPRA_HISTORICA" | "NEUTRO" | "VENDA_HISTORICA"
    "news_headlines": list[str],       # máx 3 títulos
}
```

### Output do SignalEngine

```python
{
    "signal": str,                     # "VERDE" | "AMARELO" | "VERMELHO"
    "confluence_score": int,           # 0–9
    "score_breakdown": {
        "rsi": int, "bollinger": int, "macd": int,
        "sma": int, "fear_greed": int, "onchain": int
    }
}
```

### Output do RiskManager

```python
{
    "price_entry": float,
    "stop_loss": float | None,         # None se AMARELO
    "take_profit": float | None,       # None se AMARELO
    "rr_ratio": float | None,
    "sl_percent": float | None,
    "tp_percent": float | None,
}
```

### Response da API — GET /analysis/today

```typescript
interface DailyAnalysis {
  id: string
  date: string                         // "YYYY-MM-DD"
  symbol: string
  signal: "VERDE" | "AMARELO" | "VERMELHO"
  confluence_score: number             // 0–9
  score_breakdown: ScoreBreakdown
  price_close: number
  price_entry: number | null
  stop_loss: number | null
  take_profit: number | null
  rr_ratio: number | null
  sl_percent: number | null
  tp_percent: number | null
  rsi_14: number
  sma_20: number
  sma_50: number
  macd_value: number
  macd_signal: number
  bb_upper: number
  bb_lower: number
  atr_14: number
  fear_greed_score: number
  fear_greed_label: string
  network_health: string
  news_headlines: string[]
  ai_report: {
    technical: string
    onchain: string
    sentiment: string
    verdict: string
  }
  outcome: "TP_HIT" | "SL_HIT" | "MANUAL" | "OPEN" | "N/A"
  telegram_sent: boolean
  created_at: string
}
```

---

## DESIGN SYSTEM (Frontend)

### Tokens de cor (CSS variables obrigatórias)

```css
--bg-primary:     #0A0A0F;   /* fundo principal */
--bg-secondary:   #111118;   /* cards */
--bg-elevated:    #1A1A24;   /* cards hover */
--border:         #2A2A38;   /* bordas subtis */
--border-bright:  #3A3A50;   /* separadores */
--signal-green:   #00FF88;   /* VERDE */
--signal-yellow:  #FFB800;   /* AMARELO */
--signal-red:     #FF4466;   /* VERMELHO */
--text-primary:   #F0F0FF;
--text-secondary: #8888AA;
--text-mono:      #C0C0DD;   /* apenas valores numéricos */
```

### Tipografia

```
Syne          → display, headings, semáforo
Inter         → corpo de texto, labels
JetBrains Mono → TODOS os valores numéricos sem excepção
```

### Princípios UI

```
Dark mode nativo — sem toggle na v1
Glassmorphism subtil — backdrop-blur-sm + border rgba(255,255,255,0.08)
Estética Web3 DApp — clean, denso em dados, zero decoração desnecessária
Ícones: Lucide React — zero emojis como ícones de interface
Server Components por defeito — "use client" só com useState/useEffect/WebSocket
```

---

## ENDPOINTS DA API

```
GET    /                          → health check
GET    /analysis/today            → análise do dia
GET    /analysis/history?days=30  → histórico
PATCH  /analysis/{id}/outcome     → editar resultado
GET    /settings                  → configurações
PUT    /settings                  → actualizar configurações
POST   /jobs/trigger              → trigger manual (dev only, ENVIRONMENT != production)
```

---

## VARIÁVEIS DE AMBIENTE NECESSÁRIAS

### Backend

```bash
BINANCE_BASE_URL          # https://api.binance.com
BLOCKCHAIN_BASE_URL       # https://api.blockchain.info
MEMPOOL_BASE_URL          # https://mempool.space/api
FEAR_GREED_URL            # https://api.alternative.me/fng/
NEWS_API_KEY              # chave NewsAPI.org
NEWS_BASE_URL             # https://newsapi.org/v2
GEMINI_API_KEY            # chave Google AI Studio
GEMINI_MODEL              # gemini-2.0-flash
SUPABASE_URL              # URL do projecto Supabase
SUPABASE_SERVICE_KEY      # service role key (nunca a anon key)
TELEGRAM_BOT_TOKEN        # token do bot
TELEGRAM_CHAT_ID          # chat ID pessoal
FRONTEND_URL              # URL de produção Vercel (para CORS)
SYMBOL                    # BTCUSDT
INTRADAY_THRESHOLD        # 5.0
ENVIRONMENT               # development | production
DEV_API_KEY               # chave para o endpoint /jobs/trigger
```

### Frontend

```bash
NEXT_PUBLIC_API_URL       # URL da FastAPI no Render
NEXT_PUBLIC_BINANCE_WS    # wss://stream.binance.com:9443/ws/btcusdt@trade
```

---

## SCHEMA DO BANCO (Supabase)

Tabelas: `daily_analysis` e `settings`  
Definição completa: ver `PRD.md` secção 12 ou `database/schema.sql`

Campos críticos da `daily_analysis`:

```sql
signal       TEXT  CHECK (signal IN ('VERDE','AMARELO','VERMELHO'))
outcome      TEXT  CHECK (outcome IN ('TP_HIT','SL_HIT','MANUAL','OPEN','N/A'))
outcome_source TEXT CHECK (outcome_source IN ('AUTO','MANUAL'))
date         DATE  UNIQUE NOT NULL
```

---

## TRATAMENTO DE ERROS — CONTRATO

Todo módulo que chame APIs externas deve seguir este padrão:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4)
)
def fetch_external_data() -> dict:
    """Docstring com: o que faz, o que retorna, o que lança."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return parse(response.json())
    except requests.exceptions.Timeout:
        raise ExternalAPIError("Timeout ao chamar XYZ API")
    except requests.exceptions.HTTPError as e:
        raise ExternalAPIError(f"HTTP {e.response.status_code} em XYZ API")
    except Exception as e:
        raise ExternalAPIError(f"Erro inesperado em XYZ API: {str(e)}")
```

Falha crítica (após 3 tentativas) → sempre chega via `TelegramBot.send_error_alert()`

---

## CONVENÇÕES DE COMMITS

```
feat(engines): adiciona OnchainEngine com Blockchain.com + Mempool.space
fix(signal): corrige detecção de cruzamento MACD na vela actual
refactor(risk): extrai cálculo de percentagem para método privado
test(signal): adiciona cenário de score máximo bullish
docs(api): documenta response de GET /analysis/today
chore(deps): actualiza pandas-ta para 0.3.14b0
```

---

## QUANDO TENS DÚVIDAS

1. **Sobre requisitos** → consulta `PRD.md`
2. **Sobre interfaces e estrutura** → consulta `SPECS.md`
3. **Sobre regras de desenvolvimento** → consulta `PROMPT_PRINCIPAL.md`
4. **Sobre o que implementar nesta fase** → consulta `PROMPTS_POR_FASE.md`
5. **Sobre o schema do banco** → consulta `database/schema.sql`

Se a dúvida não estiver em nenhum destes documentos: toma a decisão mais simples e conservadora, e documenta-a num comentário no código com o prefixo `# DECISION:`.