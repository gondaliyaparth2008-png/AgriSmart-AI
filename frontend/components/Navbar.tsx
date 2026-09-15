// components/Navbar.tsx
'use client';

import React, { useState } from 'react';
import { Sprout, MessageSquareQuote, Stethoscope, Droplets, CloudRain, Globe, Menu, X } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { LanguageCode } from '@/types/api';
import { BackendStatusBadge } from './BackendStatusBadge';

export type ActiveTab = 'assistant' | 'disease' | 'advisory' | 'weather';

interface NavbarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
}

export function Navbar({ activeTab, setActiveTab }: NavbarProps) {
  const { language, setLanguage, t } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs: { id: ActiveTab; label: string; icon: React.ReactNode }[] = [
    { id: 'assistant', label: t.tabAssistant, icon: <MessageSquareQuote className="w-5 h-5" /> },
    { id: 'disease', label: t.tabDisease, icon: <Stethoscope className="w-5 h-5" /> },
    { id: 'advisory', label: t.tabAdvisory, icon: <Droplets className="w-5 h-5" /> },
    { id: 'weather', label: t.tabWeather, icon: <CloudRain className="w-5 h-5" /> },
  ];

  const languages: { code: LanguageCode; label: string; flag: string }[] = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'hi', label: 'हिन्दी', flag: '🇮🇳' },
    { code: 'gu', label: 'ગુજરાતી', flag: '🇮🇳' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-emerald-900/40 bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 via-kisan-500 to-emerald-400 p-0.5 shadow-lg shadow-emerald-950/50 flex items-center justify-center">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Sprout className="w-6 h-6 text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-emerald-300 via-green-200 to-amber-200 bg-clip-text text-transparent">
                  {t.appName}
                </span>
                <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-emerald-900/60 text-emerald-300 rounded-full border border-emerald-700/50">
                  Kisan 2.0
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium hidden md:block">{t.appTagline}</p>
            </div>
          </div>

          {/* Desktop Navigation Tabs */}
          <nav className="hidden lg:flex items-center gap-1 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-500 text-white shadow-md shadow-emerald-950/80'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <span className={isActive ? 'text-white' : 'text-emerald-400'}>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Controls: Status & Language */}
          <div className="hidden sm:flex items-center gap-3">
            <BackendStatusBadge />

            {/* Language Switcher */}
            <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1">
              <Globe className="w-4 h-4 text-slate-400 ml-1.5 mr-0.5" />
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                    language === lang.code
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/70'
                  }`}
                >
                  <span>{lang.flag} </span>
                  <span>{lang.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 lg:hidden">
            <BackendStatusBadge />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-800 bg-slate-950/95 px-4 pt-3 pb-6 space-y-4 animate-fade-in">
          {/* Mobile Language Switcher */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/90 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Globe className="w-4 h-4 text-emerald-400" /> Language / ભાષા / भाषा:
            </span>
            <div className="flex gap-1">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    language === lang.code
                      ? 'bg-emerald-600 text-white shadow'
                      : 'text-slate-400 bg-slate-800 hover:bg-slate-700'
                  }`}
                >
                  {lang.flag} {lang.label}
                </button>
              ))}
            </div>
          </div>

          {/* Mobile Tabs */}
          <div className="grid grid-cols-1 gap-2">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`flex items-center gap-3 w-full px-4 py-3.5 rounded-xl font-bold text-base transition-all ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md'
                      : 'bg-slate-900/60 border border-slate-800/80 text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <span className={isActive ? 'text-white' : 'text-emerald-400'}>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
}
