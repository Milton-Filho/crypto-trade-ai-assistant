# Crypto Trade AI Assistant

> Sistema pessoal de análise diária de Bitcoin para swing trade, movido a inteligência artificial (Gemini 2.0 Flash) e dados reais do mercado.


---

## Identidade do Projecto
O **Crypto Trade AI Assistant** é um sistema pessoal desenhado para remover o "ruído" do mercado e fornecer uma análise baseada em confluência técnica, on-chain e de sentimento. 

- **Filosofia:** Cloud native, custo zero (free tiers), sem dados fictícios.
- **Uso:** Estritamente pessoal (single user).

---

## Como Funciona?

O sistema opera através de dois processos principais (Jobs):

1. **Daily Job (01:00 UTC):**
   - Coleta dados técnicos (Binance), On-chain (Blockchain.com & Mempool) e Sentimento (Fear&Greed & NewsAPI).
   - Calcula um **Score de Confluência (0-9)**.
   - A IA (Gemini 2.0 Flash) gera um relatório detalhado com veredito.
   - Se o sinal for **VERDE** (Compra) ou **VERMELHO** (Venda), envia um alerta imediato via Telegram com stop-loss e take-profit calculados.

2. **Watcher Job (Intraday):**
   - Monitoriza o preço a cada 2 horas.
   - Atualiza o status da operação automaticamente (TP Hit / SL Hit).
   - Envia notificações de movimentos bruscos (>5%).

---

## Tech Stack

- **Backend:** Python 3.11 + FastAPI (Hospedado no **Render**)
- **Frontend:** Next.js 14 App Router + Tailwind CSS (Hospedado na **Vercel**)
- **Base de Dados:** PostgreSQL via **Supabase**
- **IA:** Gemini 2.0 Flash (Google AI Studio)
- **Notificações:** Telegram Bot API

---

## Como Executar Localmente

### Pré-requisitos
- Node.js (Frontend)
- Python 3.11 (Backend)
- Conta no Supabase (Base de dados)

### 1. Configuração do Ambiente
Copie o arquivo `.env.example` para `.env.local` na raiz e preencha as suas chaves:
- `GEMINI_API_KEY`
- `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`
- `NEWS_API_KEY`

### 2. Frontend
```bash
npm install
npm run dev
```
Acesse: `http://localhost:3000`

### 3. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python -m api.main        # Rodar API
python -m jobs.daily_job  # Rodar job manual de teste
```

---

## 📊 Arquitetura de Sinal

O sistema utiliza pesos específicos para gerar confiança:
- **RSI (Surbevendido):** +2 pontos
- **Bandas de Bollinger (Toque):** +2 pontos
- **MACD Cross:** +1 ponto
- **SMA 20 > 50:** +1 ponto
- **Fear & Greed (<25):** +2 pontos
- **Network Health:** +1 ponto

---

## 📂 Estrutura do Projeto

- `/backend`: Lógica de motores, IA, jobs e API.
- `/app`: Frontend Next.js (Dashboard, Histórico, Configurações).
- `/components`: Componentes UI reutilizáveis (SignalBadge, ScoreBar, etc).
- `/supabase`: Scripts de schema da base de dados.

---

## 📜 Licença
Projeto para uso pessoal sob licença MIT. 

---
*Construído por Milton Filho*
