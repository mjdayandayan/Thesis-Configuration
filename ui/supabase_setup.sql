-- ============================================================
-- Rice Growth Monitoring System — Supabase Database Setup
-- ============================================================
-- Run this in your Supabase project: SQL Editor → New Query
-- This creates the table and policies needed for the system.
-- ============================================================

-- 1. Create the readings table
CREATE TABLE IF NOT EXISTS readings (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    timestamp TIMESTAMPTZ NOT NULL,
    soil_moisture REAL,
    soil_temperature REAL,
    ec REAL,
    ph REAL,
    soil_humidity REAL,
    prediction_label TEXT,
    prediction_confidence REAL,
    detections JSONB DEFAULT '[]',
    image_url TEXT,
    alerts JSONB DEFAULT '[]'
);

-- 2. Create index for faster queries by timestamp
CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings (timestamp DESC);

-- 3. Enable Row Level Security
ALTER TABLE readings ENABLE ROW LEVEL SECURITY;

-- 4. Allow public read access (for the Streamlit dashboard)
CREATE POLICY "Allow public read" ON readings
    FOR SELECT USING (true);

-- 5. Allow public insert (for the Raspberry Pi to send data)
CREATE POLICY "Allow public insert" ON readings
    FOR INSERT WITH CHECK (true);

-- ============================================================
-- IMPORTANT: Also create a Storage bucket for field images.
-- This CANNOT be done via SQL — use the Supabase dashboard:
--
--   1. Go to Storage in the left sidebar
--   2. Click "New Bucket"
--   3. Name it: field-images
--   4. Check "Public bucket" (so images display in the dashboard)
--   5. Click "Create bucket"
--   6. Go to the bucket → Policies → Add policy
--   7. Add a policy for INSERT (allow all) so the RPi can upload
--   8. Add a policy for SELECT (allow all) so the dashboard can view
-- ============================================================
