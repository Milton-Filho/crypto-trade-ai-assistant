'use client';

import React, { useEffect, useState } from 'react';
import { getSettings, updateSettings } from '@/lib/api';
import { Settings as SettingsType } from '@/lib/types';
import { Save, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSettings() {
      try {
        const data = await getSettings();
        if (data) {
          setSettings(data);
        } else {
          setError('Configurações não encontradas.');
        }
      } catch (err) {
        setError('Falha ao carregar as configurações.');
      } finally {
        setLoading(false);
      }
    }
    fetchSettings();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settings) return;
    
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await updateSettings({
        intraday_threshold: settings.intraday_threshold,
        symbol: settings.symbol,
        cron_time_utc: settings.cron_time_utc
      });
      setSuccess('Configurações guardadas com sucesso.');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Falha ao guardar as configurações.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse flex flex-col gap-8 max-w-2xl mx-auto">
        <div className="h-10 bg-white/5 rounded-lg w-1/3 mb-6"></div>
        <div className="h-64 bg-white/5 rounded-2xl"></div>
      </div>
    );
  }

  if (error && !settings) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <AlertTriangle className="w-16 h-16 text-[var(--signal-red)] mb-6 opacity-80" />
        <h2 className="font-display text-2xl font-bold text-white mb-2">Erro</h2>
        <p className="text-[var(--text-secondary)] max-w-md">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 pb-12 max-w-2xl mx-auto w-full">
      <header className="border-b border-white/10 pb-6">
        <h1 className="font-display text-4xl font-bold text-white tracking-tight mb-2">
          Configurações
        </h1>
        <p className="text-[var(--text-secondary)] font-medium">
          Ajuste os parâmetros do sistema e alertas
        </p>
      </header>

      <div className="glass-panel rounded-2xl p-8">
        <form onSubmit={handleSubmit} className="flex flex-col gap-8">
          
          <div className="flex flex-col gap-3">
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-white">Threshold Intraday (%)</label>
              <span className="font-mono text-[var(--signal-green)] font-bold">{settings?.intraday_threshold.toFixed(1)}%</span>
            </div>
            <p className="text-xs text-[var(--text-secondary)] mb-2">
              Variação mínima de preço desde a entrada para disparar um alerta no Telegram.
            </p>
            <input 
              type="range" 
              min="1" 
              max="20" 
              step="0.5"
              value={settings?.intraday_threshold || 5}
              onChange={(e) => setSettings(prev => prev ? {...prev, intraday_threshold: parseFloat(e.target.value)} : null)}
              className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[var(--signal-green)]"
            />
            <div className="flex justify-between text-xs text-[var(--text-secondary)] font-mono mt-1">
              <span>1.0%</span>
              <span>20.0%</span>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <label className="text-sm font-medium text-white">Par de Moeda</label>
            <p className="text-xs text-[var(--text-secondary)] mb-1">
              Símbolo negociado na Binance (ex: BTCUSDT, ETHUSDT).
            </p>
            <input 
              type="text" 
              value={settings?.symbol || ''}
              onChange={(e) => setSettings(prev => prev ? {...prev, symbol: e.target.value.toUpperCase()} : null)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-[var(--signal-green)] transition-colors uppercase"
              placeholder="BTCUSDT"
              pattern="^[A-Z0-9]+USDT$"
              required
            />
          </div>

          <div className="flex flex-col gap-3">
            <label className="text-sm font-medium text-white">Hora do Job Diário (UTC)</label>
            <p className="text-xs text-[var(--text-secondary)] mb-1">
              Apenas informativo. A alteração real requer actualização no Render Cron.
            </p>
            <input 
              type="text" 
              value={settings?.cron_time_utc || '01:00'}
              disabled
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-[var(--text-secondary)] font-mono cursor-not-allowed opacity-70"
            />
          </div>

          <div className="pt-4 border-t border-white/10 flex items-center justify-between">
            <div className="flex-1">
              {error && (
                <div className="flex items-center gap-2 text-[var(--signal-red)] text-sm font-medium">
                  <AlertTriangle className="w-4 h-4" />
                  {error}
                </div>
              )}
              {success && (
                <div className="flex items-center gap-2 text-[var(--signal-green)] text-sm font-medium">
                  <CheckCircle2 className="w-4 h-4" />
                  {success}
                </div>
              )}
            </div>
            
            <button 
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-bold bg-[var(--signal-green)] text-black hover:bg-opacity-90 transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? 'A guardar...' : 'Guardar Configurações'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
