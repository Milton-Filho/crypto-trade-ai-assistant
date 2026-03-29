'use client';

import React from 'react';

interface ScoreBarProps {
  score: number;       // 0–9
  maxScore?: number;   // Default: 9
  signal: "VERDE" | "AMARELO" | "VERMELHO";
}

/**
 * Barra visual de score de confluência 0–9.
 * Cada ponto é representado por um segmento com cor contextual.
 */
export function ScoreBar({ score, maxScore = 9, signal }: ScoreBarProps) {
  const segments = Array.from({ length: maxScore }, (_, i) => i + 1);

  const getSegmentColor = (index: number): string => {
    if (index > score) return 'bg-white/5';

    switch (signal) {
      case "VERDE":
        return 'bg-[var(--signal-green)]';
      case "VERMELHO":
        return 'bg-[var(--signal-red)]';
      case "AMARELO":
        return 'bg-[var(--signal-yellow)]';
      default:
        return 'bg-white/20';
    }
  };

  const getGlowColor = (): string => {
    switch (signal) {
      case "VERDE":
        return 'shadow-[0_0_12px_var(--signal-green)]';
      case "VERMELHO":
        return 'shadow-[0_0_12px_var(--signal-red)]';
      case "AMARELO":
        return 'shadow-[0_0_12px_var(--signal-yellow)]';
      default:
        return '';
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
          Confluência
        </span>
        <span className={`font-mono text-sm font-bold ${getGlowColor()}`}>
          {score}/{maxScore}
        </span>
      </div>
      <div className="flex gap-1">
        {segments.map((seg) => (
          <div
            key={seg}
            className={`
              h-2 flex-1 rounded-full transition-all duration-500 ease-out
              ${getSegmentColor(seg)}
              ${seg <= score ? 'opacity-100' : 'opacity-40'}
            `}
          />
        ))}
      </div>
    </div>
  );
}
