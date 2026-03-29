'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, History, Settings } from 'lucide-react';

const navLinks = [
  { href: '/',         label: 'Dashboard', icon: Activity },
  { href: '/history',  label: 'Histórico', icon: History },
  { href: '/settings', label: 'Settings',  icon: Settings },
];

/**
 * Navbar principal — glass panel com links de navegação e ícones Lucide.
 */
export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-white/10 px-4 sm:px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 text-white hover:text-[var(--signal-green)] transition-colors"
        >
          <Activity className="w-6 h-6 text-[var(--signal-green)]" />
          <span className="font-display font-bold text-lg sm:text-xl tracking-tight">
            CryptoTrade AI
          </span>
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center gap-4 sm:gap-6 text-sm font-medium">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            const Icon = link.icon;

            return (
              <Link
                key={link.href}
                href={link.href}
                className={`
                  flex items-center gap-2 transition-colors
                  ${isActive
                    ? 'text-white'
                    : 'text-[var(--text-secondary)] hover:text-white'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{link.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
