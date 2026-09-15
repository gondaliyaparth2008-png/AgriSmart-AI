// components/BackendStatusBadge.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useLanguage } from '@/context/LanguageContext';

export function BackendStatusBadge() {
  const { t } = useLanguage();
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function ping() {
      try {
        const res = await api.checkHealth();
        if (isMounted) {
          setIsOnline(res.status === 'ok' || res.status === 'healthy' || !!res);
        }
      } catch {
        if (isMounted) {
          setIsOnline(false);
        }
      }
    }

    ping();
    const interval = setInterval(ping, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold tracking-wide border transition-all ${
        isOnline === null
          ? 'bg-slate-800/60 border-slate-700 text-slate-400'
          : isOnline
          ? 'bg-emerald-950/70 border-emerald-600/50 text-emerald-300 shadow-sm shadow-emerald-900/30'
          : 'bg-red-950/70 border-red-600/50 text-red-300'
      }`}
      title={isOnline ? 'Backend API is running on localhost:8000' : 'Backend is unreachable on localhost:8000'}
    >
      <span className="relative flex h-2 w-2">
        {isOnline && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        )}
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            isOnline === null ? 'bg-slate-400' : isOnline ? 'bg-emerald-400' : 'bg-red-400'
          }`}
        ></span>
      </span>
      <span>
        {isOnline === null ? t.checkingConnection : isOnline ? t.backendOnline : t.backendOffline}
      </span>
    </div>
  );
}
