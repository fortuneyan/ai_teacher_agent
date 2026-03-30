"""
AI教师Agent Web后端 - 认证相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
)
import asyncpg
from datetime import timedelta

from app.core.database import get_db_dependency
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings
from app.schemas.schemas import UserCreate, UserLogin, Token, UserResponse, UserRole

router = APIRouter(prefix="/auth", tags=["认证"], redirect_slashes=False)
security = HTTPBearer()


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """
    用户登录，返回JWT令牌和用户信息

    - **username**: 用户名
    - **password**: 密码
    """
    # 查询用户
    user = await db.fetchrow(
        "SELECT * FROM users WHERE username = $1 AND is_active = TRUE",
        form_data.username,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # 生成令牌
    token = create_access_token(
        data={"sub": str(user["id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            uuid=str(user["uuid"]),
            username=user["username"],
            full_name=user["full_name"],
            role=UserRole(user["role"]),
            email=user["email"],
            subject=user["subject"],
            grade=user["grade"],
            is_active=user["is_active"],
            created_at=user["created_at"],
        ),
    )


@router.post("/register", response_model=UserResponse, summary="注册用户")
async def register(
    user_data: UserCreate, db: asyncpg.Connection = Depends(get_db_dependency)
):
    """注册新用户（管理员操作或演示模式）"""
    # 检查用户名是否已存在
    existing = await db.fetchrow(
        "SELECT id FROM users WHERE username = $1", user_data.username
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    # 创建用户
    user = await db.fetchrow(
        """
        INSERT INTO users (username, email, hashed_password, full_name, role, subject, grade)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """,
        user_data.username,
        user_data.email,
        get_password_hash(user_data.password),
        user_data.full_name,
        user_data.role.value,
        user_data.subject,
        user_data.grade,
    )

    return UserResponse(
        id=user["id"],
        uuid=str(user["uuid"]),
        username=user["username"],
        full_name=user["full_name"],
        role=UserRole(user["role"]),
        email=user["email"],
        subject=user["subject"],
        grade=user["grade"],
        is_active=user["is_active"],
        created_at=user["created_at"],
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """获取当前登录用户的信息"""
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌"
        )

    user_id = int(payload.get("sub"))
    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1 AND is_active = TRUE", user_id
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return UserResponse(
        id=user["id"],
        uuid=str(user["uuid"]),
        username=user["username"],
        full_name=user["full_name"],
        role=UserRole(user["role"]),
        email=user["email"],
        subject=user["subject"],
        grade=user["grade"],
        is_active=user["is_active"],
        created_at=user["created_at"],
    )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """依赖注入：获取当前用户ID和角色"""
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌"
        )
    return {"user_id": int(payload.get("sub")), "role": payload.get("role")}
