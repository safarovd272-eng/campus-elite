from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    BigInteger, Integer, String, Boolean, DateTime, Text, ForeignKey, func
)
from datetime import datetime
from typing import Optional, List

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    faculty: Mapped[str] = mapped_column(String(100), nullable=False)
    course_year: Mapped[str] = mapped_column(String(50), nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    badge_level: Mapped[str] = mapped_column(String(50), default="none")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime)

    submissions: Mapped[List["Submission"]] = relationship(back_populates="user")
    points_log: Mapped[List["PointsLog"]] = relationship(back_populates="user")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    activity_code: Mapped[str] = mapped_column(String(50), nullable=False)
    proof_type: Mapped[str] = mapped_column(String(20))  # photo, document, url
    proof_data: Mapped[str] = mapped_column(Text)  # file_id yoki url
    proof_description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/approved/rejected
    admin_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    admin_note: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    points_awarded: Mapped[Optional[int]] = mapped_column(Integer)
    hash_fingerprint: Mapped[Optional[str]] = mapped_column(String(64))

    user: Mapped["User"] = relationship(back_populates="submissions")


class PointsLog(Base):
    __tablename__ = "points_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(300))
    source: Mapped[str] = mapped_column(String(50))  # submission / manual / system
    submission_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("submissions.id"))
    added_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="points_log")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
