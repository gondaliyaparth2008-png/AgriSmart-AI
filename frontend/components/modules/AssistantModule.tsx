// components/modules/AssistantModule.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Send,
  Trash2,
  Bot,
  User,
  Sparkles,
  HelpCircle,
  BookOpen,
  Volume2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';
import { useToast } from '@/context/ToastContext';
import { api } from '@/lib/api';
import { AssistantResponse, AssistantSource } from '@/types/api';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  confidence?: string;
  sources?: AssistantSource[];
  followUps?: string[];
}

export function AssistantModule() {
  const { language, t, speechLocale } = useLanguage();
  const { showToast } = useToast();

  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');

  const chatEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize with welcome message if empty
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          sender: 'assistant',
          text: t.welcomeMessage,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          followUps: t.sampleQuestions,
        },
      ]);
    }
  }, [t.welcomeMessage, t.sampleQuestions, messages.length]);

  // Auto scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, interimTranscript, isListening]);

  // Clean up speech recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // Web Speech API Handler
  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      setInterimTranscript('');
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      showToast(t.speechNotSupported, 'error');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      recognition.lang = speechLocale; // 'gu-IN', 'hi-IN', or 'en-IN'
      recognition.interimResults = true;
      recognition.continuous = false;

      recognition.onstart = () => {
        setIsListening(true);
        setInterimTranscript('');
      };

      recognition.onresult = (event: any) => {
        let final = '';
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (final) {
          setInputQuery((prev) => (prev ? `${prev} ${final.trim()}` : final.trim()));
          setInterimTranscript('');
        } else {
          setInterimTranscript(interim);
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        if (event.error !== 'no-speech') {
          showToast(`Speech error: ${event.error}`, 'error');
        }
        setIsListening(false);
        setInterimTranscript('');
      };

      recognition.onend = () => {
        setIsListening(false);
        setInterimTranscript('');
      };

      recognition.start();
    } catch (err: any) {
      console.error('Speech recognition failed to start:', err);
      showToast(err?.message || 'Failed to start speech recognition', 'error');
      setIsListening(false);
    }
  };

  const handleSend = async (queryText?: string) => {
    const query = (queryText || inputQuery).trim();
    if (!query || loading) return;

    // Stop listening if active
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }

    const userMessage: ChatMessage = {
      id: Math.random().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setInterimTranscript('');
    setLoading(true);

    try {
      const response: AssistantResponse = await api.askAssistant({
        query: query,
        language: language,
      });

      const assistantMessage: ChatMessage = {
        id: Math.random().toString(),
        sender: 'assistant',
        text: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        confidence: response.confidence,
        sources: response.sources,
        followUps: response.follow_up_questions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      showToast(err?.message || 'Failed to get answer from Assistant', 'error');
      const errorMessage: ChatMessage = {
        id: Math.random().toString(),
        sender: 'assistant',
        text: 'Sorry, I could not reach the server. Please ensure the backend is running at http://localhost:8000 and try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        id: 'welcome-new',
        sender: 'assistant',
        text: t.welcomeMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        followUps: t.sampleQuestions,
      },
    ]);
    showToast('Conversation cleared', 'info');
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col h-[calc(100vh-140px)] min-h-[580px] bg-slate-900/60 border border-emerald-900/40 rounded-3xl shadow-2xl overflow-hidden backdrop-blur-xl">
      {/* Module Header */}
      <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-900/50 border border-emerald-600/40 flex items-center justify-center text-emerald-400 shadow-sm">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>{t.assistantTitle}</span>
              <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-300">
                {language.toUpperCase()}
              </span>
            </h2>
            <p className="text-xs text-slate-400">{t.assistantSubtitle}</p>
          </div>
        </div>

        <button
          onClick={clearConversation}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-transparent hover:border-slate-700 transition"
          title={t.clearChat}
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Chat Messages Body */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-[88%] sm:max-w-[78%] ${
                isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
              } animate-fade-in`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold shadow ${
                  isUser
                    ? 'bg-gradient-to-tr from-emerald-600 to-emerald-500 text-white'
                    : 'bg-slate-800 border border-slate-700 text-emerald-400'
                }`}
              >
                {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              {/* Bubble */}
              <div className="space-y-2">
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-md ${
                    isUser
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 text-white rounded-tr-none'
                      : 'bg-slate-950/90 border border-slate-800 text-slate-200 rounded-tl-none'
                  }`}
                >
                  <p>{msg.text}</p>

                  <div
                    className={`mt-2 flex items-center justify-between text-[10px] font-medium ${
                      isUser ? 'text-emerald-200' : 'text-slate-500'
                    }`}
                  >
                    <span>{msg.timestamp}</span>
                    {msg.confidence && (
                      <span className="flex items-center gap-1 uppercase tracking-wider text-emerald-400 font-bold">
                        <Sparkles className="w-3 h-3" /> {msg.confidence} {t.confidenceLabel}
                      </span>
                    )}
                  </div>
                </div>

                {/* Sources if present */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-2.5 text-xs text-slate-400 space-y-1">
                    <div className="font-semibold text-emerald-400 flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5" /> {t.sourcesTitle}:
                    </div>
                    {msg.sources.map((src, idx) => (
                      <div key={idx} className="pl-4 text-[11px] border-l-2 border-emerald-700/50">
                        <span className="font-bold text-slate-300">{src.title}:</span> {src.relevance}
                      </div>
                    ))}
                  </div>
                )}

                {/* Follow-up question chips */}
                {msg.followUps && msg.followUps.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                      <HelpCircle className="w-3 h-3 text-emerald-400" /> {t.followUpTitle}:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.followUps.map((chip, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(chip)}
                          disabled={loading}
                          className="px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-emerald-900/60 border border-slate-700 hover:border-emerald-600/60 text-emerald-300 text-xs text-left transition-all duration-200 shadow-sm disabled:opacity-50"
                        >
                          {chip}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Interim Speech Transcript preview */}
        {isListening && interimTranscript && (
          <div className="flex gap-3 max-w-[85%] ml-auto flex-row-reverse animate-pulse">
            <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
              <Mic className="w-5 h-5 animate-bounce" />
            </div>
            <div className="p-3 bg-emerald-950/80 border border-emerald-700 text-emerald-200 text-xs rounded-2xl rounded-tr-none italic">
              {interimTranscript}...
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-3 max-w-[75%] mr-auto items-center text-slate-400 text-xs animate-pulse">
            <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-emerald-400">
              <Bot className="w-5 h-5" />
            </div>
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
              <span>AgriSmart AI is thinking...</span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Voice Listening Feedback Banner */}
      {isListening && (
        <div className="px-6 py-2 bg-gradient-to-r from-emerald-950 via-green-900 to-emerald-950 border-t border-emerald-700/60 flex items-center justify-between text-xs text-emerald-300 font-semibold animate-pulse">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
            <span>{t.listeningNow} ({speechLocale})</span>
          </div>
          <button
            onClick={toggleListening}
            className="px-2.5 py-0.5 rounded-lg bg-red-950 border border-red-700 text-red-300 text-[11px] font-bold"
          >
            Stop
          </button>
        </div>
      )}

      {/* Input Form Bar */}
      <div className="p-4 bg-slate-950 border-t border-slate-800/80">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          {/* Microphone Button */}
          <button
            type="button"
            onClick={toggleListening}
            className={`relative p-3.5 rounded-2xl transition-all duration-300 flex items-center justify-center ${
              isListening
                ? 'bg-red-600 text-white shadow-lg shadow-red-900/60 animate-bounce'
                : 'bg-slate-800 hover:bg-slate-700 border border-slate-700 text-emerald-400 hover:text-emerald-300'
            }`}
            title={t.voiceTooltip}
          >
            {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={isListening ? t.listeningNow : t.askPlaceholder}
            disabled={loading}
            className="flex-1 px-4 py-3.5 rounded-2xl bg-slate-900 border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-white placeholder-slate-500 text-sm outline-none transition"
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="p-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold transition shadow-lg shadow-emerald-950/80 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center"
            title={t.sendBtn}
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
