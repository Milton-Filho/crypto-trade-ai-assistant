'use client';

import React, { useState } from 'react';
import { updateOutcome } from '@/lib/api';
import { X } from 'lucide-react';

interface EditModalProps {
  id: string;
  currentOutcome: string;
  currentPrice: number | null;
  currentNote: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditModal({ id, currentOutcome, currentPrice, currentNote, onClose, onSuccess }: EditModalProps) {
  const [outcome, setOutcome] = useState(currentOutcome === 'N/A' || currentOutcome === 'OPEN' ? 'MANUAL' : currentOutcome);
  const [price, setPrice] = useState(currentPrice ? currentPrice.toString() : '');
  const [note, setNote] = useState(currentNote || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await updateOutcome(id, outcome, parseFloat(price) || 0, note);
      onSuccess();
    } catch (err) {
      setError('Falha ao actualizar resultado.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="glass-panel w-full max-w-md rounded-2xl p-6 relative">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-[var(--text-secondary)] hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
        
        <h2 className="font-display text-xl font-bold text-white mb-6">Editar Resultado</h2>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-[var(--text-secondary)]">Resultado</label>
            <select 
              value={outcome}
              onChange={(e) => setOutcome(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[var(--signal-green)] transition-colors"
            >
              <option value="OPEN">OPEN</option>
              <option value="TP_HIT">TP HIT</option>
              <option value="SL_HIT">SL HIT</option>
              <option value="MANUAL">MANUAL</option>
            </select>
          </div>
          
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-[var(--text-secondary)]">Preço de Saída</label>
            <input 
              type="number" 
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white font-mono focus:outline-none focus:border-[var(--signal-green)] transition-colors"
              placeholder="0.00"
              required
            />
          </div>
          
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-[var(--text-secondary)]">Nota</label>
            <textarea 
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-[var(--signal-green)] transition-colors resize-none h-24"
              placeholder="Motivo do fecho manual..."
            />
          </div>

          {error && (
            <div className="text-[var(--signal-red)] text-sm font-medium mt-2">
              {error}
            </div>
          )}
          
          <div className="flex items-center justify-end gap-3 mt-4">
            <button 
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-white transition-colors"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              disabled={loading}
              className="px-6 py-2 rounded-lg text-sm font-medium bg-[var(--signal-green)] text-black hover:bg-opacity-90 transition-colors disabled:opacity-50"
            >
              {loading ? 'A guardar...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
