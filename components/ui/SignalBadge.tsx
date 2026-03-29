import React from 'react';

interface SignalBadgeProps {
  signal: 'VERDE' | 'AMARELO' | 'VERMELHO';
  score: number;
  size?: 'sm' | 'lg';
}

export function SignalBadge({ signal, score, size = 'sm' }: SignalBadgeProps) {
  const isLg = size === 'lg';
  
  let colorClass = '';
  let pulseClass = '';
  let text = '';
  
  switch (signal) {
    case 'VERDE':
      colorClass = 'bg-[var(--signal-green)]';
      pulseClass = 'animate-pulse shadow-[0_0_15px_var(--signal-green)]';
      text = 'COMPRA';
      break;
    case 'AMARELO':
      colorClass = 'bg-[var(--signal-yellow)]';
      pulseClass = 'animate-pulse shadow-[0_0_15px_var(--signal-yellow)]';
      text = 'ESPERA';
      break;
    case 'VERMELHO':
      colorClass = 'bg-[var(--signal-red)]';
      pulseClass = 'animate-pulse shadow-[0_0_15px_var(--signal-red)]';
      text = 'VENDA';
      break;
  }

  if (isLg) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-8 glass-panel rounded-2xl">
        <div className="relative flex items-center justify-center">
          <div className={`absolute w-16 h-16 rounded-full ${colorClass} opacity-20 ${pulseClass}`} />
          <div className={`relative w-8 h-8 rounded-full ${colorClass} shadow-lg`} />
        </div>
        <div className="text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight text-white mb-1">
            {text}
          </h2>
          <p className="font-mono text-[var(--text-secondary)] text-sm">
            SCORE: {score}/9
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 glass-panel rounded-full border border-white/5">
      <div className={`w-2.5 h-2.5 rounded-full ${colorClass}`} />
      <span className="font-mono text-xs font-medium text-[var(--text-primary)]">
        {text} — {score}/9
      </span>
    </div>
  );
}
