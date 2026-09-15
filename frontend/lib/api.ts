// lib/api.ts - Typed API client targeting FastAPI backend at http://localhost:8000

import {
  AssistantRequest,
  AssistantResponse,
  DiseasePredictionResponse,
  AdvisoryRequest,
  AdvisoryResponse,
  WeatherRiskRequest,
  WeatherRiskResponse,
  HealthCheckResponse,
} from '@/types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    let data: any = null;
    try {
      data = await res.json();
      if (data?.detail) {
        errorDetail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      } else if (data?.message) {
        errorDetail = data.message;
      }
    } catch {
      // Body not JSON
    }
    throw new ApiError(errorDetail, res.status, data);
  }
  return res.json();
}

export const api = {
  // Health check probe
  async checkHealth(): Promise<HealthCheckResponse> {
    const res = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      cache: 'no-store',
    });
    return handleResponse<HealthCheckResponse>(res);
  },

  // Module 1: AI Assistant
  async askAssistant(payload: AssistantRequest): Promise<AssistantResponse> {
    const res = await fetch(`${API_BASE}/api/v1/assistant/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<AssistantResponse>(res);
  },

  // Module 2: Crop Disease Doctor
  async predictDisease(imageBlob: Blob | File, filename = 'leaf.jpg'): Promise<DiseasePredictionResponse> {
    const formData = new FormData();
    formData.append('file', imageBlob, filename);

    const res = await fetch(`${API_BASE}/api/v1/disease/predict`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<DiseasePredictionResponse>(res);
  },

  // Module 3: Smart Irrigation & Advisory
  async getAdvisory(payload: AdvisoryRequest): Promise<AdvisoryResponse> {
    const res = await fetch(`${API_BASE}/api/v1/advisory/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<AdvisoryResponse>(res);
  },

  // Module 4: Weather Risk Forecast
  async getWeatherRisk(payload: WeatherRiskRequest): Promise<WeatherRiskResponse> {
    const res = await fetch(`${API_BASE}/api/v1/weather/risk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<WeatherRiskResponse>(res);
  },
};
