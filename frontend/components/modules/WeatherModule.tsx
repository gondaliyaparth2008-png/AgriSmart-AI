// components/modules/WeatherModule.tsx
'use client';

import React, { useState } from 'react';
import {
  CloudRain,
  Sun,
  Cloud,
  CloudLightning,
  Wind,
  Droplets,
  Thermometer,
  ShieldAlert,
  Search,
  MapPin,
  Calendar,
  Sparkles,
  Info,
} from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { useToast } from '@/context/ToastContext';
import { api } from '@/lib/api';
import { WeatherRiskRequest, WeatherRiskResponse } from '@/types/api';

export function WeatherModule() {
  const { t } = useLanguage();
  const { showToast } = useToast();

  const [location, setLocation] = useState('Ahmedabad');
  const [cropName, setCropName] = useState('Tomato');
  const [daysAhead, setDaysAhead] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WeatherRiskResponse | null>(null);

  const fetchWeather = async (loc = location) => {
    if (!loc.trim()) {
      showToast('Please enter a location name or coordinates', 'warning');
      return;
    }

    setLoading(true);
    try {
      const response = await api.getWeatherRisk({
        location: loc.trim(),
        crop_name: cropName.trim() || undefined,
        days_ahead: daysAhead,
      });
      setResult(response);
      showToast(`Weather forecast loaded for ${loc}!`, 'success');
    } catch (err: any) {
      showToast(err?.message || 'Failed to fetch weather forecast', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Weather Condition Icon Mapper
  const getWeatherIcon = (condition: string = '') => {
    const c = condition.toLowerCase();
    if (c.includes('rain') || c.includes('drizzle')) {
      return <CloudRain className="w-8 h-8 text-sky-400" />;
    }
    if (c.includes('thunder') || c.includes('storm')) {
      return <CloudLightning className="w-8 h-8 text-amber-400" />;
    }
    if (c.includes('cloud')) {
      return <Cloud className="w-8 h-8 text-slate-400" />;
    }
    return <Sun className="w-8 h-8 text-amber-400" />;
  };

  const getRiskBadge = (level: string) => {
    switch (level.toLowerCase()) {
      case 'severe':
        return 'bg-red-950/90 text-red-300 border-red-700';
      case 'high':
        return 'bg-orange-950/90 text-orange-300 border-orange-700';
      case 'moderate':
        return 'bg-amber-950/90 text-amber-300 border-amber-700';
      default:
        return 'bg-emerald-950/90 text-emerald-300 border-emerald-700';
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-emerald-900/40 rounded-3xl p-6 backdrop-blur-xl shadow-xl flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-amber-950 border border-amber-600/50 flex items-center justify-center text-amber-400 shadow-md">
          <CloudRain className="w-7 h-7" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>{t.weatherTitle}</span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-950 border border-amber-700 text-amber-300">
              Meteo Risk
            </span>
          </h2>
          <p className="text-sm text-slate-400">{t.weatherSubtitle}</p>
        </div>
      </div>

      {/* Search and Filter Card */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
          {/* Location Input */}
          <div className="sm:col-span-6 relative">
            <MapPin className="w-5 h-5 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder={t.locationPlaceholder}
              className="w-full pl-11 pr-4 py-3 rounded-2xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-emerald-500 outline-none"
            />
          </div>

          {/* Days Ahead Selector */}
          <div className="sm:col-span-3">
            <select
              value={daysAhead}
              onChange={(e) => setDaysAhead(parseInt(e.target.value))}
              className="w-full px-4 py-3 rounded-2xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-emerald-500 outline-none"
            >
              <option value={1}>1 Day Forecast</option>
              <option value={2}>2 Days Forecast</option>
              <option value={3}>3 Days Forecast</option>
              <option value={5}>5 Days Forecast</option>
            </select>
          </div>

          {/* Search Button */}
          <div className="sm:col-span-3">
            <button
              onClick={() => fetchWeather()}
              disabled={loading}
              className="w-full py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-extrabold text-sm shadow-md transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
                  <span>{t.fetchingWeather}</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>{t.getForecastBtn}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Location Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5" /> Presets:
          </span>
          {t.quickLocations.map((loc) => (
            <button
              key={loc}
              onClick={() => {
                setLocation(loc);
                fetchWeather(loc);
              }}
              className="px-3 py-1 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 transition"
            >
              {loc}
            </button>
          ))}
        </div>
      </div>

      {/* Results View */}
      {result ? (
        <div className="space-y-6 animate-fade-in">
          {/* Aggregate Risk Banner */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                {t.overallRiskTitle}
              </span>
              <div className="flex items-center gap-3">
                <span
                  className={`px-4 py-1.5 rounded-full text-sm font-extrabold uppercase tracking-wide border ${getRiskBadge(
                    result.overall_risk_level
                  )}`}
                >
                  {result.overall_risk_level} Risk
                </span>
                <span className="text-xs text-slate-400">
                  Risk Index: <strong className="text-white">{result.risk_index} / 100</strong>
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950/70 px-3 py-1.5 rounded-xl border border-slate-800">
              <Info className="w-4 h-4 text-emerald-400" />
              <span>
                Data source: <strong className="text-slate-300">{result.data_source}</strong>
              </span>
            </div>
          </div>

          {/* Forecast Cards Grid */}
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-emerald-400" /> {t.dailyForecastTitle}
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {result.daily_forecast.map((day, idx) => (
                <div
                  key={idx}
                  className="bg-slate-900/80 border border-slate-800 hover:border-emerald-800/60 transition p-5 rounded-3xl space-y-4 shadow-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-slate-400">{day.date}</span>
                      <h4 className="text-base font-extrabold text-white mt-0.5">{day.condition}</h4>
                    </div>
                    {getWeatherIcon(day.condition)}
                  </div>

                  {/* Temperatures */}
                  <div className="flex items-center gap-2 text-2xl font-extrabold text-white">
                    <Thermometer className="w-5 h-5 text-amber-400" />
                    <span>
                      {day.temp_max_c ?? day.temperature_c ?? '--'}°C
                    </span>
                    {day.temp_min_c !== undefined && (
                      <span className="text-sm text-slate-500 font-semibold">
                        / {day.temp_min_c}°C
                      </span>
                    )}
                  </div>

                  {/* Weather Attributes */}
                  <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-xs">
                    <div>
                      <span className="text-slate-500 block text-[10px]">{t.rainfallLabel}</span>
                      <span className="font-bold text-sky-400">{day.rain_mm} mm</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">{t.humidityLabel}</span>
                      <span className="font-bold text-blue-300">{day.humidity_pct}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">{t.windLabel}</span>
                      <span className="font-bold text-slate-300">{day.wind_kph} km/h</span>
                    </div>
                  </div>

                  {/* Day Risk Score */}
                  {day.day_risk_score !== undefined && (
                    <div className="flex items-center justify-between text-[11px] pt-2 border-t border-slate-800/80">
                      <span className="text-slate-400 font-semibold">Agronomic Threat:</span>
                      <span
                        className={`font-bold px-2 py-0.5 rounded ${
                          day.day_risk_score > 30
                            ? 'bg-red-950 text-red-300 border border-red-800'
                            : day.day_risk_score > 15
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}
                      >
                        {day.day_risk_score} pts
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
              <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" /> {t.weatherRecommendations}
              </h4>
              <ul className="space-y-2">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-xs text-slate-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0"></span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center text-center text-slate-500">
          <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-3">
            <CloudRain className="w-7 h-7" />
          </div>
          <h4 className="text-base font-bold text-slate-400">{t.weatherTitle}</h4>
          <p className="text-xs text-slate-500 max-w-sm mt-1">
            Enter your district or city above and tap &quot;Check Weather Risk&quot; to inspect upcoming rainfall, humidity, and agronomic risks.
          </p>
        </div>
      )}
    </div>
  );
}
