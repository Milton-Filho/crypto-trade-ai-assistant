'use client';

import React, { useEffect, useState } from 'react';
import { getTodayAnalysis } from '@/lib/api';
import { DailyAnalysis } from '@/lib/types';
import { SignalBadge } from '@/components/ui/SignalBadge';
import { PriceCard } from '@/components/ui/PriceCard';
import { IndicatorCard } from '@/components/ui/IndicatorCard';
import { ReportBlock } from '@/components/ui/ReportBlock';
import { Activity, BarChart2, Link as LinkIcon, MessageSquare, AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const [analysis, setAnalysis] = useState<DailyAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [livePrice, setLivePrice] = useState<number | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getTodayAnalysis();
        if (data) {
          setAnalysis(data);
        } else {
          setError('Nenhuma análise encontrada para hoje.');
        }
      } catch (err) {
        setError('Falha ao carregar a análise de hoje.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    if (!analysis) return;
    
    const ws = new WebSocket(`wss://stream.binance.com:9443/ws/${analysis.symbol.toLowerCase()}@ticker`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.c) {
        setLivePrice(parseFloat(data.c));
      }
    };

    return () => {
      ws.close();
    };
  }, [analysis]);

  if (loading) {
    return (
      <div className="animate-pulse flex flex-col gap-8">
        <div className="h-16 bg-white/5 rounded-2xl w-1/3 mb-8"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="h-64 bg-white/5 rounded-2xl"></div>
          <div className="h-64 bg-white/5 rounded-2xl"></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-white/5 rounded-2xl"></div>
          ))}
        </div>
        <div className="flex flex-col gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-16 bg-white/5 rounded-2xl"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <AlertTriangle className="w-16 h-16 text-[var(--signal-yellow)] mb-6 opacity-80" />
        <h2 className="font-display text-2xl font-bold text-white mb-2">Análise Indisponível</h2>
        <p className="text-[var(--text-secondary)] max-w-md">
          {error || 'A análise de hoje ainda não foi gerada. O job diário corre às 01:00 (Lisboa).'}
        </p>
      </div>
    );
  }

  const formatPrice = (val: number) => `$${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="flex flex-col gap-10 pb-12">
      {/* Header with Live Price */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <h1 className="font-display text-4xl font-bold text-white tracking-tight mb-2">
            Dashboard
          </h1>
          <p className="text-[var(--text-secondary)] font-medium">
            Análise Diária • {new Date(analysis.date).toLocaleDateString('pt-PT', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider mb-1">
            {analysis.symbol} Live
          </p>
          <div className="font-mono text-4xl font-bold text-white tracking-tight">
            {livePrice ? formatPrice(livePrice) : 'A carregar...'}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-5 flex flex-col justify-center">
          <SignalBadge signal={analysis.signal} score={analysis.confluence_score} size="lg" />
        </div>
        <div className="lg:col-span-7">
          <PriceCard 
            entry={analysis.price_entry} 
            stopLoss={analysis.stop_loss} 
            takeProfit={analysis.take_profit} 
            rrRatio={analysis.rr_ratio} 
          />
        </div>
      </section>

      {/* Indicators Grid */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <IndicatorCard 
          label="RSI (14)" 
          value={analysis.rsi_14.toFixed(1)} 
          interpretation={analysis.rsi_14 > 70 ? 'Zona de Sobrecoumpra' : analysis.rsi_14 < 30 ? 'Zona de Sobrevenda' : 'Neutro'}
          progress={analysis.rsi_14}
          progressColor={analysis.rsi_14 > 70 ? 'var(--signal-red)' : analysis.rsi_14 < 30 ? 'var(--signal-green)' : 'var(--signal-yellow)'}
        />
        <IndicatorCard 
          label="Fear & Greed" 
          value={analysis.fear_greed_score} 
          interpretation={analysis.fear_greed_label}
          progress={analysis.fear_greed_score}
          progressColor={analysis.fear_greed_score > 75 ? 'var(--signal-red)' : analysis.fear_greed_score < 25 ? 'var(--signal-green)' : 'var(--signal-yellow)'}
        />
        <IndicatorCard 
          label="Confluência" 
          value={`${analysis.confluence_score}/9`} 
          interpretation="Score total de indicadores"
          progress={(analysis.confluence_score / 9) * 100}
          progressColor={analysis.confluence_score >= 6 ? 'var(--signal-green)' : analysis.confluence_score <= 3 ? 'var(--signal-red)' : 'var(--signal-yellow)'}
        />
        <IndicatorCard 
          label="Tx Volume" 
          value={`${(analysis.tx_volume / 1000).toFixed(1)}k BTC`} 
          interpretation="Volume on-chain nas últimas 24h"
        />
      </section>

      {/* AI Report Section */}
      <section className="flex flex-col gap-4">
        <h2 className="font-display text-2xl font-bold text-white mb-4 mt-4">Relatório da IA</h2>
        
        <ReportBlock 
          title="Análise Técnica" 
          icon={BarChart2} 
          content={analysis.ai_report_technical} 
        />
        <ReportBlock 
          title="Dados On-Chain" 
          icon={LinkIcon} 
          content={analysis.ai_report_onchain} 
        />
        <ReportBlock 
          title="Sentimento e Macro" 
          icon={MessageSquare} 
          content={analysis.ai_report_sentiment} 
        />
        <ReportBlock 
          title="Veredito Final" 
          icon={Activity} 
          content={analysis.ai_report_verdict} 
          defaultOpen={true}
        />
      </section>
    </div>
  );
}
