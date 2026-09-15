// components/ui/MetricGauge.tsx
'use client';

import React from 'react';

interface MetricGaugeProps {
  value: number; // 0 - 100
  title?: string;
  subtitle?: string;
  rating?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function MetricGauge({
  value,
  title,
  subtitle,
  rating,
  size = 'md',
}: MetricGaugeProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)));

  // Color logic
  let strokeColor = 'stroke-emerald-400';
  let badgeColor = 'bg-emerald-950 text-emerald-300 border-emerald-700';

  if (clamped < 40) {
    strokeColor = 'stroke-red-400';
    badgeColor = 'bg-red-950 text-red-300 border-red-700';
  } else if (clamped < 70) {
    strokeColor = 'stroke-amber-400';
    badgeColor = 'bg-amber-950 text-amber-300 border-amber-700';
  }

  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clamped / 100) * circumference;

  const sizeClasses = {
    sm: 'w-24 h-24 text-xl',
    md: 'w-36 h-36 text-3xl',
    lg: 'w-48 h-48 text-4xl',
  };

  return (
    <div className="flex flex-col items-center justify-center text-center p-3">
      <div className={`relative flex items-center justify-center ${sizeClasses[size]}`}>
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            className="stroke-slate-800"
            strokeWidth="9"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            className={`${strokeColor} transition-all duration-1000 ease-out`}
            strokeWidth="9"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="font-extrabold tracking-tight text-white">{clamped}</span>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">/ 100</span>
        </div>
      </div>

      {rating && (
        <span className={`mt-2 px-3 py-0.5 text-xs font-extrabold rounded-full border ${badgeColor}`}>
          {rating}
        </span>
      )}

      {title && <span className="mt-2 text-sm font-bold text-slate-200">{title}</span>}
      {subtitle && <span className="text-xs text-slate-400 max-w-xs">{subtitle}</span>}
    </div>
  );
}
