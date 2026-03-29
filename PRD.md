# Product Requirements Document (PRD)
## Crypto Trade AI Assistant — v1.0

---

## 1. Visão do Produto

**Nome:** Crypto Trade AI Assistant  
**Tagline:** *Análise institucional. Execução pessoal.*  
**Versão:** 1.0  
**Última atualização:** Março 2025  
**Owner:** Uso estritamente pessoal  

### 1.1 Resumo Executivo

Sistema pessoal, cloud native e de custo zero que analisa o Bitcoin diariamente à **01:00 (Lisboa)**, cruza dados técnicos, on-chain reais, de sentimento e macro, calcula um score de confluência de 0–9 e entrega de manhã um relatório estruturado em quatro blocos gerado por IA — com veredito claro, preços de execução calculados matematicamente e explicações didáticas que constroem repertório analítico ao longo do tempo. Alertas Telegram apenas quando há sinal acionável. Silêncio total em dias indecisivos.

### 1.2 Problema Central

O utilizador tem acesso a múltiplas fontes de dados de mercado mas não consegue sintetizá-las em conjunto para tomar uma decisão de swing trade com confiança. O problema não é falta de dados — é falta de síntese.

### 1.3 Solução

Uma camada de inteligência artificial (Gemini 2.0 Flash) que recebe um payload estruturado com todas as camadas de análise, calcula automaticamente um score de confluência, e produz um relatório didático com veredito + preços de execução — entregue de forma autónoma, sem intervenção manual.

---

## 2. Objetivos do Produto

| # | Objetivo | Métrica de Sucesso |
|---|----------|-------------------|
| 1 | Automatizar a síntese de dados de mercado | Sistema gera relatório diário sem falhas por 30 dias consecutivos |
| 2 | Fornecer sinais acionáveis com gestão de risco | Todo sinal Verde/Vermelho inclui Entrada, SL, TP e R/R |
| 3 | Reduzir fadiga de decisão | Zero alertas Telegram em dias com sinal Amarelo |
| 4 | Educar progressivamente o utilizador | Relatório explica o raciocínio de cada indicador de forma didática |
| 5 | Construir diário de trading auditável | Histórico de 30 dias com registo automático de TP/SL atingido |

---

## 3. Público-Alvo

- **Utilizador único:** uso estritamente pessoal
- **Perfil:** Investidor/Trader nível iniciante-a-intermédio
- **Foco:** Swing trade em Bitcoin (operações de dias a poucas semanas)
- **Contexto geográfico:** Portugal (UTC+0/UTC+1) — relevante para timing dos cron jobs

---

## 4. Arquitetura Técnica

### 4.1 Stack Cloud Native (Custo Zero)

| Camada | Tecnologia | Plataforma |
|--------|-----------|-----------|
| Frontend | Next.js 14 (App Router) | Vercel (free tier) |
| Backend | Python 3.11 + FastAPI | Render (free tier) |
| Agendamento | Cron Jobs nativos do Render | Render |
| Banco de Dados | PostgreSQL | Supabase (free tier) |
| Inteligência Artificial | Gemini 2.0 Flash | Google AI Studio (free tier) |
| Notificações | Telegram Bot API | Telegram (gratuito) |

### 4.2 Ritmo Operacional

**Modo Analítico — 01:00 Lisboa (diário)**
```
01:00 → Cron dispara main.py
01:01 → Coleta dados (Técnico + On-Chain + Sentimento + Macro)
01:03 → Calcula score de confluência
01:04 → Calcula Entrada, SL, TP, R/R via ATR
01:05 → Chama Gemini 2.0 Flash com payload completo
01:07 → Persiste relatório no Supabase
01:08 → Se sinal ≠ AMARELO → dispara Telegram
```

**Modo Vigilante — A cada 2 horas (07:00–23:00 Lisboa)**
```
A cada 2h → watcher.py verifica preço atual vs entrada sugerida do dia
Se variação ≥ ±5% → Telegram envia alerta leve de revisão
Sem chamada à IA. Sem recálculo de indicadores.
```

---

## 5. Integrações de Dados

### 5.1 Análise Técnica
- **Fonte:** Binance API (`/api/v3/klines`) — gratuita, sem autenticação
- **Intervalo:** Velas diárias (`1d`), 100 períodos
- **Indicadores calculados via `pandas-ta`:**

| Indicador | Parâmetros | Sinal |
|-----------|-----------|-------|
| RSI | 14 períodos | < 35 = bullish / > 65 = bearish |
| SMA curta | 20 períodos | Cruzamento acima de SMA50 = bullish |
| SMA longa | 50 períodos | Referência de tendência |
| MACD | 12/26/9 | Cruzamento acima da signal line = bullish |
| Bandas de Bollinger | 20/2.0 | Preço < banda inferior = bullish |
| ATR | 14 períodos | Base para cálculo de SL e TP |

### 5.2 Dados On-Chain (Reais)
- **Fonte primária:** Blockchain.com API (gratuita, sem registo)
  - Volume de transações diário
  - Número de transações únicas
  - Hash rate da rede
- **Fonte secundária:** Mempool.space API (gratuita, sem registo)
  - Fee rate médio (sat/vByte)
  - Congestionamento da mempool
- **Interpretação:** Actividade elevada + hash rate crescente = rede saudável = bullish

### 5.3 Sentimento
- **Fonte:** Alternative.me Crypto Fear & Greed Index (gratuita)
  - Score 0–100
  - Classificação textual
- **Interpretação:** Score < 25 (Medo Extremo) = oportunidade de compra histórica

### 5.4 Macro e Notícias
- **Fonte:** NewsAPI.org (free tier — 100 req/dia)
  - Palavras-chave: "Bitcoin", "Federal Reserve", "crypto regulation", "inflation"
  - Últimas 24 horas
- **Interpretação:** A IA recebe as 3 manchetes mais relevantes e contextualiza no relatório

---

## 6. Lógica de Sinal — Score de Confluência

O sistema calcula um **score de 0 a 9** somando sinais bullish. A cor do semáforo deriva do score:

| Score | Sinal | Ação |
|-------|-------|------|
| 0–3 | 🔴 VERMELHO | Venda / Short — lógica inversa |
| 4–5 | 🟡 AMARELO | Espera — sem alerta Telegram |
| 6–9 | 🟢 VERDE | Compra — alerta Telegram disparado |

**Composição do Score:**

| Critério | Pontos |
|----------|--------|
| RSI < 35 (zona de sobrevenda) | +2 |
| Preço ≤ Banda de Bollinger Inferior | +2 |
| MACD cruzou acima da signal line | +1 |
| SMA20 > SMA50 (tendência de alta) | +1 |
| Fear & Greed < 25 (Medo Extremo) | +2 |
| Exchange Netflow negativo (saída de BTC) | +1 |

> **Nota:** Para o sinal VERMELHO, a lógica é invertida — RSI > 65, preço ≥ Bollinger Superior, MACD cruzou abaixo, SMA20 < SMA50, Fear & Greed > 75.

---

## 7. Gestão de Risco — Cálculo de Preços

Todos os preços são calculados com base no **ATR de 14 períodos** (Average True Range), que mede a volatilidade real do ativo:

```
Stop-Loss   = Preço Atual − (ATR × 1.5)   [para compra]
Take-Profit = Preço Atual + (ATR × 3.0)   [para compra]
R/R Ratio   = (TP - Entrada) / (Entrada - SL)
```

A relação risco/retorno mínima aceitável é **1:2** — o Take-Profit é sempre o dobro do risco assumido.

---

## 8. Relatório Diário da IA

### 8.1 Estrutura do Output

O relatório é gerado pela IA em quatro blocos fixos:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ANÁLISE TÉCNICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Leitura didática dos indicadores: RSI, MACD,
Bollinger, SMAs — o que cada um significa AGORA]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 ON-CHAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Leitura da actividade da rede Bitcoin:
hash rate, volume de transações, mempool]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😨 SENTIMENTO & MACRO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Fear & Greed contextualizado + manchetes
relevantes das últimas 24h]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 VEREDITO FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 SINAL: COMPRA | Score: 7/9

📥 Entrada:      $103,200
🛑 Stop-Loss:    $99,800   (-3.3%)
🎯 Take-Profit:  $110,400  (+7.0%)
⚖️  R/R Ratio:   1 : 2.12
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 9. Casos de Uso

### 9.1 UC-01 — Análise Diária Automática
**Actor:** Sistema (cron job)  
**Trigger:** 01:00 Lisboa  
**Fluxo:** Coleta dados → Score → IA → Supabase → Telegram (se aplicável)  
**Resultado:** Relatório disponível no dashboard quando utilizador acorda

### 9.2 UC-02 — Alerta de Execução
**Actor:** Sistema (Telegram Bot)  
**Trigger:** Score ≥ 6 (VERDE) ou Score ≤ 3 (VERMELHO)  
**Fluxo:** Telegram envia mensagem compacta com semáforo + preços  
**Resultado:** Notificação push recebida antes das 08:00

### 9.3 UC-03 — Alerta Intraday
**Actor:** Sistema (watcher.py)  
**Trigger:** Variação de preço ≥ ±5% face ao ponto de entrada do dia  
**Fluxo:** watcher.py verifica preço atual, compara, dispara Telegram leve  
**Resultado:** Utilizador é alertado para rever posição

### 9.4 UC-04 — Consulta do Dashboard
**Actor:** Utilizador  
**Trigger:** Acesso ao painel web  
**Fluxo:** Dashboard carrega análise do dia + histórico dos últimos 30 dias  
**Resultado:** Visão completa do estado do mercado e histórico de sinais

### 9.5 UC-05 — Edição do Histórico
**Actor:** Utilizador  
**Trigger:** Clique em "Editar" numa linha do histórico  
**Fluxo:** Modal inline com campos editáveis (resultado real da operação)  
**Resultado:** Registo atualizado com a decisão real tomada pelo utilizador

---

## 10. Interface — Dashboard Web

### 10.1 Estética e Design

- **Inspiração:** DApps Web3 (Uniswap, Aave, GMX) — clean, data-first, dark-native
- **Modo:** Dark mode primário, sem toggle light/dark na v1
- **Paleta:** Fundos escuros profundos (#0A0A0F, #111118), acentos elétricos (verde neon para VERDE, âmbar para AMARELO, vermelho para VERMELHO), tipografia monoespaçada para dados
- **Tipografia:** Display font geométrica para headings + fonte mono para valores numéricos
- **Estilo:** Glassmorphism subtil nos cards, sem gradientes genéricos de IA, sem elementos decorativos desnecessários
- **Filosofia:** Cada pixel serve um dado. UI invisível, dados visíveis.

### 10.2 Páginas e Componentes

**Página 1 — Dashboard (hoje)**
- Header com preço atual do BTC em tempo real (websocket Binance)
- Semáforo grande com score de confluência
- Bloco de preços: Entrada / SL / TP / R/R
- Relatório da IA em quatro blocos colapsáveis
- Indicadores em cards: RSI, MACD, Fear & Greed, Score

**Página 2 — Histórico (30 dias)**
- Tabela com: Data, Sinal, Entrada, SL, TP, R/R, Resultado (Auto/Manual), Editar
- Resultado automático: watcher.py atualiza quando TP ou SL é atingido
- Edição manual: botão inline abre modal com campos editáveis

**Página 3 — Configurações**
- Threshold do alerta intraday (default: 5%)
- Par de moeda (default: BTCUSDT)
- Horário do cron (default: 01:00)

---

## 11. Notificações Telegram

### 11.1 Alerta de Execução (01:00)
```
🟢 SINAL DE COMPRA — BTC/USDT

📥 Entrada:     $103,200
🛑 Stop-Loss:   $99,800 (-3.3%)
🎯 Take-Profit: $110,400 (+7.0%)
⚖️  R/R: 1:2.1 | Score: 7/9

→ Confluência: RSI sobrevendido + Medo Extremo
  + Saída líquida das exchanges

Ver relatório completo: [link dashboard]
```

### 11.2 Alerta Intraday (watcher.py)
```
⚠️ ALERTA DE MOVIMENTO — BTC/USDT

BTC subiu 5.3% desde o sinal de hoje.
Preço atual: $108,700 | Entrada: $103,200

Considere rever a posição.
```

### 11.3 Regra de Silêncio
- Sinal AMARELO → zero mensagens Telegram
- Sem relatório no Telegram — apenas no dashboard

---

## 12. Banco de Dados — Schema

```sql
-- Análise diária completa
CREATE TABLE daily_analysis (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at      timestamptz DEFAULT now(),
  date            date UNIQUE NOT NULL,
  symbol          text DEFAULT 'BTCUSDT',

  -- Preços calculados
  price_close     numeric NOT NULL,
  price_entry     numeric,
  stop_loss       numeric,
  take_profit     numeric,
  rr_ratio        numeric,
  atr_14          numeric,

  -- Indicadores técnicos
  rsi_14          numeric,
  sma_20          numeric,
  sma_50          numeric,
  macd_value      numeric,
  macd_signal     numeric,
  bb_upper        numeric,
  bb_lower        numeric,

  -- On-Chain
  tx_volume       numeric,
  tx_count        bigint,
  hash_rate       numeric,
  mempool_fee     numeric,

  -- Sentimento
  fear_greed_score      integer,
  fear_greed_label      text,
  news_headlines        jsonb,  -- array de strings

  -- Sinal
  confluence_score      integer NOT NULL,
  signal                text CHECK (signal IN ('VERDE','AMARELO','VERMELHO')),

  -- Output da IA
  ai_report_technical   text,
  ai_report_onchain     text,
  ai_report_sentiment   text,
  ai_report_verdict     text,
  ai_model              text DEFAULT 'gemini-2.0-flash',

  -- Resultado (performance tracking)
  outcome               text CHECK (outcome IN ('TP_HIT','SL_HIT','MANUAL','OPEN','N/A')),
  outcome_price         numeric,
  outcome_note          text,
  outcome_source        text CHECK (outcome_source IN ('AUTO','MANUAL')) DEFAULT 'AUTO',

  -- Sistema
  telegram_sent         boolean DEFAULT false,
  error_log             text
);

-- Configurações do utilizador
CREATE TABLE settings (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  intraday_threshold    numeric DEFAULT 5.0,
  symbol                text DEFAULT 'BTCUSDT',
  cron_time_utc         text DEFAULT '01:00',
  updated_at            timestamptz DEFAULT now()
);
```

---

## 13. Restrições e Limitações

| Item | Limite | Mitigação |
|------|--------|-----------|
| Gemini 2.0 Flash | 1500 req/dia (free) | 1 req/dia + fallback manual |
| NewsAPI | 100 req/dia (free) | 1 req/dia às 01:00 |
| Supabase | 500MB / 2GB bandwidth | Armazenar só texto, sem binários |
| Render (free) | Sleep após inactividade | Configurar cron para manter ativo |
| Binance API | Sem limite para dados públicos | Sem restrições |

---

## 14. Fora do Escopo (v1)

- Suporte a outros ativos além de BTC
- Multi-utilizador / autenticação
- Backtesting automatizado
- Trading automatizado (sem execução de ordens)
- Mobile app nativo
- Light mode
- Dados on-chain via CryptoQuant/Glassnode (v2)

---

## 15. Roadmap de Desenvolvimento

| Fase | Entregável | Status |
|------|-----------|--------|
| 1 | Fundação: Schema Supabase + estrutura de pastas + variáveis de ambiente | Pendente |
| 2 | Engines de dados: Technical + Sentiment + On-Chain + Macro | Pendente |
| 3 | Cérebro: signal_engine.py + risk_manager.py | Pendente |
| 4 | IA: ai_analyst.py + prompt versionado + Gemini 2.0 Flash | Pendente |
| 5 | Orquestração: main.py + watcher.py + telegram_bot.py | Pendente |
| 6 | API: FastAPI endpoints para o frontend | Pendente |
| 7 | Frontend: Next.js Dashboard + Histórico + Configurações | Pendente |