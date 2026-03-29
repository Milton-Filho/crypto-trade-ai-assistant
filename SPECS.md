# Technical Specifications
## Crypto Trade AI Assistant — v1.0

---

## 1. Estrutura de Pastas

```
crypto-trade-ai/
│
├── backend/
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── technical_engine.py       # Binance API + pandas-ta
│   │   ├── onchain_engine.py         # Blockchain.com + Mempool.space
│   │   ├── sentiment_engine.py       # Fear&Greed + NewsAPI
│   │   └── macro_engine.py           # Contextualização macro (via NewsAPI)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── signal_engine.py          # Score de confluência 0–9
│   │   ├── risk_manager.py           # Cálculo de Entrada, SL, TP, R/R
│   │   └── ai_analyst.py             # Monta payload + chama Gemini
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── supabase_client.py        # Leitura e escrita no banco
│   │   └── telegram_bot.py           # Envio de alertas
│   │
│   ├── prompts/
│   │   └── daily_report_v1.txt       # Prompt versionado da IA
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   └── routes/
│   │       ├── analysis.py           # GET /analysis, GET /analysis/today
│   │       ├── history.py            # GET /history, PATCH /history/{id}
│   │       └── settings.py           # GET /settings, PUT /settings
│   │
│   ├── jobs/
│   │   ├── daily_job.py              # Orquestrador principal — 01:00
│   │   └── watcher_job.py            # Vigilância intraday — cada 2h
│   │
│   ├── tests/
│   │   ├── test_technical_engine.py
│   │   ├── test_signal_engine.py
│   │   └── test_risk_manager.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── render.yaml                   # Configuração de deploy + cron jobs
│
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                  # Dashboard (hoje)
    │   ├── history/
    │   │   └── page.tsx              # Histórico 30 dias
    │   └── settings/
    │       └── page.tsx              # Configurações
    │
    ├── components/
    │   ├── ui/
    │   │   ├── SignalBadge.tsx        # Semáforo Verde/Amarelo/Vermelho
    │   │   ├── PriceCard.tsx         # Entrada / SL / TP / R/R
    │   │   ├── ScoreBar.tsx          # Barra de score 0–9
    │   │   ├── ReportBlock.tsx       # Bloco colapsável do relatório IA
    │   │   ├── IndicatorCard.tsx     # Card de indicador (RSI, MACD, etc)
    │   │   └── EditModal.tsx         # Modal de edição do histórico
    │   │
    │   └── layout/
    │       ├── Navbar.tsx
    │       └── Footer.tsx
    │
    ├── lib/
    │   ├── api.ts                    # Funções de chamada à FastAPI
    │   └── types.ts                  # TypeScript types/interfaces
    │
    ├── .env.local.example
    ├── next.config.ts
    └── tailwind.config.ts
```

---

## 2. Variáveis de Ambiente

### Backend (`backend/.env`)

```env
# Binance (sem autenticação para dados públicos)
BINANCE_BASE_URL=https://api.binance.com

# Blockchain.com On-Chain
BLOCKCHAIN_BASE_URL=https://api.blockchain.info

# Mempool.space
MEMPOOL_BASE_URL=https://mempool.space/api

# Alternative.me Fear & Greed
FEAR_GREED_URL=https://api.alternative.me/fng/

# NewsAPI
NEWS_API_KEY=your_newsapi_key_here
NEWS_BASE_URL=https://newsapi.org/v2

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_personal_chat_id

# App
SYMBOL=BTCUSDT
INTRADAY_THRESHOLD=5.0
ENVIRONMENT=production
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=https://your-backend.render.com
NEXT_PUBLIC_BINANCE_WS=wss://stream.binance.com:9443/ws/btcusdt@trade
```

---

## 3. Especificações por Módulo

---

### 3.1 `technical_engine.py`

**Responsabilidade:** Buscar dados OHLCV da Binance e calcular todos os indicadores técnicos necessários.

**Inputs:** Nenhum (usa `SYMBOL` do env)

**Output:** `dict` com os seguintes campos:

```python
{
    "price_close": float,      # Preço de fecho da última vela diária
    "rsi_14": float,           # RSI de 14 períodos
    "sma_20": float,           # Média Móvel Simples de 20 períodos
    "sma_50": float,           # Média Móvel Simples de 50 períodos
    "macd_value": float,       # Linha MACD (12/26/9)
    "macd_signal": float,      # Linha de sinal do MACD
    "macd_cross_bullish": bool,# True se MACD cruzou acima da signal hoje
    "bb_upper": float,         # Banda de Bollinger Superior (20/2.0)
    "bb_lower": float,         # Banda de Bollinger Inferior (20/2.0)
    "atr_14": float,           # ATR de 14 períodos
}
```

**Dependências:** `requests`, `pandas`, `pandas-ta`

**Tratamento de erros:**
- Retry automático: 3 tentativas com backoff exponencial (1s, 2s, 4s)
- Em caso de falha total: lança `TechnicalDataError` com mensagem descritiva

---

### 3.2 `onchain_engine.py`

**Responsabilidade:** Coletar dados reais de actividade on-chain da rede Bitcoin.

**Fontes:**
- `https://api.blockchain.info/stats` — stats gerais da rede
- `https://mempool.space/api/v1/fees/recommended` — fee rates

**Output:**

```python
{
    "tx_volume_btc": float,       # Volume total de BTC transacionado nas últimas 24h
    "tx_count": int,              # Número de transações confirmadas nas últimas 24h
    "hash_rate_th": float,        # Hash rate em TH/s
    "mempool_fee_fastest": int,   # Fee para confirmação rápida (sat/vByte)
    "network_health": str,        # "SAUDAVEL" | "CONGESTAO" | "LENTA"
}
```

**Lógica de `network_health`:**
```
hash_rate > média_30d AND tx_count > 250000  → "SAUDAVEL"
mempool_fee_fastest > 80                     → "CONGESTAO"
default                                       → "LENTA"
```

**Tratamento de erros:**
- Se Blockchain.com falhar: retorna dados parciais com flag `partial: true`
- Se Mempool.space falhar: `mempool_fee_fastest = None`, `network_health = "DESCONHECIDO"`

---

### 3.3 `sentiment_engine.py`

**Responsabilidade:** Coletar Fear & Greed Index e manchetes relevantes das últimas 24h.

**Output:**

```python
{
    "fear_greed_score": int,            # 0–100
    "fear_greed_label": str,            # "Extreme Fear" | "Fear" | "Neutral" | "Greed" | "Extreme Greed"
    "fear_greed_context": str,          # "COMPRA_HISTORICA" | "NEUTRO" | "VENDA_HISTORICA"
    "news_headlines": list[str],        # Máximo 3 manchetes mais relevantes
}
```

**Lógica de `fear_greed_context`:**
```
score 0–24   → "COMPRA_HISTORICA"
score 25–74  → "NEUTRO"
score 75–100 → "VENDA_HISTORICA"
```

**NewsAPI query:**
```python
params = {
    "q": "Bitcoin OR cryptocurrency OR Federal Reserve",
    "language": "en",
    "sortBy": "relevancy",
    "pageSize": 5,
    "from": (datetime.now() - timedelta(hours=24)).isoformat()
}
```

---

### 3.4 `signal_engine.py`

**Responsabilidade:** Receber os dados das engines e calcular o score de confluência.

**Inputs:** Output consolidado das três engines

**Lógica do score (BULLISH):**

```python
score = 0

# Análise Técnica (máx: 6 pontos)
if tech["rsi_14"] < 35:                          score += 2
if tech["price_close"] <= tech["bb_lower"]:      score += 2
if tech["macd_cross_bullish"]:                   score += 1
if tech["sma_20"] > tech["sma_50"]:              score += 1

# Sentimento (máx: 2 pontos)
if sentiment["fear_greed_score"] < 25:           score += 2

# On-Chain (máx: 1 ponto)
if onchain["network_health"] == "SAUDAVEL":      score += 1

# Total máximo: 9 pontos
```

**Determinação do sinal:**
```python
if score >= 6:   signal = "VERDE"
elif score <= 3: signal = "VERMELHO"   # Lógica bearish simétrica
else:            signal = "AMARELO"
```

**Output:**

```python
{
    "confluence_score": int,    # 0–9
    "signal": str,              # "VERDE" | "AMARELO" | "VERMELHO"
    "score_breakdown": dict,    # Detalhe de cada ponto ganho/perdido
}
```

---

### 3.5 `risk_manager.py`

**Responsabilidade:** Calcular os preços exactos de execução com base no ATR.

**Inputs:**
- `price_close: float` — preço de fecho da vela
- `atr_14: float` — ATR calculado
- `signal: str` — "VERDE" | "VERMELHO"

**Fórmulas:**

```python
# Para sinal VERDE (Compra)
price_entry = price_close
stop_loss   = round(price_close - (atr_14 * 1.5), 2)
take_profit = round(price_close + (atr_14 * 3.0), 2)

# Para sinal VERMELHO (Short)
price_entry = price_close
stop_loss   = round(price_close + (atr_14 * 1.5), 2)
take_profit = round(price_close - (atr_14 * 3.0), 2)

# R/R Ratio
rr_ratio = round((take_profit - price_entry) / abs(price_entry - stop_loss), 2)
```

**Output:**

```python
{
    "price_entry": float,
    "stop_loss": float,
    "take_profit": float,
    "rr_ratio": float,
    "sl_percent": float,    # SL em % do preço de entrada
    "tp_percent": float,    # TP em % do preço de entrada
}
```

---

### 3.6 `ai_analyst.py`

**Responsabilidade:** Montar o payload completo, chamar o Gemini 2.0 Flash e receber o relatório estruturado em quatro blocos.

**Modelo:** `gemini-2.0-flash` via `google-generativeai` SDK

**Estratégia do prompt:** O prompt é carregado do ficheiro `prompts/daily_report_v1.txt` — versionado e imutável durante a execução. Os dados são injectados como JSON no prompt.

**Output esperado da IA:** JSON com quatro campos:

```json
{
  "technical": "texto do bloco técnico...",
  "onchain": "texto do bloco on-chain...",
  "sentiment": "texto do bloco sentimento e macro...",
  "verdict": "texto do veredito final..."
}
```

**Parsing:** A resposta é extraída como JSON. Se a IA retornar texto fora do formato, o sistema tenta parsear via regex como fallback e regista o erro no `error_log` do banco.

---

### 3.7 `supabase_client.py`

**Responsabilidade:** Persistir o relatório diário e consultar histórico.

**Métodos principais:**

```python
def save_daily_analysis(payload: dict) -> str:
    """Insere ou actualiza o registo do dia. Retorna o UUID."""

def get_today_analysis() -> dict | None:
    """Retorna o registo de hoje ou None."""

def get_history(days: int = 30) -> list[dict]:
    """Retorna os últimos N dias ordenados por data decrescente."""

def update_outcome(id: str, outcome: str, price: float, note: str) -> bool:
    """Actualiza o resultado de uma operação (manual ou automático)."""

def get_settings() -> dict:
    """Retorna as configurações actuais."""

def update_settings(payload: dict) -> bool:
    """Actualiza as configurações."""
```

---

### 3.8 `telegram_bot.py`

**Responsabilidade:** Enviar mensagens formatadas ao utilizador via Telegram Bot API.

**Métodos:**

```python
def send_execution_alert(analysis: dict) -> bool:
    """Envia alerta de sinal Verde ou Vermelho com preços."""

def send_intraday_alert(current_price: float, entry_price: float, change_pct: float) -> bool:
    """Envia alerta leve de variação intraday ≥ 5%."""

def send_error_alert(message: str) -> bool:
    """Envia alerta de erro do sistema (falha de API, etc)."""
```

**Regras:**
- Sinal AMARELO → `send_execution_alert` NÃO é chamado
- Intraday → apenas entre 07:00 e 23:00 Lisboa (evitar acordar o utilizador)
- Rate limit: máximo 1 mensagem por tipo por hora

---

### 3.9 `daily_job.py`

**Responsabilidade:** Orquestrador do fluxo completo das 01:00.

**Fluxo sequencial:**

```python
async def run():
    try:
        # 1. Coleta de dados
        tech_data      = await TechnicalEngine().fetch()
        onchain_data   = await OnchainEngine().fetch()
        sentiment_data = await SentimentEngine().fetch()

        # 2. Score e sinal
        signal_result = SignalEngine().calculate(tech_data, onchain_data, sentiment_data)

        # 3. Gestão de risco
        risk_result = RiskManager().calculate(
            price_close = tech_data["price_close"],
            atr_14      = tech_data["atr_14"],
            signal      = signal_result["signal"]
        )

        # 4. Relatório da IA
        ai_report = await AIAnalyst().generate({
            **tech_data, **onchain_data, **sentiment_data,
            **signal_result, **risk_result
        })

        # 5. Persistência
        full_payload = {**tech_data, **onchain_data, **sentiment_data,
                        **signal_result, **risk_result, **ai_report}
        record_id = SupabaseClient().save_daily_analysis(full_payload)

        # 6. Notificação (apenas se não for Amarelo)
        if signal_result["signal"] != "AMARELO":
            TelegramBot().send_execution_alert(full_payload)

    except Exception as e:
        TelegramBot().send_error_alert(str(e))
        log_error(e)
```

---

### 3.10 `watcher_job.py`

**Responsabilidade:** Verificar variação de preço intraday e disparar alerta se ≥ ±5%.

**Fluxo (executado a cada 2 horas, 07:00–23:00 Lisboa):**

```python
def run():
    today = SupabaseClient().get_today_analysis()
    if not today or today["signal"] == "AMARELO":
        return  # Nada a monitorar

    entry_price   = today["price_entry"]
    current_price = fetch_current_price()  # GET simples à Binance ticker
    change_pct    = ((current_price - entry_price) / entry_price) * 100

    if abs(change_pct) >= INTRADAY_THRESHOLD:
        TelegramBot().send_intraday_alert(current_price, entry_price, change_pct)

    # Verificar se TP ou SL foi atingido (auto-update do outcome)
    if today["signal"] == "VERDE":
        if current_price >= today["take_profit"]:
            SupabaseClient().update_outcome(today["id"], "TP_HIT", current_price, "Auto")
        elif current_price <= today["stop_loss"]:
            SupabaseClient().update_outcome(today["id"], "SL_HIT", current_price, "Auto")
```

---

## 4. FastAPI — Endpoints

```
GET    /                         → Health check
GET    /analysis/today           → Análise do dia atual
GET    /analysis/history?days=30 → Histórico dos últimos N dias
PATCH  /analysis/{id}/outcome    → Editar resultado de uma análise
GET    /settings                 → Configurações atuais
PUT    /settings                 → Actualizar configurações
POST   /jobs/trigger             → Trigger manual do daily_job (dev only)
```

### Exemplo de Response — `GET /analysis/today`

```json
{
  "id": "uuid",
  "date": "2025-03-29",
  "symbol": "BTCUSDT",
  "signal": "VERDE",
  "confluence_score": 7,
  "price_close": 103200,
  "price_entry": 103200,
  "stop_loss": 99800,
  "take_profit": 110400,
  "rr_ratio": 2.12,
  "sl_percent": -3.29,
  "tp_percent": 6.97,
  "rsi_14": 31.4,
  "fear_greed_score": 22,
  "fear_greed_label": "Extreme Fear",
  "network_health": "SAUDAVEL",
  "ai_report": {
    "technical": "...",
    "onchain": "...",
    "sentiment": "...",
    "verdict": "..."
  },
  "telegram_sent": true,
  "created_at": "2025-03-29T01:08:43Z"
}
```

---

## 5. Frontend — Especificações de Componentes

### 5.1 Design System

```css
/* Paleta de Cores */
--bg-primary:     #0A0A0F;   /* Fundo principal */
--bg-secondary:   #111118;   /* Cards e painéis */
--bg-elevated:    #1A1A24;   /* Cards hover / elevated */
--border:         #2A2A38;   /* Bordas subtis */
--border-bright:  #3A3A50;   /* Bordas de separação */

/* Acentos de Sinal */
--signal-green:   #00FF88;   /* Verde neon — COMPRA */
--signal-yellow:  #FFB800;   /* Âmbar — ESPERA */
--signal-red:     #FF4466;   /* Vermelho — VENDA */

/* Texto */
--text-primary:   #F0F0FF;   /* Texto principal */
--text-secondary: #8888AA;   /* Labels e subtítulos */
--text-mono:      #C0C0DD;   /* Valores numéricos */

/* Tipografia */
--font-display: 'Syne', sans-serif;       /* Headings e semáforo */
--font-body:    'Inter', sans-serif;       /* Corpo de texto */
--font-mono:    'JetBrains Mono', mono;   /* Preços e dados */
```

### 5.2 `SignalBadge.tsx`

Exibe o sinal atual com animação de pulso. Tamanho grande no dashboard, compacto no histórico.

```tsx
interface SignalBadgeProps {
  signal: "VERDE" | "AMARELO" | "VERMELHO";
  score: number;
  size?: "lg" | "sm";
}
```

### 5.3 `PriceCard.tsx`

Card com os quatro valores de execução: Entrada, SL, TP, R/R. Usa `--font-mono` para os números. Percentagens em cor de acordo com positivo/negativo.

```tsx
interface PriceCardProps {
  entry: number;
  stopLoss: number;
  takeProfit: number;
  rrRatio: number;
  slPercent: number;
  tpPercent: number;
  signal: "VERDE" | "VERMELHO" | "AMARELO";
}
```

### 5.4 `ReportBlock.tsx`

Componente colapsável para cada bloco do relatório da IA. Header com ícone e título, corpo com o texto gerado. Expansível com animação suave.

```tsx
interface ReportBlockProps {
  type: "technical" | "onchain" | "sentiment" | "verdict";
  content: string;
  defaultOpen?: boolean;
}
```

### 5.5 Websocket — Preço em Tempo Real

```typescript
// lib/useBtcPrice.ts
const ws = new WebSocket(process.env.NEXT_PUBLIC_BINANCE_WS);
ws.onmessage = (event) => {
  const { p: price } = JSON.parse(event.data);
  setCurrentPrice(parseFloat(price));
};
```

---

## 6. Render.yaml — Deploy e Cron Jobs

```yaml
services:
  - type: web
    name: crypto-trade-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - fromGroup: crypto-trade-secrets

  - type: cron
    name: daily-analysis
    env: python
    schedule: "0 1 * * *"        # 01:00 UTC (= 01:00 Lisboa inverno / 02:00 verão)
    buildCommand: pip install -r requirements.txt
    startCommand: python -m jobs.daily_job
    envVars:
      - fromGroup: crypto-trade-secrets

  - type: cron
    name: intraday-watcher
    env: python
    schedule: "0 7,9,11,13,15,17,19,21,23 * * *"   # Cada 2h, 07:00–23:00 UTC
    buildCommand: pip install -r requirements.txt
    startCommand: python -m jobs.watcher_job
    envVars:
      - fromGroup: crypto-trade-secrets
```

---

## 7. Requirements.txt

```txt
# Framework
fastapi==0.111.0
uvicorn==0.30.0

# Data
requests==2.31.0
pandas==2.2.2
pandas-ta==0.3.14b0
numpy==1.26.4

# IA
google-generativeai==0.7.0

# Banco de dados
supabase==2.5.0

# Utilitários
python-dotenv==1.0.1
tenacity==8.3.0       # Retry automático com backoff
pydantic==2.7.0
httpx==0.27.0

# Testes
pytest==8.2.0
pytest-asyncio==0.23.7
```

---

## 8. Prompt da IA — `prompts/daily_report_v1.txt`

*Ver documento separado: `PROMPT_PRINCIPAL.md`*

---

## 9. Checklist de Qualidade

### Backend
- [ ] Todos os módulos têm `try/except` com fallback definido
- [ ] Variáveis de ambiente validadas no startup via Pydantic Settings
- [ ] Retry automático em todas as chamadas externas (tenacity)
- [ ] Logs estruturados em JSON para fácil parsing
- [ ] Nenhum dado fictício ou hardcoded em produção

### Frontend
- [ ] Sem fontes genéricas (Inter como fallback apenas)
- [ ] Todos os valores numéricos usam `--font-mono`
- [ ] Websocket com reconnect automático em caso de queda
- [ ] Estados de loading para todas as chamadas à API
- [ ] Skeleton screens nos cards enquanto dados carregam
- [ ] Responsivo: 375px / 768px / 1280px / 1440px

### Segurança
- [ ] SUPABASE_SERVICE_KEY nunca exposta no frontend
- [ ] CORS configurado para aceitar apenas domínio Vercel
- [ ] Rate limiting no endpoint `POST /jobs/trigger`
- [ ] Variáveis sensíveis apenas no Render Secret Group