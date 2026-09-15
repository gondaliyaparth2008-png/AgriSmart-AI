// types/api.ts - AgriSmart AI TypeScript schemas matching FastAPI backend

export type LanguageCode = 'en' | 'hi' | 'gu';

export interface AssistantSource {
  title: string;
  relevance: string;
}

export interface AssistantRequest {
  query: string;
  language?: LanguageCode;
  context?: string;
}

export interface AssistantResponse {
  answer: string;
  language: string;
  follow_up_questions: string[];
  sources: AssistantSource[];
  confidence: 'high' | 'medium' | 'low';
  powered_by: string;
}

export interface PrecautionItem {
  step: number;
  action: string;
  detail: string;
}

export interface AlternativePrediction {
  class_name: string;
  confidence: number;
}

export interface DiseasePredictionResponse {
  class_name: string;
  confidence: number;
  severity: 'Low' | 'Moderate' | 'High' | string;
  is_healthy: boolean;
  display_name: string;
  crop_name: string;
  description: string;
  precautions: PrecautionItem[];
  alternatives?: AlternativePrediction[] | null;
  model_version?: string;
  processing_time_ms?: number | null;
}

export type CropStage =
  | 'germination'
  | 'seedling'
  | 'vegetative'
  | 'flowering'
  | 'fruiting'
  | 'harvest';

export type SoilType =
  | 'clay'
  | 'sandy'
  | 'loamy'
  | 'silty'
  | 'peaty'
  | 'chalky'
  | 'saline';

export type IrrigationMethod =
  | 'drip'
  | 'sprinkler'
  | 'flood'
  | 'furrow'
  | 'none';

export interface AdvisoryRequest {
  crop_name: string;
  crop_stage: CropStage;
  soil_type: SoilType;
  ph: number;
  moisture: number;
  temperature: number;
  rain_prob: number;
  current_irrigation_method?: IrrigationMethod;
}

export interface IrrigationScheduleItem {
  day_offset: number;
  duration_minutes: number;
  water_volume_liters_per_sqm: number;
  notes: string;
}

export interface AdvisoryResponse {
  crop_name: string;
  crop_stage: string;
  should_irrigate_today: boolean;
  recommended_method: IrrigationMethod;
  irrigation_schedule: IrrigationScheduleItem[];
  sustainability_score: number;
  sustainability_rating: 'Excellent' | 'Good' | 'Fair' | 'Poor' | string;
  soil_health_notes: string[];
  risk_flags: string[];
  actionable_tips: string[];
}

export interface WeatherRiskRequest {
  location: string;
  crop_name?: string;
  days_ahead?: number;
}

export interface DailyForecastItem {
  date: string;
  temp_max_c?: number;
  temp_min_c?: number;
  temperature_c?: number;
  humidity_pct: number;
  rain_mm: number;
  wind_kph: number;
  condition: string;
  day_risk_score?: number;
}

export interface WeatherRiskResponse {
  location: string;
  forecast_days: number;
  overall_risk_level: 'Low' | 'Moderate' | 'High' | 'Severe' | string;
  risk_index: number;
  daily_forecast: DailyForecastItem[];
  recommendations: string[];
  data_source: string;
}

export interface HealthCheckResponse {
  status: string;
  app_name?: string;
  version?: string;
  timestamp?: string;
}
