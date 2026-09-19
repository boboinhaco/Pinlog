import json
from pathlib import Path
from ..core.config import settings

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "demo"
_fail_count = 0


# 외부 API 연속 실패 카운트, 3회면 fixture fallback
def record_failure() -> bool:
    global _fail_count
    _fail_count += 1
    return _fail_count >= 3


def reset_failures():
    global _fail_count
    _fail_count = 0


# 데모 샘플 fixture 로드 (share text/링크로 매칭, 없으면 None)
def load_fixture(text: str) -> dict | None:
    if not settings.demo_mode: return None
    for f in FIXTURE_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        if any(k in text for k in data.get("match_keywords", [])): return data
    return None
