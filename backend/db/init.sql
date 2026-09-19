-- NEXTO MVP 스키마 (명세서 v3.0 10장)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(100),
  password_hash TEXT,
  photo TEXT,
  cover TEXT,
  notes JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE content_shares (
  share_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  text TEXT,
  original_url TEXT,
  input_hash VARCHAR(64),
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_shares_hash ON content_shares(input_hash);

CREATE TABLE media_assets (
  asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  share_id UUID NOT NULL REFERENCES content_shares(share_id) ON DELETE CASCADE,
  storage_key TEXT NOT NULL,
  asset_order INT DEFAULT 0
);

CREATE TABLE analysis_jobs (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  share_id UUID NOT NULL REFERENCES content_shares(share_id),
  status VARCHAR(20) NOT NULL DEFAULT 'QUEUED',
  stage VARCHAR(20),
  stage_results JSONB DEFAULT '{}'::jsonb,
  error_code VARCHAR(50),
  error_message TEXT,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ
);

CREATE TABLE extractions (
  extraction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  share_id UUID NOT NULL REFERENCES content_shares(share_id),
  model_name VARCHAR(100),
  schema_version VARCHAR(20) DEFAULT 'v3.0',
  payload_json JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE source_documents (
  source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  extraction_id UUID NOT NULL REFERENCES extractions(extraction_id),
  url TEXT NOT NULL,
  url_hash VARCHAR(64),
  domain_type VARCHAR(30),
  title TEXT,
  published_at DATE,
  excerpt TEXT,
  rank INT DEFAULT 0
);
CREATE INDEX idx_sources_hash ON source_documents(url_hash);

CREATE TABLE verification_results (
  verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  extraction_id UUID NOT NULL REFERENCES extractions(extraction_id),
  fields_json JSONB NOT NULL,
  overall_grade VARCHAR(20),
  verified_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE saved_items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  extraction_id UUID REFERENCES extractions(extraction_id),
  title VARCHAR(200) NOT NULL,
  category VARCHAR(30),
  status VARCHAR(20) DEFAULT 'ACTIVE',
  fields_json JSONB NOT NULL,
  user_overrides TEXT[],
  primary_source_id UUID REFERENCES source_documents(source_id),
  overall_grade VARCHAR(20),
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_items_user_status ON saved_items(user_id, status);

CREATE TABLE calendar_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL REFERENCES saved_items(item_id) ON DELETE CASCADE,
  event_type VARCHAR(20) NOT NULL,
  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ,
  all_day BOOLEAN DEFAULT true,
  date_status VARCHAR(20) DEFAULT 'EXACT'
);
CREATE INDEX idx_events_start ON calendar_events(start_at);

-- 데모 사용자
INSERT INTO users (user_id, email, name) VALUES ('00000000-0000-0000-0000-000000000001', 'demo@nexto.app', '데모 사용자');
