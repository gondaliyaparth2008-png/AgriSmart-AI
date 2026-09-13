"""
app/core/supabase_config.py
----------------------------
Supabase credential placeholders for AgriSmart AI.

HOW TO USE
----------
1. Copy the three values below from your Supabase project dashboard.
2. Paste them into backend/.env (NOT here — this file may be committed).
3. Never commit real credentials to version control.

DASHBOARD LOCATIONS
-------------------
  SUPABASE_URL              → Project Settings → API → Project URL
  SUPABASE_PUBLISHABLE_KEY  → Project Settings → API → Project API Keys → anon / public
  DATABASE_URL              → Project Settings → Database → Connection string → URI
                              (use the "Direct connection" URI, NOT the pooler URL)

DATABASE_URL FORMAT (asyncpg)
------------------------------
  postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres

NOTE ON KEYS
------------
  • SUPABASE_PUBLISHABLE_KEY (anon key) is safe to expose to browsers.
    It is used only for Supabase Auth / Storage client calls.
  • DATABASE_URL contains your database password — treat it as a secret.
    Store it ONLY in .env, which is gitignored.
  • Do NOT use the publishable key as the database password.

PLACEHOLDER VALUES (replace in .env, not here)
-----------------------------------------------
"""

# ─── Paste your values into .env — these are reference placeholders only ─────

SUPABASE_URL = "PASTE_YOUR_SUPABASE_PROJECT_URL_HERE"
# e.g. https://xyzxyzxyz.supabase.co

SUPABASE_PUBLISHABLE_KEY = "PASTE_YOUR_SUPABASE_PUBLISHABLE_KEY_HERE"
# e.g. eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

DATABASE_URL = "PASTE_YOUR_SUPABASE_DIRECT_CONNECTION_STRING_HERE"
# e.g. postgresql+asyncpg://postgres.xyzxyzxyz:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
