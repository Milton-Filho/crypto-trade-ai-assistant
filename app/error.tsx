'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <h2 className="text-2xl font-bold mb-4">Algo correu mal!</h2>
      <button
        onClick={() => reset()}
        className="px-4 py-2 bg-[var(--signal-yellow)] text-black rounded-md"
      >
        Tentar novamente
      </button>
    </div>
  );
}
