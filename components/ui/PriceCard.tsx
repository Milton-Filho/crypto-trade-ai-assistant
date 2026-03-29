import React from 'react';

interface PriceCardProps {
  entry: number | null;
  stopLoss: number | null;
  takeProfit: number | null;
  rrRatio: number | null;
}

export function PriceCard({ entry, stopLoss, takeProfit, rrRatio }: PriceCardProps) {
  const e = entry ?? 0;
  const sl = stopLoss ?? 0;
  const tp = takeProfit ?? 0;
  const rr = rrRatio ?? 0;

  const slPct = e ? ((sl - e) / e) * 100 : 0;
  const tpPct = e ? ((tp - e) / e) * 100 : 0;

  const formatPrice = (val: number) => `$${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatPct = (val: number) => `${val > 0 ? '+' : ''}${val.toFixed(2)}%`;

  return (
    <div className="glass-panel p-6 rounded-2xl">
      <h3 className="font-display text-lg font-semibold text-white mb-6 flex items-center gap-2">
        <span className="w-1.5 h-6 bg-[var(--text-secondary)] rounded-full block"></span>
        Níveis de Execução
      </h3>
      
      <div className="grid grid-cols-2 gap-6">
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Entrada</span>
          <span className="font-mono text-xl text-white font-semibold">{formatPrice(e)}</span>
        </div>
        
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">R/R Ratio</span>
          <span className="font-mono text-xl text-white font-semibold">1:{rr.toFixed(1)}</span>
        </div>

        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Stop-Loss</span>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-xl text-white font-semibold">{formatPrice(sl)}</span>
            <span className={`font-mono text-xs font-medium ${slPct < 0 ? 'text-[var(--signal-red)]' : 'text-[var(--signal-green)]'}`}>
              {formatPct(slPct)}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Take-Profit</span>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-xl text-white font-semibold">{formatPrice(tp)}</span>
            <span className={`font-mono text-xs font-medium ${tpPct > 0 ? 'text-[var(--signal-green)]' : 'text-[var(--signal-red)]'}`}>
              {formatPct(tpPct)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
