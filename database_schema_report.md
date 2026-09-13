# AgriSmart-AI Database Schema Report

Based on my inspection of your FastAPI backend (specifically the ORM models defined in `app/models/`), your code expects two tables to exist in the database: `prediction_logs` and `advisory_logs`.

Below is the detailed schema breakdown for both tables, followed by the SQL statements you can run in your Supabase SQL Editor.

## 1. Table: `prediction_logs`
*Defined in: `app/models/prediction_log.py`*

**Purpose:** Logs every disease prediction request (POST `/api/v1/disease/predict`) for audit trails and future model fine-tuning.

| Column Name | PostgreSQL Type | Primary Key | Foreign Key | Nullable | Default Value | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | **Yes** | No | No | Auto-incrementing (`SERIAL`) | Indexed |
| `image_name` | `VARCHAR(255)` | No | No | **Yes** | None | Original filename of uploaded image |
| `predicted_disease` | `VARCHAR(128)` | No | No | No | None | Top disease class label (Indexed) |
| `confidence` | `DOUBLE PRECISION` / `FLOAT` | No | No | No | None | Prediction confidence score (0.0 - 1.0) |
| `is_healthy` | `BOOLEAN` | No | No | No | `FALSE` | True when plant predicted as healthy |
| `severity` | `VARCHAR(16)` | No | No | **Yes** | None | "None" / "Low" / "Moderate" / "High" |
| `model_version` | `VARCHAR(32)` | No | No | **Yes** | None | Identifier of the model version |
| `processing_time_ms`| `DOUBLE PRECISION` / `FLOAT` | No | No | **Yes** | None | Server-side inference time in ms |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | No | No | `now()` / `timezone.utc` | UTC timestamp of request |

**Relationships:** None. This table operates independently.

---

## 2. Table: `advisory_logs`
*Defined in: `app/models/advisory_log.py`*

**Purpose:** Logs every irrigation advisory request (POST `/api/v1/advisory/recommend`) for retrospective analysis.

| Column Name | PostgreSQL Type | Primary Key | Foreign Key | Nullable | Default Value | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | **Yes** | No | No | Auto-incrementing (`SERIAL`) | Indexed |
| `crop_type` | `VARCHAR(64)` | No | No | No | None | Name of crop (Indexed) |
| `crop_stage` | `VARCHAR(32)` | No | No | **Yes** | None | e.g. germination / flowering |
| `soil_type` | `VARCHAR(32)` | No | No | **Yes** | None | e.g. clay / sandy / loamy |
| `ph` | `DOUBLE PRECISION` / `FLOAT` | No | No | **Yes** | None | Soil pH reading (0-14) |
| `moisture` | `DOUBLE PRECISION` / `FLOAT` | No | No | **Yes** | None | Soil moisture percentage (0-100) |
| `temperature` | `DOUBLE PRECISION` / `FLOAT` | No | No | **Yes** | None | Ambient temperature in °C |
| `rain_prob` | `DOUBLE PRECISION` / `FLOAT` | No | No | **Yes** | None | Probability of rain in 24h (0.0-1.0) |
| `should_irrigate` | `BOOLEAN` | No | No | **Yes** | None | Whether irrigation was recommended |
| `sustainability_score`| `DOUBLE PRECISION` / `FLOAT`| No | No | **Yes** | None | Computed sustainability score (0-100)|
| `recommendation` | `TEXT` | No | No | **Yes** | None | Summarised recommendation text |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | No | No | `now()` / `timezone.utc` | UTC timestamp of request |

**Relationships:** None. This table operates independently.

---

## Supabase Status
Your current Supabase `DATABASE_URL` in the `.env` file contains a placeholder password (`[AgriSmart-Ai]`). Therefore, **the backend cannot currently connect to Supabase** to verify if these tables exist. 

If this is a fresh Supabase project, they do not exist yet. However, the FastAPI app is set up to automatically create these tables on startup via SQLAlchemy's `Base.metadata.create_all` if the connection is successful. If you prefer to manage the database structure manually via Supabase, you can run the SQL below.

---

## Recommended SQL CREATE TABLE Statements

You can copy and paste the following SQL directly into the **SQL Editor** on your Supabase dashboard to create these tables.

```sql
-- --------------------------------------------------------
-- Table: prediction_logs
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.prediction_logs (
    id SERIAL PRIMARY KEY,
    image_name VARCHAR(255),
    predicted_disease VARCHAR(128) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    is_healthy BOOLEAN NOT NULL DEFAULT FALSE,
    severity VARCHAR(16),
    model_version VARCHAR(32),
    processing_time_ms DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create index on commonly queried columns
CREATE INDEX IF NOT EXISTS ix_prediction_logs_predicted_disease ON public.prediction_logs(predicted_disease);
CREATE INDEX IF NOT EXISTS ix_prediction_logs_id ON public.prediction_logs(id);

-- --------------------------------------------------------
-- Table: advisory_logs
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.advisory_logs (
    id SERIAL PRIMARY KEY,
    crop_type VARCHAR(64) NOT NULL,
    crop_stage VARCHAR(32),
    soil_type VARCHAR(32),
    ph DOUBLE PRECISION,
    moisture DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    rain_prob DOUBLE PRECISION,
    should_irrigate BOOLEAN,
    sustainability_score DOUBLE PRECISION,
    recommendation TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create index on commonly queried columns
CREATE INDEX IF NOT EXISTS ix_advisory_logs_crop_type ON public.advisory_logs(crop_type);
CREATE INDEX IF NOT EXISTS ix_advisory_logs_id ON public.advisory_logs(id);
```

> [!TIP]
> Once you've created these tables in Supabase (or once you enter the correct `DATABASE_URL` in your `.env` so SQLAlchemy can create them for you), your backend's database structure will be fully configured and ready for the frontend.
