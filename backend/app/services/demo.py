import json
from pathlib import Path
from ..core.config import settings

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "demo"


# 데모 샘플 fixture 로드 (share text/링크로 매칭, 없으면 None)
def load_fixture(text: str) -> dict | None:
    if not settings.demo_mode: return None
    for f in FIXTURE_DIR.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        if any(k in text for k in data.get("match_keywords", [])): return data
    return None
