from typing import Literal, Optional
from pydantic import BaseModel

Category = Literal["POLICY_HOUSING", "POLICY_JOB", "POLICY_LIVING", "SUBSCRIPTION", "FINANCE", "EVENT", "RECRUIT", "CONTEST", "OTHER"]
FieldStatus = Literal["VERIFIED", "REFINED", "CONFLICT", "ADDED", "AMBIGUOUS", "UNVERIFIED"]
Grade = Literal["HIGH", "REVIEW", "UNVERIFIED"]
DomainType = Literal["OFFICIAL_GOV", "OFFICIAL_PUBLIC", "OFFICIAL_FINANCE", "OFFICIAL_ORGANIZER", "SECONDARY", "UNKNOWN"]
Stage = Literal["UNDERSTAND", "EXTRACT", "NORMALIZE", "SEARCH", "VERIFY", "DONE"]


class Period(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    status: Literal["exact", "ambiguous", "unknown"] = "unknown"


# 장소 (지도 표시용 좌표 포함)
class Place(BaseModel):
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


# 한 게시물에서 나온 개별 일정 후보
class EventCandidate(BaseModel):
    title: str
    category: Category = "EVENT"
    event_period: Period = Period()
    location: Optional[Place] = None
    image_url: Optional[str] = None


# FR-03 구조화 추출 결과
class ExtractionPayload(BaseModel):
    title: str
    category: Category = "OTHER"
    summary: Optional[str] = None              # 이 게시물이 알려주는 내용 요약
    organization: Optional[str] = None
    benefit_amount: Optional[dict] = None       # {text, value, unit, period}
    target: Optional[dict] = None               # {text, age_min, age_max, region}
    eligibility: list[str] = []                 # 자격요건
    apply_period: Period = Period()             # 신청 기간 / 마감
    event_period: Optional[Period] = None       # 행사 기간
    location: Optional[dict] = None             # {name, address, lat, lng}
    requirements: list[str] = []                # 준비 서류
    key_points: list[str] = []                  # 그 밖의 정보 요약
    notice: Optional[str] = None                # 링크만으로 알 수 없는 정보 안내 (예: 상세가 이미지 슬라이드에 있음)
    raw_evidence: list[str] = []
    events: list[EventCandidate] = []
    image_url: Optional[str] = None


class SourceDoc(BaseModel):
    url: str
    domain_type: DomainType = "UNKNOWN"
    title: str = ""
    published_at: Optional[str] = None
    excerpt: str = ""
    rank: int = 0


class FieldResult(BaseModel):
    field: str
    sns_value: Optional[object] = None
    official_value: Optional[object] = None
    status: FieldStatus
    evidence: Optional[str] = None


# FR-05 검증 결과, 숫자 confidence 없음
class VerificationPayload(BaseModel):
    primary_source: Optional[SourceDoc] = None
    fields: list[FieldResult] = []
    overall_grade: Grade = "UNVERIFIED"
    official_summary: Optional[str] = None      # 공식 공고 기준 요약
    official: dict = {}                         # 공식 출처의 구조화 값 (apply_period, target, eligibility ...)


# 검토 화면에서 사용자가 확인한 항목들 (정책/상품 1건 또는 행사 여러 건)
class ConfirmItem(BaseModel):
    title: str
    category: Category = "OTHER"
    fields: dict
    user_overrides: list[str] = []


class ConfirmItemsRequest(BaseModel):
    items: list[ConfirmItem]


# 링크 없이 직접 추가하는 일정
class ManualItemRequest(BaseModel):
    title: str
    category: Category = "OTHER"
    fields: dict = {}


class UpdateItemRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[Category] = None
    fields: Optional[dict] = None
    status: Optional[str] = None
