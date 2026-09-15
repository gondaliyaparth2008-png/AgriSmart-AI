// components/modules/DiseaseModule.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Camera,
  Upload,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Stethoscope,
  Sparkles,
  Layers,
  ArrowRight,
  ShieldCheck,
  RotateCcw,
  Maximize2,
} from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { useToast } from '@/context/ToastContext';
import { api } from '@/lib/api';
import { DiseasePredictionResponse } from '@/types/api';

interface DiseaseModuleProps {
  onAskAboutDisease?: (diseaseContext: string) => void;
}

export function DiseaseModule({ onAskAboutDisease }: DiseaseModuleProps) {
  const { t } = useLanguage();
  const { showToast } = useToast();

  const [mode, setMode] = useState<'camera' | 'upload'>('camera');
  const [cameraActive, setCameraActive] = useState(false);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [imageBlob, setImageBlob] = useState<Blob | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<DiseasePredictionResponse | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Stop camera stream on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const startCamera = async (facing: 'environment' | 'user' = facingMode) => {
    stopCamera();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: facing },
          width: { ideal: 1280 },
          height: { ideal: 960 },
        },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraActive(true);
      setCapturedImage(null);
      setImageBlob(null);
    } catch (err: any) {
      console.error('Error opening camera:', err);
      if (err.name === 'NotAllowedError') {
        showToast(t.cameraPermissionDenied, 'error');
      } else if (err.name === 'NotFoundError') {
        showToast(t.noCameraFound, 'error');
      } else {
        showToast(err.message || 'Failed to open camera', 'error');
      }
      setCameraActive(false);
    }
  };

  const switchCamera = () => {
    const nextFacing = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextFacing);
    if (cameraActive) {
      startCamera(nextFacing);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (blob) {
          setImageBlob(blob);
          setSelectedFile(null);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
          setCapturedImage(dataUrl);
          stopCamera();
        }
      },
      'image/jpeg',
      0.92
    );
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    setImageBlob(null);
    setResult(null);
    startCamera();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      showToast('Please select a valid image file (JPEG, PNG, WebP)', 'error');
      return;
    }

    stopCamera();
    setSelectedFile(file);
    setImageBlob(file);

    const reader = new FileReader();
    reader.onload = () => {
      setCapturedImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleAnalyze = async () => {
    const fileToUpload = imageBlob || selectedFile;
    if (!fileToUpload) {
      showToast('Please capture or upload a leaf photo first', 'warning');
      return;
    }

    setAnalyzing(true);
    setResult(null);

    try {
      const response = await api.predictDisease(
        fileToUpload,
        selectedFile ? selectedFile.name : 'leaf_capture.jpg'
      );
      setResult(response);
      showToast('Diagnosis completed successfully!', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Disease diagnosis failed', 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900/80 border border-emerald-900/40 rounded-3xl p-6 backdrop-blur-xl shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-950 border border-emerald-600/50 flex items-center justify-center text-emerald-400 shadow-md">
            <Stethoscope className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>{t.diseaseTitle}</span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-900/80 text-emerald-300 border border-emerald-700">
                AI Vision
              </span>
            </h2>
            <p className="text-sm text-slate-400">{t.diseaseSubtitle}</p>
          </div>
        </div>

        {/* Mode Switcher */}
        <div className="flex p-1 bg-slate-950 rounded-2xl border border-slate-800">
          <button
            onClick={() => {
              setMode('camera');
              if (!cameraActive && !capturedImage) startCamera();
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === 'camera'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Camera className="w-4 h-4" /> Camera
          </button>
          <button
            onClick={() => {
              setMode('upload');
              stopCamera();
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === 'upload'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Upload className="w-4 h-4" /> Upload
          </button>
        </div>
      </div>

      {/* Main Studio Viewport */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Visual Capture */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="relative aspect-[4/3] w-full bg-slate-950 rounded-3xl overflow-hidden border border-slate-800 shadow-2xl flex items-center justify-center">
            {/* Live Video Feed */}
            <video
              ref={videoRef}
              playsInline
              muted
              className={`w-full h-full object-cover ${
                cameraActive && !capturedImage ? 'block' : 'hidden'
              }`}
            />

            {/* Hidden Canvas for capture */}
            <canvas ref={canvasRef} className="hidden" />

            {/* Captured Preview */}
            {capturedImage && (
              <img
                src={capturedImage}
                alt="Captured Leaf"
                className="w-full h-full object-cover animate-fade-in"
              />
            )}

            {/* Inactive Camera State */}
            {!cameraActive && !capturedImage && mode === 'camera' && (
              <div className="flex flex-col items-center gap-3 text-slate-400 p-6 text-center">
                <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-emerald-400">
                  <Camera className="w-8 h-8" />
                </div>
                <p className="text-sm font-semibold">{t.cameraGuide}</p>
                <button
                  onClick={() => startCamera()}
                  className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition shadow-lg shadow-emerald-950"
                >
                  {t.openCameraBtn}
                </button>
              </div>
            )}

            {/* File Upload Mode */}
            {mode === 'upload' && !capturedImage && (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center justify-center p-8 text-center cursor-pointer hover:bg-slate-900/50 transition w-full h-full border-2 border-dashed border-slate-800 rounded-3xl"
              >
                <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-emerald-400 mb-3">
                  <Upload className="w-8 h-8" />
                </div>
                <p className="text-sm font-semibold text-slate-200">
                  {t.dropImageHere} <span className="text-emerald-400 underline">{t.browseFiles}</span>
                </p>
                <p className="text-xs text-slate-500 mt-1">JPEG, PNG, WebP (Max 10MB)</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>
            )}

            {/* Camera Viewfinder Overlay when active */}
            {cameraActive && !capturedImage && (
              <div className="absolute inset-0 pointer-events-none p-6 flex flex-col justify-between">
                <div className="flex justify-between items-center text-xs font-semibold text-emerald-300 bg-slate-950/60 px-3 py-1.5 rounded-full border border-emerald-800/60 w-fit backdrop-blur-sm">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-2"></span>
                  Live Viewfinder ({facingMode === 'environment' ? 'Back' : 'Front'})
                </div>
                <div className="border-2 border-dashed border-emerald-400/40 rounded-2xl m-auto w-3/4 h-3/4 pointer-events-none flex items-center justify-center">
                  <span className="text-[11px] text-emerald-300/80 bg-slate-950/70 px-2 py-1 rounded-md">
                    Center Infected Leaf
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Action Button Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-slate-900/80 border border-slate-800 rounded-2xl">
            <div className="flex items-center gap-2">
              {cameraActive && !capturedImage && (
                <>
                  <button
                    onClick={capturePhoto}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-sm shadow-md transition"
                  >
                    <Camera className="w-4 h-4" /> {t.capturePhotoBtn}
                  </button>
                  <button
                    onClick={switchCamera}
                    className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition"
                    title={t.switchCameraBtn}
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </>
              )}

              {capturedImage && (
                <button
                  onClick={retakePhoto}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-bold text-sm transition"
                >
                  <RotateCcw className="w-4 h-4" /> {t.retakeBtn}
                </button>
              )}
            </div>

            {/* Diagnose Button */}
            <button
              onClick={handleAnalyze}
              disabled={analyzing || !imageBlob}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 via-green-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-extrabold text-sm shadow-lg shadow-emerald-950 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {analyzing ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
                  <span>{t.analyzingImage}</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>{t.analyzeDiseaseBtn}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Diagnostic Report Card */}
        <div className="lg:col-span-5 flex flex-col">
          {result ? (
            <div className="bg-slate-900/90 border border-emerald-900/50 rounded-3xl p-6 shadow-2xl space-y-5 animate-fade-in">
              {/* Header Status */}
              <div className="flex items-start justify-between gap-3 border-b border-slate-800 pb-4">
                <div>
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">
                    {result.crop_name} {t.cropLabel}
                  </span>
                  <h3 className="text-2xl font-extrabold text-white mt-0.5">
                    {result.display_name}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{result.class_name}</p>
                </div>

                <div
                  className={`px-3 py-1.5 rounded-full text-xs font-bold border flex items-center gap-1.5 ${
                    result.is_healthy
                      ? 'bg-emerald-950 border-emerald-600 text-emerald-300'
                      : 'bg-red-950 border-red-600 text-red-300'
                  }`}
                >
                  {result.is_healthy ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                  )}
                  <span>{result.is_healthy ? t.statusHealthy : t.statusDiseased}</span>
                </div>
              </div>

              {/* Confidence & Severity Meters */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-950/80 p-3.5 rounded-2xl border border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-400 block mb-1">
                    {t.confidenceLabel}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-800 h-2.5 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-400 h-full rounded-full transition-all duration-1000"
                        style={{ width: `${Math.round(result.confidence * 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-extrabold text-white">
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950/80 p-3.5 rounded-2xl border border-slate-800">
                  <span className="text-[11px] font-semibold text-slate-400 block mb-1">
                    {t.severityLabel}
                  </span>
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-md text-xs font-bold uppercase tracking-wider ${
                      result.severity === 'High'
                        ? 'bg-red-900/60 text-red-300 border border-red-700'
                        : result.severity === 'Moderate'
                        ? 'bg-amber-900/60 text-amber-300 border border-amber-700'
                        : 'bg-emerald-900/60 text-emerald-300 border border-emerald-700'
                    }`}
                  >
                    {result.severity}
                  </span>
                </div>
              </div>

              {/* Description */}
              {result.description && (
                <div className="p-3.5 bg-slate-950/60 rounded-2xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
                  {result.description}
                </div>
              )}

              {/* Step-by-Step ICAR Precautions */}
              {result.precautions && result.precautions.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" /> {t.precautionsTitle}
                  </h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                    {result.precautions.map((p) => (
                      <div
                        key={p.step}
                        className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs"
                      >
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-900 text-emerald-300 flex items-center justify-center font-bold text-[11px]">
                          {p.step}
                        </span>
                        <div>
                          <strong className="text-white block font-semibold">{p.action}</strong>
                          <span className="text-slate-400 leading-relaxed mt-0.5 block">
                            {p.detail}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ask Assistant Shortcut */}
              {onAskAboutDisease && (
                <button
                  onClick={() =>
                    onAskAboutDisease(
                      `Disease detected: ${result.display_name} on ${result.crop_name}. Severity: ${result.severity}. Confidence: ${Math.round(result.confidence * 100)}%. What are the best immediate treatments?`
                    )
                  }
                  className="w-full flex items-center justify-center gap-2 p-3 rounded-2xl bg-emerald-950/70 hover:bg-emerald-900/70 border border-emerald-700/60 text-emerald-300 text-xs font-bold transition shadow-sm"
                >
                  <span>{t.askAssistantAboutDisease}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          ) : (
            <div className="h-full min-h-[380px] bg-slate-900/40 border border-dashed border-slate-800 rounded-3xl p-8 flex flex-col items-center justify-center text-center text-slate-500">
              <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-3">
                <Stethoscope className="w-7 h-7" />
              </div>
              <h4 className="text-base font-bold text-slate-400">{t.diagnosisResult}</h4>
              <p className="text-xs text-slate-500 max-w-xs mt-1">
                Capture or upload a crop leaf image to see disease classification, confidence score, and ICAR treatment steps.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
