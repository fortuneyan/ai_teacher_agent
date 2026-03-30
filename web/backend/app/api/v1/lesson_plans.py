"""
AI教师Agent Web后端 - 教案管理API
"""

import json
import sys
import time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import asyncpg
from typing import List, Optional

# 添加项目根目录到Python路径，以便导入Agent代码
import os

# 获取项目根目录 (web/backend/app/api/v1/lesson_plans.py 向上6级)
project_root = Path(__file__).resolve()
for _ in range(6):
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.database import get_db_dependency
from app.api.v1.auth import get_current_user_id
from app.schemas.schemas import (
    LessonPlanCreate,
    LessonPlanUpdate,
    LessonPlanResponse,
    LessonPlanListItem,
)

router = APIRouter(prefix="/lesson-plans", tags=["教案管理"], redirect_slashes=False)


@router.get("/", response_model=List[LessonPlanListItem], summary="获取教案列表")
async def list_lesson_plans(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """获取当前教师的教案列表，支持过滤"""
    query = """
        SELECT id, uuid, title, subject, grade, topic, status, ai_generated, created_at
        FROM lesson_plans
        WHERE teacher_id = $1
    """
    params = [current_user["user_id"]]
    param_idx = 2

    if subject:
        query += f" AND subject = ${param_idx}"
        params.append(subject)
        param_idx += 1

    if grade:
        query += f" AND grade = ${param_idx}"
        params.append(grade)
        param_idx += 1

    if status:
        query += f" AND status = ${param_idx}"
        params.append(status)
        param_idx += 1

    query += f" ORDER BY created_at DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
    params.extend([limit, offset])

    rows = await db.fetch(query, *params)

    return [
        LessonPlanListItem(
            id=row["id"],
            uuid=str(row["uuid"]),
            title=row["title"],
            subject=row["subject"],
            grade=row["grade"],
            topic=row["topic"],
            status=row["status"],
            ai_generated=row["ai_generated"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.post("/", summary="创建教案（AI辅助生成）")
async def create_lesson_plan(
    plan_data: LessonPlanCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """
    创建新教案，使用AI自动生成内容

    该接口会：
    1. 创建教案记录（状态为draft）
    2. 调用AI技能生成教案内容（Mock模式下返回示例数据）
    3. 返回完整的教案数据
    """
    start_time = time.time()

    # 调用AI技能生成教案（集成现有Agent技能代码）
    lesson_plan_content = await _generate_lesson_plan_with_ai(plan_data)

    generation_time = time.time() - start_time

    # 保存到数据库
    row = await db.fetchrow(
        """
        INSERT INTO lesson_plans (
            teacher_id, title, subject, grade, topic, version, duration,
            objectives, content, key_points, teaching_flow, resources,
            ai_generated, generation_time, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 'draft')
        RETURNING *
        """,
        current_user["user_id"],
        lesson_plan_content["title"],
        plan_data.subject,
        plan_data.grade,
        plan_data.topic,
        plan_data.version,
        plan_data.duration,
        json.dumps(lesson_plan_content.get("objectives", {}), ensure_ascii=False),
        lesson_plan_content.get("content", ""),
        lesson_plan_content.get("key_points", ""),
        json.dumps(lesson_plan_content.get("teaching_flow", []), ensure_ascii=False),
        json.dumps(lesson_plan_content.get("resources", []), ensure_ascii=False),
        True,
        generation_time,
    )

    return {
        "id": row["id"],
        "uuid": str(row["uuid"]),
        "title": row["title"],
        "subject": plan_data.subject,
        "grade": plan_data.grade,
        "topic": plan_data.topic,
        "status": "draft",
        "content": lesson_plan_content.get("content"),
        "teaching_flow": lesson_plan_content.get("teaching_flow"),
        "ai_generated": True,
        "generation_time": round(generation_time, 2),
        "created_at": row["created_at"].isoformat(),
    }


@router.get("/{plan_id}", response_model=LessonPlanResponse, summary="获取教案详情")
async def get_lesson_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """获取教案详情"""
    row = await db.fetchrow(
        "SELECT * FROM lesson_plans WHERE id = $1 AND teacher_id = $2",
        plan_id,
        current_user["user_id"],
    )

    if not row:
        raise HTTPException(status_code=404, detail="教案不存在或无权访问")

    return LessonPlanResponse(
        id=row["id"],
        uuid=str(row["uuid"]),
        title=row["title"],
        subject=row["subject"],
        grade=row["grade"],
        topic=row["topic"],
        status=row["status"],
        content=row["content"],
        teaching_flow=json.loads(row["teaching_flow"])
        if row["teaching_flow"]
        else None,
        ai_generated=row["ai_generated"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.put("/{plan_id}", summary="更新教案")
async def update_lesson_plan(
    plan_id: int,
    update_data: LessonPlanUpdate,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """更新教案内容"""
    # 检查权限
    existing = await db.fetchrow(
        "SELECT id FROM lesson_plans WHERE id = $1 AND teacher_id = $2",
        plan_id,
        current_user["user_id"],
    )
    if not existing:
        raise HTTPException(status_code=404, detail="教案不存在或无权访问")

    # 构建更新语句
    updates = {}
    if update_data.title is not None:
        updates["title"] = update_data.title
    if update_data.content is not None:
        updates["content"] = update_data.content
    if update_data.key_points is not None:
        updates["key_points"] = update_data.key_points
    if update_data.teaching_flow is not None:
        updates["teaching_flow"] = json.dumps(
            update_data.teaching_flow, ensure_ascii=False
        )

    if not updates:
        return {"message": "无需更新"}

    set_clauses = ", ".join(f"{k} = ${i + 2}" for i, k in enumerate(updates.keys()))
    await db.execute(
        f"UPDATE lesson_plans SET {set_clauses}, updated_at = NOW() WHERE id = $1",
        plan_id,
        *updates.values(),
    )

    return {"message": "更新成功", "id": plan_id}


@router.post("/{plan_id}/submit", summary="提交教案审核")
async def submit_lesson_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """提交教案给教研组长审核"""
    result = await db.execute(
        """
        UPDATE lesson_plans SET status = 'submitted', updated_at = NOW()
        WHERE id = $1 AND teacher_id = $2 AND status = 'draft'
        """,
        plan_id,
        current_user["user_id"],
    )

    if result == "UPDATE 0":
        raise HTTPException(
            status_code=400, detail="教案不存在、无权访问或状态不允许提交"
        )

    return {"message": "教案已提交审核", "id": plan_id}


@router.delete("/{plan_id}", summary="删除教案")
async def delete_lesson_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """删除指定教案"""
    result = await db.execute(
        """
        DELETE FROM lesson_plans 
        WHERE id = $1 AND teacher_id = $2
        """,
        plan_id,
        current_user["user_id"],
    )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="教案不存在或无权删除")

    return {"message": "教案已删除", "id": plan_id}


@router.get("/{plan_id}/export", summary="导出教案")
async def export_lesson_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user_id),
    db: asyncpg.Connection = Depends(get_db_dependency),
):
    """导出教案为指定格式（暂不支持，返回JSON）"""
    plan = await db.fetchrow(
        """
        SELECT id, uuid, title, subject, grade, topic, content, teaching_flow
        FROM lesson_plans 
        WHERE id = $1 AND teacher_id = $2
        """,
        plan_id,
        current_user["user_id"],
    )

    if not plan:
        raise HTTPException(status_code=404, detail="教案不存在或无权访问")

    return {
        "id": plan["id"],
        "uuid": str(plan["uuid"]),
        "title": plan["title"],
        "subject": plan["subject"],
        "grade": plan["grade"],
        "topic": plan["topic"],
        "content": plan["content"],
        "teaching_flow": plan["teaching_flow"],
    }


async def _generate_lesson_plan_with_ai(plan_data: LessonPlanCreate) -> dict:
    """
    调用真实LLM生成教案内容
    """
    import logging
    import time
    from app.core.llm import get_llm_service
    import json

    logger = logging.getLogger(__name__)
    print(f"========== LLM Request Start ==========")
    print(f"plan_data: {json.dumps(plan_data.model_dump(), ensure_ascii=False)}")
    start_time = time.time()

    # 从 grade 推断学段
    education_level = "高中"
    if plan_data.grade:
        if (
            "高一" in plan_data.grade
            or "高二" in plan_data.grade
            or "高三" in plan_data.grade
        ):
            education_level = "高中"
        elif (
            "初一" in plan_data.grade
            or "初二" in plan_data.grade
            or "初三" in plan_data.grade
        ):
            education_level = "初中"
        else:
            education_level = "小学"

    # 准备发送到LLM的数据
    llm_request_data = {
        "subject": plan_data.subject,
        "topic": plan_data.topic,
        "grade": plan_data.grade,
        "education_level": education_level,
        "duration": plan_data.duration or 1,
    }

    logger.info(f"========== LLM Request ==========")
    logger.info(
        f"请求数据: {json.dumps(llm_request_data, ensure_ascii=False, indent=2)}"
    )

    # 调用LLM服务生成教案
    llm = get_llm_service()
    result = await llm.generate_lesson_plan(**llm_request_data)

    content = result["content"]
    topic = plan_data.topic
    generation_time = time.time() - start_time

    logger.info(f"========== LLM Response ==========")
    logger.info(f"返回数据长度: {len(content)} 字符")
    logger.info(f"返回内容预览:\n{content[:500]}...")
    logger.info(f"==================================")

    # 提取教学目标（简单解析）
    objectives = _extract_objectives(content)

    # 提取教学流程（简单解析）
    teaching_flow = _extract_teaching_flow(content)

    return {
        "title": f"{education_level}{plan_data.subject}《{topic}》教学设计",
        "objectives": objectives,
        "key_points": f"**重点**: {topic}的概念和性质\n**难点**: {topic}的应用",
        "content": content,
        "teaching_flow": teaching_flow,
        "resources": [
            {"type": "ppt", "name": f"{topic}课件", "url": ""},
            {"type": "video", "name": f"{topic}讲解视频", "url": ""},
            {"type": "exercise", "name": f"{topic}练习题", "url": ""},
        ],
        "generation_time": round(generation_time, 2),
    }


def _extract_objectives(content: str) -> dict:
    """从生成内容中提取教学目标"""
    knowledge = []
    skill = []
    emotion = []

    lines = content.split("\n")
    current_type = None

    for line in lines:
        line = line.strip()
        if "知识与技能" in line or "知识目标" in line:
            current_type = "knowledge"
        elif "过程与方法" in line or "能力目标" in line:
            current_type = "skill"
        elif "情感态度" in line or "情感目标" in line:
            current_type = "emotion"
        elif line.startswith("- ") and current_type:
            obj = line[2:].strip()
            if current_type == "knowledge":
                knowledge.append(obj)
            elif current_type == "skill":
                skill.append(obj)
            elif current_type == "emotion":
                emotion.append(obj)

    # 如果没有提取到，使用默认值
    if not knowledge:
        knowledge = ["理解本节课的基本概念", "掌握相关核心原理"]
    if not skill:
        skill = ["培养分析问题能力", "提升解决问题能力"]
    if not emotion:
        emotion = ["激发学习兴趣", "培养科学态度"]

    return {"knowledge": knowledge, "skill": skill, "emotion": emotion}


def _extract_teaching_flow(content: str) -> list:
    """从生成内容中提取教学流程"""
    teaching_flow = []

    # 常见教学环节
    phases = ["导入", "新授", "讲授", "练习", "小结", "总结", "作业"]
    current_phase = None
    current_activity = ""

    lines = content.split("\n")
    for line in lines:
        line = line.strip()

        # 检测阶段
        for phase in phases:
            if phase in line and ("（" in line or len(line) < 10):
                if current_phase:
                    teaching_flow.append(
                        {
                            "stage": current_phase,
                            "duration": 5,
                            "activity": current_activity,
                            "method": "讲授/探究",
                            "teacher_action": current_activity,
                            "student_action": "听讲、思考",
                        }
                    )
                current_phase = phase
                current_activity = line
                break

    # 添加最后一个阶段
    if current_phase:
        teaching_flow.append(
            {
                "stage": current_phase,
                "duration": 5,
                "activity": current_activity,
                "method": "讲授/探究",
                "teacher_action": current_activity,
                "student_action": "听讲、思考",
            }
        )

    # 如果没有提取到，使用默认流程
    if not teaching_flow:
        teaching_flow = [
            {
                "stage": "导入",
                "duration": 5,
                "activity": "创设情境",
                "method": "导入",
                "teacher_action": "提出问题",
                "student_action": "思考回答",
            },
            {
                "stage": "新授",
                "duration": 20,
                "activity": "讲解概念",
                "method": "讲授",
                "teacher_action": "讲解",
                "student_action": "听讲",
            },
            {
                "stage": "练习",
                "duration": 10,
                "activity": "课堂练习",
                "method": "练习",
                "teacher_action": "巡视指导",
                "student_action": "完成练习",
            },
            {
                "stage": "小结",
                "duration": 5,
                "activity": "总结",
                "method": "讲授",
                "teacher_action": "总结",
                "student_action": "记录",
            },
        ]

    return teaching_flow
