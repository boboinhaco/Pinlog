import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Boolean, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def uid():
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = uid()
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str | None] = mapped_column(String(100))
    password_hash: Mapped[str | None] = mapped_column(Text)
    photo: Mapped[str | None] = mapped_column(Text)        # 아치 사진 (data URL)
    cover: Mapped[str | None] = mapped_column(Text)        # 헤더 커버 사진 (data URL)
    notes: Mapped[list | None] = mapped_column(JSONB, default=list)  # 퀵노트 [{text, done}]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 사용자가 공유한 원본 요청 단위
class ContentShare(Base):
    __tablename__ = "content_shares"
    share_id: Mapped[uuid.UUID] = uid()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"))
    text: Mapped[str | None] = mapped_column(Text)
    original_url: Mapped[str | None] = mapped_column(Text)
    input_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MediaAsset(Base):
    __tablename__ = "media_assets"
    asset_id: Mapped[uuid.UUID] = uid()
    share_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_shares.share_id", ondelete="CASCADE"))
    storage_key: Mapped[str] = mapped_column(Text)
    asset_order: Mapped[int] = mapped_column(Integer, default=0)


# 비동기 분석 Job, 단계별 결과를 stage_results에 보관해 부분 재시도 가능
class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    job_id: Mapped[uuid.UUID] = uid()
    share_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_shares.share_id"))
    status: Mapped[str] = mapped_column(String(20), default="QUEUED")
    stage: Mapped[str | None] = mapped_column(String(20))
    stage_results: Mapped[dict] = mapped_column(JSONB, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# AI 초안 (사용자 확정값과 분리)
class Extraction(Base):
    __tablename__ = "extractions"
    extraction_id: Mapped[uuid.UUID] = uid()
    share_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_shares.share_id"))
    model_name: Mapped[str | None] = mapped_column(String(100))
    schema_version: Mapped[str] = mapped_column(String(20), default="v3.0")
    payload_json: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourceDocument(Base):
    __tablename__ = "source_documents"
    source_id: Mapped[uuid.UUID] = uid()
    extraction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extractions.extraction_id"))
    url: Mapped[str] = mapped_column(Text)
    url_hash: Mapped[str] = mapped_column(String(64), index=True)
    domain_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[date | None] = mapped_column(Date)
    excerpt: Mapped[str | None] = mapped_column(Text)
    rank: Mapped[int] = mapped_column(Integer, default=0)


class VerificationResult(Base):
    __tablename__ = "verification_results"
    verification_id: Mapped[uuid.UUID] = uid()
    extraction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extractions.extraction_id"))
    fields_json: Mapped[list] = mapped_column(JSONB)
    overall_grade: Mapped[str] = mapped_column(String(20))
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 사용자가 확정 저장한 값
class SavedItem(Base):
    __tablename__ = "saved_items"
    item_id: Mapped[uuid.UUID] = uid()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), index=True)
    extraction_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("extractions.extraction_id"))
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    fields_json: Mapped[dict] = mapped_column(JSONB)
    user_overrides: Mapped[list | None] = mapped_column(ARRAY(String))
    primary_source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("source_documents.source_id"))
    overall_grade: Mapped[str | None] = mapped_column(String(20))
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    event_id: Mapped[uuid.UUID] = uid()
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("saved_items.item_id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(20))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    all_day: Mapped[bool] = mapped_column(Boolean, default=True)
    date_status: Mapped[str] = mapped_column(String(20), default="EXACT")
