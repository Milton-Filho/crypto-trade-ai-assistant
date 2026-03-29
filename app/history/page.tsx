'use client';

import React, { useEffect, useState } from 'react';
import { getHistory } from '@/lib/api';
import { DailyAnalysis } from '@/lib/types';
import { SignalBadge } from '@/components/ui/SignalBadge';
import { EditModal } from '@/components/ui/EditModal';
import { Edit2, AlertTriangle } from 'lucide-react';

export default function HistoryPage() {
  const [history, setHistory] = useState<DailyAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getHistory(30);
      setHistory(data);
    } catch (err) {
      setError('Falha ao carregar o histórico.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatPrice = (val: number) => `$${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const getOutcomeBadge = (outcome: string) => {
    switch (outcome) {
      case 'TP_HIT':
        return <span className="px-2 py-1 rounded-md bg-[var(--signal-green)]/20 text-[var(--signal-green)] text-xs font-bold tracking-wider">TP HIT</span>;
      case 'SL_HIT':
        return <span className="px-2 py-1 rounded-md bg-[var(--signal-red)]/20 text-[var(--signal-red)] text-xs font-bold tracking-wider">SL HIT</span>;
      case 'OPEN':
        return <span className="px-2 py-1 rounded-md bg-[var(--signal-yellow)]/20 text-[var(--signal-yellow)] text-xs font-bold tracking-wider">OPEN</span>;
      case 'MANUAL':
        return <span className="px-2 py-1 rounded-md bg-white/10 text-white/80 text-xs font-bold tracking-wider">MANUAL</span>;
      default:
        return <span className="px-2 py-1 rounded-md bg-white/5 text-white/50 text-xs font-bold tracking-wider">N/A</span>;
    }
  };

  if (loading && history.length === 0) {
    return (
      <div className="animate-pulse flex flex-col gap-4">
        <div className="h-10 bg-white/5 rounded-lg w-1/4 mb-6"></div>
        {[...Array(10)].map((_, i) => (
          <div key={i} className="h-16 bg-white/5 rounded-xl"></div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <AlertTriangle className="w-16 h-16 text-[var(--signal-red)] mb-6 opacity-80" />
        <h2 className="font-display text-2xl font-bold text-white mb-2">Erro</h2>
        <p className="text-[var(--text-secondary)] max-w-md">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 pb-12">
      <header className="border-b border-white/10 pb-6">
        <h1 className="font-display text-4xl font-bold text-white tracking-tight mb-2">
          Histórico
        </h1>
        <p className="text-[var(--text-secondary)] font-medium">
          Últimos 30 dias de análise e sinais
        </p>
      </header>

      <div className="glass-panel rounded-2xl overflow-hidden overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr className="border-b border-white/10 bg-white/5">
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Data</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Sinal</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider text-right">Entrada</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider text-right">SL</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider text-right">TP</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider text-center">R/R</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider text-center">Resultado</th>
              <th className="px-6 py-4 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider text-center">Acção</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {history.map((row) => (
              <tr key={row.id} className="hover:bg-white/5 transition-colors group">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--text-primary)]">
                  {new Date(row.date).toLocaleDateString('pt-PT', { day: '2-digit', month: 'short' })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <SignalBadge signal={row.signal} score={row.confluence_score} size="sm" />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-white text-right">
                  {row.price_entry ? formatPrice(row.price_entry) : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-[var(--signal-red)] text-right">
                  {row.stop_loss ? formatPrice(row.stop_loss) : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-[var(--signal-green)] text-right">
                  {row.take_profit ? formatPrice(row.take_profit) : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-[var(--text-secondary)] text-center">
                  {row.rr_ratio ? `1:${row.rr_ratio.toFixed(1)}` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  {getOutcomeBadge(row.outcome)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <button 
                    onClick={() => setEditingId(row.id)}
                    className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-white hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                    title="Editar Resultado"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {history.length === 0 && !loading && (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center text-[var(--text-secondary)]">
                  Nenhum histórico encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {editingId && (
        <EditModal 
          id={editingId}
          currentOutcome={history.find(h => h.id === editingId)?.outcome || 'OPEN'}
          currentPrice={history.find(h => h.id === editingId)?.outcome_price || null}
          currentNote={history.find(h => h.id === editingId)?.outcome_note || null}
          onClose={() => setEditingId(null)}
          onSuccess={() => {
            setEditingId(null);
            fetchHistory();
          }}
        />
      )}
    </div>
  );
}
