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
    调用 skills/lesson_preparation 中的 LessonPreparationAssistant 生成教案内容。

    流程：
    1. 构建 LessonPreparationAssistant，注入真实 LLM 服务
    2. 调用 assistant.prepare_lesson() — 内部会完成：
       获取课程标准 → 搜索资源 → ContentGenerator.generate_lesson_plan()（调用 LLM）→ 生成课件
    3. 将返回的结构化教案转换为 Web 接口需要的格式
    """
    import logging
    import time

    logger = logging.getLogger(__name__)

    # ── 学科英文到中文映射 ──────────────────────────────────────────────────────
    subject_map = {
        "math": "数学", "chinese": "语文", "english": "英语",
        "physics": "物理", "chemistry": "化学", "biology": "生物",
        "history": "历史", "geography": "地理", "politics": "政治",
        "music": "音乐", "art": "美术", "pe": "体育",
    }
    subject_cn = subject_map.get(plan_data.subject, plan_data.subject)

    # ── 从 grade 推断学段 ──────────────────────────────────────────────────────
    education_level = "高中"
    if plan_data.grade:
        if any(k in plan_data.grade for k in ("高一", "高二", "高三")):
            education_level = "高中"
        elif any(k in plan_data.grade for k in ("初一", "初二", "初三")):
            education_level = "初中"
        elif any(k in plan_data.grade for k in ("大一", "大二", "大三", "大四")):
            education_level = "大学"
        elif any(k in plan_data.grade for k in ("一年级", "二年级", "三年级", "四年级", "五年级", "六年级")):
            education_level = "小学"

    # ── 构造课程名称（用于查询课程标准）─────────────────────────────────────────
    # STANDARDS_DB 的键格式是 "高中数学"、"初中数学" 等
    course_name = f"{education_level}{subject_cn}"
    topic = plan_data.topic

    print(f"========== LessonPreparationAssistant Start ==========")
    print(f"course_name={course_name}, topic={topic}, grade={plan_data.grade}")

    start_time = time.time()

    # ── 获取 LLM 服务，注入到备课助手 ──────────────────────────────────────────
    from app.core.llm import get_llm_service
    from skills.lesson_preparation import LessonPreparationAssistant

    llm_service = get_llm_service()
    assistant = LessonPreparationAssistant(llm_service=llm_service)

    # ── 调用核心 generate_lesson_plan 流程 ─────────────────────────────────────
    result = await assistant.prepare_lesson(
        course_name=course_name,
        topic=topic,
        education_level=education_level,
    )

    generation_time = time.time() - start_time

    # ── 从结构化教案提取数据 ───────────────────────────────────────────────────
    lesson_plan_dict = result.get("lesson_plan", {})
    teaching_process = lesson_plan_dict.get("teaching_process", [])

    # 教学目标
    objectives = {
        "knowledge": lesson_plan_dict.get("knowledge_objectives", []),
        "skill":     lesson_plan_dict.get("ability_objectives", []),
        "emotion":   lesson_plan_dict.get("emotion_objectives", []),
    }

    # 教学重难点
    key_points_list = lesson_plan_dict.get("key_points", [])
    difficult_points_list = lesson_plan_dict.get("difficult_points", [])
    key_points_str = (
        f"**重点**: {'、'.join(key_points_list)}\n**难点**: {'、'.join(difficult_points_list)}"
        if key_points_list or difficult_points_list
        else f"**重点**: {topic}的概念和性质\n**难点**: {topic}的应用"
    )

    # 教学流程 — 统一转为 Web 接口格式
    teaching_flow = [
        {
            "stage":          step.get("stage", ""),
            "duration":       step.get("duration", 5),
            "activity":       "、".join(step.get("activities", [])) if isinstance(step.get("activities"), list) else step.get("activities", ""),
            "method":         step.get("methods", "讲授/探究"),
            "teacher_action": "、".join(step.get("activities", [])) if isinstance(step.get("activities"), list) else step.get("activities", ""),
            "student_action": "听讲、思考",
        }
        for step in teaching_process
    ]

    # 生成 Markdown 格式正文（复用 assistant 的格式化方法）
    from dataclasses import fields as dc_fields
    from skills.lesson_preparation import LessonPlan as SkillLessonPlan

    try:
        lp_obj = SkillLessonPlan(**{
            k: lesson_plan_dict[k]
            for k in (f.name for f in dc_fields(SkillLessonPlan))
            if k in lesson_plan_dict
        })
        content = assistant.format_lesson_plan_for_display(lp_obj)
    except Exception:
        # 降级：把整个 lesson_plan_dict 序列化为可读文本
        content = json.dumps(lesson_plan_dict, ensure_ascii=False, indent=2)

    # 教学资源
    resources_needed = lesson_plan_dict.get("resources_needed", [])
    resources = [{"type": "other", "name": r, "url": ""} for r in resources_needed] or [
        {"type": "ppt",      "name": f"{topic}课件",     "url": ""},
        {"type": "video",    "name": f"{topic}讲解视频", "url": ""},
        {"type": "exercise", "name": f"{topic}练习题",   "url": ""},
    ]

    logger.info(f"========== LessonPreparationAssistant Done ==========")
    logger.info(f"content length={len(content)}, generation_time={generation_time:.2f}s")

    return {
        "title":         f"{course_name}《{topic}》教学设计",
        "objectives":    objectives,
        "key_points":    key_points_str,
        "content":       content,
        "teaching_flow": teaching_flow,
        "resources":     resources,
        "generation_time": round(generation_time, 2),
    }



