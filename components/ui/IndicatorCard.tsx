import React from 'react';

interface IndicatorCardProps {
  label: string;
  value: string | number;
  interpretation: string;
  progress?: number; // 0 to 100
  progressColor?: string;
}

export function IndicatorCard({ label, value, interpretation, progress, progressColor = 'var(--signal-green)' }: IndicatorCardProps) {
  return (
    <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-full border border-white/5 hover:border-white/10 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <span className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
          {label}
        </span>
        <span className="font-mono text-xl font-bold text-white">
          {value}
        </span>
      </div>
      
      <div className="mt-auto">
        {progress !== undefined && (
          <div className="w-full h-1.5 bg-white/10 rounded-full mb-3 overflow-hidden">
            <div 
              className="h-full rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${Math.min(Math.max(progress, 0), 100)}%`, backgroundColor: progressColor }}
            />
          </div>
        )}
        <p className="text-sm text-[var(--text-secondary)] leading-snug">
          {interpretation}
        </p>
      </div>
    </div>
  );
}
