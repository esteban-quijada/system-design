import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Generator, Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# DATABASE_URL can be overridden directly (e.g. sqlite:///:memory: in tests)
DATABASE_URL = os.environ.get("DATABASE_URL") or (
    "postgresql://{user}:{password}@{host}:{port}/{db}".format(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ.get("POSTGRES_PORT", "5432"),
        db=os.environ["POSTGRES_DB"],
    )
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class URLRecord(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    click_count = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ShortenRequest(BaseModel):
    url: HttpUrl
    expires_in_hours: Optional[int] = None


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None


class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    click_count: int
    expires_at: Optional[datetime] = None


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: Request, body: ShortenRequest, db: Session = Depends(get_db)):
    short_code = secrets.token_urlsafe(6)
    expires_at = None
    if body.expires_in_hours is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=body.expires_in_hours)
    record = URLRecord(
        short_code=short_code,
        original_url=str(body.url),
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    base_url = str(request.base_url)
    return ShortenResponse(
        short_code=short_code,
        short_url=f"{base_url}{short_code}",
        created_at=record.created_at,
        expires_at=expires_at,
    )


@app.get("/stats/{short_code}", response_model=StatsResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    record = db.query(URLRecord).filter(URLRecord.short_code == short_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return StatsResponse(
        short_code=record.short_code,
        original_url=record.original_url,
        created_at=record.created_at,
        click_count=record.click_count,
        expires_at=record.expires_at,
    )


@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    record = db.query(URLRecord).filter(URLRecord.short_code == short_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")
    expires_at = record.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at and datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=410, detail="Short URL has expired")
    record.click_count += 1
    db.commit()
    return RedirectResponse(url=record.original_url)
