// app/page.tsx
'use client';

import React, { useState } from 'react';
import { Navbar, ActiveTab } from '@/components/Navbar';
import { AssistantModule } from '@/components/modules/AssistantModule';
import { DiseaseModule } from '@/components/modules/DiseaseModule';
import { AdvisoryModule } from '@/components/modules/AdvisoryModule';
import { WeatherModule } from '@/components/modules/WeatherModule';
import { useLanguage } from '@/context/LanguageContext';
import { Sprout, ShieldCheck, Cpu, Waves } from 'lucide-react';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('assistant');
  const [diseaseContextToPass, setDiseaseContextToPass] = useState<string | null>(null);
  const { t } = useLanguage();

  const handleAskAboutDisease = (context: string) => {
    setDiseaseContextToPass(context);
    setActiveTab('assistant');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-slate-950">
      {/* Sticky Navigation Bar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 flex flex-col gap-6">
        {/* Module Content Rendering */}
        <div className="w-full flex-1">
          {activeTab === 'assistant' && <AssistantModule />}
          {activeTab === 'disease' && (
            <DiseaseModule onAskAboutDisease={handleAskAboutDisease} />
          )}
          {activeTab === 'advisory' && <AdvisoryModule />}
          {activeTab === 'weather' && <WeatherModule />}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-900 bg-slate-950/80 py-6 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Sprout className="w-4 h-4 text-emerald-400" />
            <span className="font-semibold text-slate-400">{t.appName}</span>
            <span>— Precision Agriculture for Bharat</span>
          </div>

          <div className="flex items-center gap-6 text-[11px]">
            <span className="flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-emerald-400" /> FastAPI Engine
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> PlantVillage &amp; ICAR Certified
            </span>
            <span className="flex items-center gap-1">
              <Waves className="w-3.5 h-3.5 text-sky-400" /> Web Speech Trilingual
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
