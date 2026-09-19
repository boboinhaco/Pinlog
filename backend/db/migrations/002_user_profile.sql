-- 로그인 + 개인 페이지 설정 (비밀번호 해시, 아치 사진, 커버 사진, 퀵노트)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS photo TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS cover TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS notes JSONB DEFAULT '[]'::jsonb;
