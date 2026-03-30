"""
AI教师Agent Web后端 - 频道（课堂）API
"""

import uuid
import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
from typing import List

from app.core.database import get_db_dependency
from app.core.security import decode_access_token
from app.api.v1.auth import get_current_user_id

router = APIRouter(prefix="/channels", tags=["频道"], redirect_slashes=False)
security = HTTPBearer()


def generate_invite_code(length=6) -> str:
    """生成随机邀请码"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("", summary="创建授课频道")
async def create_channel(
    data: dict,
    db: asyncpg.Connection = Depends(get_db_dependency),
    current_user: dict = Depends(get_current_user_id),
):
    """教师创建授课频道"""
    if current_user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="只有教师可以创建频道")

    channel_id = str(uuid.uuid4())
    invite_code = generate_invite_code()

    # 确保邀请码唯一
    while await db.fetchrow(
        "SELECT 1 FROM channels WHERE invite_code = $1 AND status = 'active'",
        invite_code,
    ):
        invite_code = generate_invite_code()

    channel = await db.fetchrow(
        """
        INSERT INTO channels (channel_id, title, teacher_id, lesson_plan_id, invite_code, max_students, status)
        VALUES ($1, $2, $3, $4, $5, $6, 'active')
        RETURNING *
        """,
        channel_id,
        data.get("title", "未命名课堂"),
        current_user["user_id"],
        data.get("lessonPlanId"),
        invite_code,
        data.get("maxStudents", 50),
    )

    return {
        "channel_id": channel["channel_id"],
        "title": channel["title"],
        "invite_code": channel["invite_code"],
        "status": channel["status"],
        "created_at": channel["created_at"].isoformat()
        if channel["created_at"]
        else None,
    }


@router.get("/{channel_id}", summary="获取频道信息")
async def get_channel(
    channel_id: str,
    db: asyncpg.Connection = Depends(get_db_dependency),
    current_user: dict = Depends(get_current_user_id),
):
    """获取频道详情"""
    channel = await db.fetchrow(
        "SELECT * FROM channels WHERE channel_id = $1", channel_id
    )
    if not channel:
        raise HTTPException(status_code=404, detail="频道不存在")
    return dict(channel)


@router.post("/{channel_id}/join", summary="学生加入频道")
async def join_channel(
    channel_id: str,
    data: dict,
    db: asyncpg.Connection = Depends(get_db_dependency),
    current_user: dict = Depends(get_current_user_id),
):
    """学生通过邀请码加入频道"""
    invite_code = data.get("invite_code", "")

    # 通过邀请码查找频道
    channel = await db.fetchrow(
        "SELECT * FROM channels WHERE invite_code = $1 AND status = 'active'",
        invite_code,
    )
    if not channel:
        raise HTTPException(status_code=404, detail="邀请码无效或课堂已结束")

    return {
        "channel_id": channel["channel_id"],
        "title": channel["title"],
        "invite_code": channel["invite_code"],
        "status": channel["status"],
    }


@router.post("/{channel_id}/end", summary="结束授课")
async def end_channel(
    channel_id: str,
    db: asyncpg.Connection = Depends(get_db_dependency),
    current_user: dict = Depends(get_current_user_id),
):
    """教师结束授课，关闭频道"""
    channel = await db.fetchrow(
        "SELECT * FROM channels WHERE channel_id = $1", channel_id
    )
    if not channel:
        raise HTTPException(status_code=404, detail="频道不存在")

    if channel["teacher_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="只有授课教师可以结束课堂")

    await db.execute(
        "UPDATE channels SET status = 'ended', ended_at = NOW() WHERE channel_id = $1",
        channel_id,
    )

    return {"message": "课堂已结束"}
