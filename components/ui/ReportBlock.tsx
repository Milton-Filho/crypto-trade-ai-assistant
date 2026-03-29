'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, LucideIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface ReportBlockProps {
  title: string;
  icon: LucideIcon;
  content: string;
  defaultOpen?: boolean;
}

export function ReportBlock({ title, icon: Icon, content, defaultOpen = false }: ReportBlockProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border border-white/5 transition-colors hover:border-white/10">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 text-left bg-transparent focus:outline-none"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-white/5 text-[var(--text-secondary)]">
            <Icon className="w-5 h-5" />
          </div>
          <h3 className="font-display font-semibold text-lg text-white tracking-tight">
            {title}
          </h3>
        </div>
        <div className="text-[var(--text-secondary)]">
          {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>
      </button>
      
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
          >
            <div className="px-5 pb-6 pt-2 border-t border-white/5">
              <div className="prose prose-invert max-w-none text-[var(--text-primary)] leading-relaxed text-[15px]">
                {content.split('\n').map((paragraph, idx) => (
                  <p key={idx} className="mb-4 last:mb-0">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
