-- Financial Compliance Auditor - Supabase Schema
-- Run this in your Supabase SQL Editor to create the tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,                    -- Discord user ID or web session ID
    source TEXT NOT NULL,                   -- 'discord' or 'web'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audits table
CREATE TABLE IF NOT EXISTS audits (
    audit_id TEXT PRIMARY KEY,              -- e.g. 'aud_abc123'
    user_id TEXT REFERENCES users(id),
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL,            -- 'SOX 404', '10-K', '8-K', 'Invoice'
    score INTEGER NOT NULL,
    grade TEXT NOT NULL,                    -- 'A', 'B', 'C', 'D', 'F'
    executive_summary TEXT,
    report_pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit gaps table
CREATE TABLE IF NOT EXISTS audit_gaps (
    id SERIAL PRIMARY KEY,
    audit_id TEXT REFERENCES audits(audit_id) ON DELETE CASCADE,
    severity TEXT NOT NULL,                 -- 'critical', 'high', 'medium'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    regulation TEXT NOT NULL
);

-- Gap locations table (for PDF highlighting)
CREATE TABLE IF NOT EXISTS gap_locations (
    id SERIAL PRIMARY KEY,
    gap_id INTEGER REFERENCES audit_gaps(id) ON DELETE CASCADE,
    page INTEGER NOT NULL,
    quote TEXT NOT NULL,
    context TEXT
);

-- Audit remediations table
CREATE TABLE IF NOT EXISTS audit_remediations (
    id SERIAL PRIMARY KEY,
    audit_id TEXT REFERENCES audits(audit_id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    description TEXT NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audits_user_id ON audits(user_id);
CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_gaps_audit_id ON audit_gaps(audit_id);
CREATE INDEX IF NOT EXISTS idx_gap_locations_gap_id ON gap_locations(gap_id);
CREATE INDEX IF NOT EXISTS idx_audit_remediations_audit_id ON audit_remediations(audit_id);

-- Row Level Security (RLS) policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE gap_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_remediations ENABLE ROW LEVEL SECURITY;

-- For hackathon, allow all operations with service role key
-- In production, you'd add proper policies based on user authentication
CREATE POLICY "Allow all for service role" ON users FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON audits FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON audit_gaps FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON gap_locations FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON audit_remediations FOR ALL USING (true);
