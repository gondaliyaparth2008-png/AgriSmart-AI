// components/modules/AdvisoryModule.tsx
'use client';

import React, { useState } from 'react';
import {
  Droplets,
  Calendar,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Waves,
  Lightbulb,
  ShieldAlert,
  Sprout,
  Activity,
} from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { useToast } from '@/context/ToastContext';
import { api } from '@/lib/api';
import {
  AdvisoryRequest,
  AdvisoryResponse,
  CropStage,
  SoilType,
  IrrigationMethod,
} from '@/types/api';
import { MetricGauge } from '@/components/ui/MetricGauge';

export function AdvisoryModule() {
  const { t } = useLanguage();
  const { showToast } = useToast();

  const [formData, setFormData] = useState<AdvisoryRequest>({
    crop_name: 'Tomato',
    crop_stage: 'flowering',
    soil_type: 'loamy',
    ph: 6.5,
    moisture: 42.0,
    temperature: 28.5,
    rain_prob: 0.25,
    current_irrigation_method: 'drip',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AdvisoryResponse | null>(null);

  const cropOptions = [
    'Tomato',
    'Wheat',
    'Paddy (Rice)',
    'Cotton',
    'Potato',
    'Maize (Corn)',
    'Sugarcane',
    'Groundnut',
    'Soybean',
    'Onion',
  ];

  const stageOptions: { value: CropStage; label: string }[] = [
    { value: 'germination', label: 'Germination (અંકુરણ / अंकुरण)' },
    { value: 'seedling', label: 'Seedling (રોપા અવસ્થા / पौध)' },
    { value: 'vegetative', label: 'Vegetative (વાનસ્પતિક / वानस्पतिक)' },
    { value: 'flowering', label: 'Flowering (ફૂલ અવસ્થા / फूल)' },
    { value: 'fruiting', label: 'Fruiting / Grain Fill (ફળ-દાણા / फल-दाना)' },
    { value: 'harvest', label: 'Maturity / Harvest (પાકવાની અવસ્થા / कटाई)' },
  ];

  const soilOptions: { value: SoilType; label: string }[] = [
    { value: 'loamy', label: 'Loamy (ગોરાડુ / दोमट - Best Balance)' },
    { value: 'clay', label: 'Clay (કાળી-ચીકણી / चिकनी काली)' },
    { value: 'sandy', label: 'Sandy (રેતાળ / बलुई)' },
    { value: 'silty', label: 'Silty (કાંપવાળી / गादयुक्त)' },
    { value: 'peaty', label: 'Peaty (સેન્દ્રિય / जैविक)' },
    { value: 'chalky', label: 'Chalky (ચૂનાયુક્ત / चूनेदार)' },
    { value: 'saline', label: 'Saline (ક્ષારવાળી / क्षारीय)' },
  ];

  const irrigationMethods: { value: IrrigationMethod; label: string }[] = [
    { value: 'drip', label: 'Drip Irrigation (ટપક પદ્ધતિ)' },
    { value: 'sprinkler', label: 'Sprinkler (ફુવારા પદ્ધતિ)' },
    { value: 'furrow', label: 'Furrow / Ridge (ક્યારી / धोरा)' },
    { value: 'flood', label: 'Flood / Basin (પૂરક પદ્ધતિ)' },
    { value: 'none', label: 'Rainfed / None (કેવળ વરસાદ આધારિત)' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.getAdvisory(formData);
      setResult(response);
      showToast('Irrigation advisory generated successfully!', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Failed to generate advisory', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-emerald-900/40 rounded-3xl p-6 backdrop-blur-xl shadow-xl flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-sky-950 border border-sky-600/50 flex items-center justify-center text-sky-400 shadow-md">
          <Droplets className="w-7 h-7" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>{t.advisoryTitle}</span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-sky-950 border border-sky-700 text-sky-300">
              Sensor AI
            </span>
          </h2>
          <p className="text-sm text-slate-400">{t.advisorySubtitle}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form Column */}
        <div className="lg:col-span-6 bg-slate-900/70 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
            <Activity className="w-4 h-4" /> Field &amp; Soil Conditions
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Crop Name */}
            <div>
              <label className="text-xs font-semibold text-slate-300 mb-1.5 block">
                {t.cropNameLabel}
              </label>
              <select
                value={formData.crop_name}
                onChange={(e) => setFormData({ ...formData, crop_name: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-emerald-500 outline-none"
              >
                {cropOptions.map((crop) => (
                  <option key={crop} value={crop}>
                    {crop}
                  </option>
                ))}
              </select>
            </div>

            {/* Growth Stage */}
            <div>
              <label className="text-xs font-semibold text-slate-300 mb-1.5 block">
                {t.growthStageLabel}
              </label>
              <select
                value={formData.crop_stage}
                onChange={(e) =>
                  setFormData({ ...formData, crop_stage: e.target.value as CropStage })
                }
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-emerald-500 outline-none"
              >
                {stageOptions.map((stg) => (
                  <option key={stg.value} value={stg.value}>
                    {stg.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Soil Type */}
            <div>
              <label className="text-xs font-semibold text-slate-300 mb-1.5 block">
                {t.soilTypeLabel}
              </label>
              <select
                value={formData.soil_type}
                onChange={(e) =>
                  setFormData({ ...formData, soil_type: e.target.value as SoilType })
                }
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-emerald-500 outline-none"
              >
                {soilOptions.map((soil) => (
                  <option key={soil.value} value={soil.value}>
                    {soil.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Interactive Sliders */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              {/* pH Slider */}
              <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>{t.phLabel}</span>
                  <span className="text-emerald-400 font-bold">{formData.ph.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="4.0"
                  max="9.5"
                  step="0.1"
                  value={formData.ph}
                  onChange={(e) => setFormData({ ...formData, ph: parseFloat(e.target.value) })}
                  className="w-full accent-emerald-500 cursor-pointer"
                />
              </div>

              {/* Moisture Slider */}
              <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>{t.moistureLabel}</span>
                  <span className="text-sky-400 font-bold">{Math.round(formData.moisture)}%</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="95"
                  step="1"
                  value={formData.moisture}
                  onChange={(e) =>
                    setFormData({ ...formData, moisture: parseFloat(e.target.value) })
                  }
                  className="w-full accent-sky-500 cursor-pointer"
                />
              </div>

              {/* Temperature Slider */}
              <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>{t.tempLabel}</span>
                  <span className="text-amber-400 font-bold">
                    {formData.temperature.toFixed(1)}°C
                  </span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="48"
                  step="0.5"
                  value={formData.temperature}
                  onChange={(e) =>
                    setFormData({ ...formData, temperature: parseFloat(e.target.value) })
                  }
                  className="w-full accent-amber-500 cursor-pointer"
                />
              </div>

              {/* Rain Probability Slider */}
              <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span>{t.rainProbLabel}</span>
                  <span className="text-blue-400 font-bold">
                    {Math.round(formData.rain_prob * 100)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={formData.rain_prob}
                  onChange={(e) =>
                    setFormData({ ...formData, rain_prob: parseFloat(e.target.value) })
                  }
                  className="w-full accent-blue-500 cursor-pointer"
                />
              </div>
            </div>

            {/* Current Method */}
            <div>
              <label className="text-xs font-semibold text-slate-300 mb-1.5 block">
                {t.currentMethodLabel}
              </label>
              <select
                value={formData.current_irrigation_method}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    current_irrigation_method: e.target.value as IrrigationMethod,
                  })
                }
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-white text-sm focus:border-emerald-500 outline-none"
              >
                {irrigationMethods.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 via-green-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-extrabold text-sm shadow-lg shadow-emerald-950 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
                  <span>{t.calculatingAdvisory}</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>{t.getAdvisoryBtn}</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Results Column */}
        <div className="lg:col-span-6 flex flex-col">
          {result ? (
            <div className="bg-slate-900/90 border border-emerald-900/40 rounded-3xl p-6 shadow-2xl space-y-6 animate-fade-in">
              {/* Should Irrigate Banner */}
              <div
                className={`p-5 rounded-2xl border flex items-center gap-4 ${
                  result.should_irrigate_today
                    ? 'bg-emerald-950/80 border-emerald-600 text-emerald-100 shadow-md shadow-emerald-950'
                    : 'bg-sky-950/80 border-sky-600 text-sky-100'
                }`}
              >
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    result.should_irrigate_today
                      ? 'bg-emerald-600 text-white'
                      : 'bg-sky-600 text-white'
                  }`}
                >
                  <Droplets className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    {t.shouldIrrigateToday}
                  </span>
                  <h4 className="text-lg font-extrabold">
                    {result.should_irrigate_today ? t.irrigateYes : t.irrigateNo}
                  </h4>
                </div>
              </div>

              {/* Sustainability Score & Recommended Method */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center bg-slate-950/80 p-4 rounded-2xl border border-slate-800">
                <MetricGauge
                  value={result.sustainability_score}
                  title={t.sustainabilityScore}
                  rating={result.sustainability_rating}
                  size="sm"
                />

                <div className="flex flex-col gap-2 p-2">
                  <span className="text-xs font-semibold text-slate-400">
                    {t.recommendedMethod}
                  </span>
                  <span className="px-3.5 py-1.5 rounded-xl bg-emerald-950 border border-emerald-700 text-emerald-300 font-extrabold text-sm uppercase tracking-wide w-fit">
                    {result.recommended_method.toUpperCase()}
                  </span>
                  <span className="text-xs text-slate-400">
                    Calculated for {result.crop_name} ({result.crop_stage} stage)
                  </span>
                </div>
              </div>

              {/* 3-Day Irrigation Timetable */}
              {result.irrigation_schedule && result.irrigation_schedule.length > 0 && (
                <div className="space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Calendar className="w-4 h-4 text-emerald-400" /> {t.timetableTitle}
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    {result.irrigation_schedule.map((item) => (
                      <div
                        key={item.day_offset}
                        className="bg-slate-950/90 border border-slate-800 p-3.5 rounded-2xl space-y-1.5"
                      >
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-extrabold text-emerald-400">
                            {item.day_offset === 0
                              ? 'Today'
                              : item.day_offset === 1
                              ? 'Tomorrow'
                              : `Day +${item.day_offset}`}
                          </span>
                          <Clock className="w-3.5 h-3.5 text-slate-500" />
                        </div>
                        <div className="text-lg font-extrabold text-white">
                          {item.duration_minutes} mins
                        </div>
                        <div className="text-xs text-slate-400">
                          {item.water_volume_liters_per_sqm} L/m²
                        </div>
                        {item.notes && (
                          <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-800/80 italic">
                            {item.notes}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actionable Tips & Risk Flags */}
              <div className="space-y-3">
                {result.risk_flags && result.risk_flags.length > 0 && (
                  <div className="p-3.5 bg-red-950/40 border border-red-800/60 rounded-2xl text-xs space-y-1.5">
                    <div className="font-bold text-red-300 flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-red-400" /> {t.riskFlagsTitle}:
                    </div>
                    <ul className="list-disc pl-5 text-red-200/90 space-y-0.5">
                      {result.risk_flags.map((flag, idx) => (
                        <li key={idx}>{flag}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.actionable_tips && result.actionable_tips.length > 0 && (
                  <div className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-2xl text-xs space-y-1.5">
                    <div className="font-bold text-amber-300 flex items-center gap-1.5">
                      <Lightbulb className="w-4 h-4 text-amber-400" /> {t.actionableTipsTitle}:
                    </div>
                    <ul className="space-y-1 pl-1">
                      {result.actionable_tips.map((tip, idx) => (
                        <li key={idx} className="text-slate-300 flex items-start gap-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[380px] bg-slate-900/40 border border-dashed border-slate-800 rounded-3xl p-8 flex flex-col items-center justify-center text-center text-slate-500">
              <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-3">
                <Droplets className="w-7 h-7" />
              </div>
              <h4 className="text-base font-bold text-slate-400">{t.advisoryTitle}</h4>
              <p className="text-xs text-slate-500 max-w-xs mt-1">
                Configure your crop type, soil texture, pH, moisture, and rain forecast on the left to receive a custom irrigation schedule.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
