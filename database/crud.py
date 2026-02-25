from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Optional, List
import hashlib

from database.db import User, Submission, PointsLog, async_session
from config import ACTIVITIES, BADGE_THRESHOLDS


# ===== USER CRUD =====

async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


async def create_user(
    telegram_id: int,
    full_name: str,
    faculty: str,
    course_year: str,
    student_id: str,
    phone_number: Optional[str] = None
) -> User:
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            faculty=faculty,
            course_year=course_year,
            student_id=student_id,
            phone_number=phone_number,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_student_id_exists(student_id: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.student_id == student_id)
        )
        return result.scalar_one_or_none() is not None


# ===== LEADERBOARD =====

async def get_leaderboard(limit: int = 10, faculty: Optional[str] = None,
                           course: Optional[str] = None) -> List[User]:
    async with async_session() as session:
        query = select(User).where(User.is_active == True)
        if faculty:
            query = query.where(User.faculty == faculty)
        if course:
            query = query.where(User.course_year == course)
        query = query.order_by(desc(User.total_points)).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())


async def get_user_rank(telegram_id: int) -> int:
    async with async_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return 0
        rank_result = await session.execute(
            select(func.count()).where(
                and_(User.total_points > user.total_points, User.is_active == True)
            )
        )
        return rank_result.scalar() + 1


# ===== POINTS =====

async def add_points(user_id: int, points: int, reason: str,
                     source: str = "manual", submission_id: Optional[int] = None,
                     added_by: Optional[int] = None) -> User:
    async with async_session() as session:
        # Points log
        log = PointsLog(
            user_id=user_id,
            points=points,
            reason=reason,
            source=source,
            submission_id=submission_id,
            added_by=added_by,
        )
        session.add(log)

        # User total yangilash
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                total_points=User.total_points + points,
                last_activity=datetime.now()
            )
        )
        await session.commit()

        # Yangilangan userni qaytarish
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()

        # Badge tekshirish
        await check_and_update_badge(user_id, user.total_points)
        return user


async def check_and_update_badge(user_id: int, total_points: int) -> Optional[str]:
    new_badge = "none"
    for badge_code, info in sorted(BADGE_THRESHOLDS.items(), key=lambda x: x[1]["min"], reverse=True):
        if total_points >= info["min"]:
            new_badge = badge_code
            break

    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user and user.badge_level != new_badge:
            await session.execute(
                update(User).where(User.id == user_id).values(badge_level=new_badge)
            )
            await session.commit()
            return new_badge if new_badge != "none" else None
    return None


async def get_points_history(user_id: int, limit: int = 10) -> List[PointsLog]:
    async with async_session() as session:
        result = await session.execute(
            select(PointsLog)
            .where(PointsLog.user_id == user_id)
            .order_by(desc(PointsLog.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())


# ===== SUBMISSIONS =====

def make_hash(user_id: int, activity_code: str, proof_data: str) -> str:
    raw = f"{user_id}:{activity_code}:{proof_data}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def check_duplicate(hash_fp: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(Submission).where(Submission.hash_fingerprint == hash_fp)
        )
        return result.scalar_one_or_none() is not None


async def create_submission(
    user_id: int,
    activity_code: str,
    proof_type: str,
    proof_data: str,
    proof_description: Optional[str] = None,
) -> Optional[Submission]:
    hash_fp = make_hash(user_id, activity_code, proof_data)

    if await check_duplicate(hash_fp):
        return None  # Dublikat!

    async with async_session() as session:
        sub = Submission(
            user_id=user_id,
            activity_code=activity_code,
            proof_type=proof_type,
            proof_data=proof_data,
            proof_description=proof_description,
            hash_fingerprint=hash_fp,
        )
        session.add(sub)
        await session.commit()
        await session.refresh(sub)
        return sub


async def get_pending_submissions() -> List[Submission]:
    async with async_session() as session:
        result = await session.execute(
            select(Submission)
            .where(Submission.status == "pending")
            .order_by(Submission.submitted_at)
            .options(selectinload(Submission.user))
        )
        return list(result.scalars().all())


async def get_submission_by_id(sub_id: int) -> Optional[Submission]:
    async with async_session() as session:
        result = await session.execute(
            select(Submission)
            .where(Submission.id == sub_id)
            .options(selectinload(Submission.user))
        )
        return result.scalar_one_or_none()


async def approve_submission(sub_id: int, admin_id: int) -> Optional[Submission]:
    async with async_session() as session:
        result = await session.execute(
            select(Submission)
            .where(Submission.id == sub_id)
            .options(selectinload(Submission.user))
        )
        sub = result.scalar_one_or_none()
        if not sub or sub.status != "pending":
            return None

        points = ACTIVITIES[sub.activity_code]["points"]
        sub.status = "approved"
        sub.admin_id = admin_id
        sub.reviewed_at = datetime.now()
        sub.points_awarded = points
        await session.commit()

    # Ball qo'shish
    activity_name = ACTIVITIES[sub.activity_code]["name"]
    await add_points(
        user_id=sub.user_id,
        points=points,
        reason=f"{activity_name} uchun",
        source="submission",
        submission_id=sub_id,
        added_by=admin_id,
    )
    return sub


async def reject_submission(sub_id: int, admin_id: int, reason: str) -> Optional[Submission]:
    async with async_session() as session:
        result = await session.execute(
            select(Submission)
            .where(Submission.id == sub_id)
            .options(selectinload(Submission.user))
        )
        sub = result.scalar_one_or_none()
        if not sub or sub.status != "pending":
            return None

        sub.status = "rejected"
        sub.admin_id = admin_id
        sub.admin_note = reason
        sub.reviewed_at = datetime.now()
        await session.commit()
        return sub


# ===== ADMIN STATS =====

async def get_stats() -> dict:
    async with async_session() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar()
        total_subs = (await session.execute(select(func.count(Submission.id)))).scalar()
        pending_subs = (await session.execute(
            select(func.count(Submission.id)).where(Submission.status == "pending")
        )).scalar()
        approved_subs = (await session.execute(
            select(func.count(Submission.id)).where(Submission.status == "approved")
        )).scalar()
        total_points_given = (await session.execute(
            select(func.sum(PointsLog.points)).where(PointsLog.points > 0)
        )).scalar() or 0

        return {
            "total_users": total_users,
            "total_submissions": total_subs,
            "pending_submissions": pending_subs,
            "approved_submissions": approved_subs,
            "total_points_given": total_points_given,
        }


async def get_all_users(limit: int = 50) -> List[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).order_by(desc(User.total_points)).limit(limit)
        )
        return list(result.scalars().all())
