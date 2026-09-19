import re
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

# SNS는 로그인 벽 대신 링크 미리보기(OG 태그)를 주는 크롤러 UA가 필요
CRAWLER_UA = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
SNS_HOSTS = ("instagram.com", "facebook.com", "threads.net", "threads.com", "x.com", "twitter.com", "tiktok.com")
MAX_PAGE_TEXT = 6000


def _meta(soup: BeautifulSoup, key: str) -> str | None:
    tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
    return tag.get("content") if tag and tag.get("content") else None


# 본문 텍스트: 스크립트/내비 제거 후 공백 정리
def page_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "nav", "footer", "header", "svg", "form"]): t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ")).strip()[:MAX_PAGE_TEXT]


# 링크 → 제목·캡션·본문·대표 이미지 URL (실패해도 사용자 입력 텍스트로 계속 진행)
async def fetch_link(url: str) -> dict:
    host = urlparse(url).netloc.lower()
    is_sns = any(host.endswith(h) for h in SNS_HOSTS)
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers={"User-Agent": CRAWLER_UA if is_sns else BROWSER_UA, "Accept-Language": "ko-KR,ko;q=0.9"}) as client:
            res = await client.get(url)
        res.raise_for_status()
    except Exception as e:
        return {"url": url, "error": f"링크를 열 수 없어요: {e.__class__.__name__}"}
    soup = BeautifulSoup(res.text, "html.parser")
    title = _meta(soup, "og:title") or (soup.title.string.strip() if soup.title and soup.title.string else None)
    desc = _meta(soup, "og:description") or _meta(soup, "description")
    body = "" if is_sns else page_text(res.text)
    return {"url": url, "is_sns": is_sns, "title": title, "description": desc, "body": body, "image_url": _meta(soup, "og:image")}


async def download_image(url: str | None) -> tuple[str, bytes] | None:
    if not url: return None
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers={"User-Agent": BROWSER_UA}) as client:
            res = await client.get(url)
        mime = res.headers.get("content-type", "").split(";")[0]
        if res.status_code == 200 and mime.startswith("image/") and len(res.content) < 6_000_000: return mime, res.content
    except Exception:
        pass
    return None


# A1: 링크·텍스트·이미지 경로를 하나의 이해 결과로 (이미지 해석은 추출 단계 LLM이 담당)
async def run(text: str, image_paths: list[str], url: str | None = None) -> dict:
    link = await fetch_link(url) if url else None
    parts = [text.strip()] if text.strip() else []
    if link and not link.get("error"):
        parts += [p for p in (link.get("title"), link.get("description"), link.get("body")) if p]
    return {"text": text, "url": url, "link": link, "image_paths": image_paths, "image_count": len(image_paths),
            "summary": "\n\n".join(parts)[:MAX_PAGE_TEXT + 2000]}
