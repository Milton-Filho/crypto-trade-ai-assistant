import React from 'react';

/**
 * Footer minimalista — apenas informação de copyright.
 */
export function Footer() {
  return (
    <footer className="border-t border-white/5 px-6 py-4 mt-auto">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <p className="text-xs text-[var(--text-secondary)]">
          Crypto Trade AI Assistant — Uso pessoal
        </p>
        <p className="text-xs text-[var(--text-secondary)] font-mono">
          v1.0
        </p>
      </div>
    </footer>
  );
}
