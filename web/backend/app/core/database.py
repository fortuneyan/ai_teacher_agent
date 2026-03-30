"""
AI教师Agent Web后端 - 数据库连接管理 (PostgreSQL单库方案)
"""
import asyncpg
import psycopg2
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from app.core.config import settings


# 全局连接池（asyncpg，用于异步API）
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """获取或创建异步连接池"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )
    return _pool


async def close_pool():
    """关闭连接池"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """获取数据库连接（async context manager）"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def get_db_dependency():
    """FastAPI依赖注入 - 数据库连接"""
    async with get_db() as conn:
        yield conn


async def init_database():
    """初始化数据库 - 创建所有表"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # 执行数据库初始化SQL
        await conn.execute(_INIT_SQL)
        print("✅ 数据库初始化完成")


# ============================================================
# 数据库初始化SQL（基于数据持久化方案设计）
# ============================================================

_INIT_SQL = """
-- =====================================================
-- AI教师Agent - PostgreSQL单库方案 (v1.0)
-- 对应文档：数据持久化方案设计_PostgreSQL.md
-- =====================================================

-- 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================
-- 1. 用户表
-- ===========================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    uuid            UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(200) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            VARCHAR(20) NOT NULL CHECK (role IN ('teacher', 'student', 'admin', 'parent')),
    subject         VARCHAR(50),           -- 教师学科（如：数学、语文）
    grade           VARCHAR(50),           -- 教师年级（如：高中、初中）
    student_number  VARCHAR(50),           -- 学生学号
    class_name      VARCHAR(50),           -- 班级（教师/学生）
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ===========================
-- 2. 教案表（JSONB存储灵活内容）
-- ===========================
CREATE TABLE IF NOT EXISTS lesson_plans (
    id              SERIAL PRIMARY KEY,
    uuid            UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    title           VARCHAR(200) NOT NULL,
    teacher_id      INTEGER REFERENCES users(id),
    subject         VARCHAR(50),
    grade           VARCHAR(50),
    topic           VARCHAR(200),
    version         VARCHAR(100),          -- 教材版本（如：人教版2025）
    duration        INTEGER,               -- 课时（分钟）
    status          VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),

    -- 教案内容（JSONB存储灵活结构）
    objectives      JSONB,                 -- 教学目标 {knowledge: [], skill: [], emotion: []}
    content         TEXT,                  -- 教案正文（富文本HTML）
    key_points      TEXT,                  -- 重难点
    teaching_flow   JSONB,                 -- 教学流程 [{stage, duration, activity, method}]
    resources       JSONB,                 -- 教学资源 [{type, name, url}]

    -- AI生成元数据
    ai_generated    BOOLEAN DEFAULT FALSE,
    ai_model        VARCHAR(50),
    generation_time FLOAT,                 -- 生成耗时(秒)

    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lesson_plans_teacher ON lesson_plans(teacher_id);
CREATE INDEX IF NOT EXISTS idx_lesson_plans_subject ON lesson_plans(subject);
CREATE INDEX IF NOT EXISTS idx_lesson_plans_status ON lesson_plans(status);
CREATE INDEX IF NOT EXISTS idx_lesson_plans_content ON lesson_plans USING GIN (teaching_flow);

-- ===========================
-- 3. 课件大纲表
-- ===========================
CREATE TABLE IF NOT EXISTS coursewares (
    id              SERIAL PRIMARY KEY,
    uuid            UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    lesson_plan_id  INTEGER REFERENCES lesson_plans(id),
    teacher_id      INTEGER REFERENCES users(id),
    title           VARCHAR(200),
    slides          JSONB,                 -- 幻灯片大纲列表 [{title, content, notes, order}]
    total_slides    INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coursewares_lesson ON coursewares(lesson_plan_id);

-- ===========================
-- 4. 习题表
-- ===========================
CREATE TABLE IF NOT EXISTS exercises (
    id              SERIAL PRIMARY KEY,
    uuid            UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    teacher_id      INTEGER REFERENCES users(id),
    subject         VARCHAR(50),
    grade           VARCHAR(50),
    topic           VARCHAR(200),
    type            VARCHAR(20) CHECK (type IN ('single', 'multiple', 'fill', 'judge', 'short', 'calc', 'proof', 'apply', 'comprehensive')),
    difficulty      VARCHAR(10) CHECK (difficulty IN ('easy', 'medium', 'hard', 'challenge')),
    content         TEXT NOT NULL,         -- 题目内容
    options         JSONB,                 -- 选项（选择题用）[{key, content}]
    answer          TEXT,                  -- 正确答案
    explanation     TEXT,                  -- 解析
    steps           JSONB,                 -- 解题步骤 [{order, content}]
    knowledge_points JSONB,               -- 知识点标签 ["函数概念", "定义域"]
    ai_generated    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exercises_subject ON exercises(subject);
CREATE INDEX IF NOT EXISTS idx_exercises_type ON exercises(type);
CREATE INDEX IF NOT EXISTS idx_exercises_kp ON exercises USING GIN (knowledge_points);

-- ===========================
-- 5. 试卷表
-- ===========================
CREATE TABLE IF NOT EXISTS test_papers (
    id              SERIAL PRIMARY KEY,
    uuid            UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    teacher_id      INTEGER REFERENCES users(id),
    title           VARCHAR(200),
    subject         VARCHAR(50),
    grade           VARCHAR(50),
    type            VARCHAR(20),           -- 试卷类型
    duration        INTEGER,               -- 考试时长（分钟）
    total_score     INTEGER,               -- 总分
    structure       JSONB,                 -- 试卷结构 [{section_name, exercises: [{id, score}]}]
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_test_papers_teacher ON test_papers(teacher_id);

-- ===========================
-- 6. 频道表（UNLOGGED，高速读写）
-- ===========================
CREATE UNLOGGED TABLE IF NOT EXISTS channels (
    id              SERIAL PRIMARY KEY,
    channel_code    VARCHAR(20) UNIQUE NOT NULL,  -- 房间码（学生加入用）
    teacher_id      INTEGER REFERENCES users(id),
    lesson_plan_id  INTEGER REFERENCES lesson_plans(id),
    name            VARCHAR(200),
    status          VARCHAR(20) DEFAULT 'waiting' CHECK (status IN ('waiting', 'teaching', 'ended')),
    current_page    INTEGER DEFAULT 1,
    student_count   INTEGER DEFAULT 0,
    started_at      TIMESTAMP,
    ended_at        TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_channels_code ON channels(channel_code);
CREATE INDEX IF NOT EXISTS idx_channels_teacher ON channels(teacher_id);
CREATE INDEX IF NOT EXISTS idx_channels_status ON channels(status);

-- ===========================
-- 7. 频道成员表（UNLOGGED）
-- ===========================
CREATE UNLOGGED TABLE IF NOT EXISTS channel_members (
    channel_id      INTEGER,
    user_id         INTEGER,
    role            VARCHAR(20),           -- teacher/student
    joined_at       TIMESTAMP DEFAULT NOW(),
    is_online       BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (channel_id, user_id)
);

-- ===========================
-- 8. 频道状态表（UNLOGGED，实时同步）
-- ===========================
CREATE UNLOGGED TABLE IF NOT EXISTS channel_state (
    channel_id      INTEGER PRIMARY KEY,
    current_page    INTEGER DEFAULT 1,
    annotations     JSONB DEFAULT '[]',    -- 画板标注
    quiz_active     BOOLEAN DEFAULT FALSE,
    quiz_question_id INTEGER,
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_channel_state_annotations ON channel_state USING GIN (annotations);

-- ===========================
-- 9. 随堂测试答案表（UNLOGGED，快速写入）
-- ===========================
CREATE UNLOGGED TABLE IF NOT EXISTS quiz_answers (
    channel_id      INTEGER,
    student_id      INTEGER,
    exercise_id     INTEGER,
    answer          TEXT,
    is_correct      BOOLEAN,
    submitted_at    TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (channel_id, student_id, exercise_id)
);

-- ===========================
-- 10. 随堂测试统计表（UNLOGGED）
-- ===========================
CREATE UNLOGGED TABLE IF NOT EXISTS quiz_stats (
    channel_id          INTEGER,
    exercise_id         INTEGER,
    total_students      INTEGER DEFAULT 0,
    submitted_count     INTEGER DEFAULT 0,
    correct_count       INTEGER DEFAULT 0,
    option_counts       JSONB DEFAULT '{}', -- {"A": 10, "B": 5, ...}
    updated_at          TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (channel_id, exercise_id)
);

-- ===========================
-- 11. 学生答题记录表（持久化）
-- ===========================
CREATE TABLE IF NOT EXISTS student_answers (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER REFERENCES users(id),
    exercise_id     INTEGER REFERENCES exercises(id),
    test_paper_id   INTEGER REFERENCES test_papers(id),
    channel_id      INTEGER,               -- 关联频道（随堂测试为非空）
    answer          TEXT,
    is_correct      BOOLEAN,
    score           FLOAT DEFAULT 0,
    time_spent      INTEGER,               -- 答题时长（秒）
    submitted_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_student_answers_student ON student_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_student_answers_exercise ON student_answers(exercise_id);

-- ===========================
-- 12. 学情分析表（JSONB灵活存储）
-- ===========================
CREATE TABLE IF NOT EXISTS student_learning_records (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER REFERENCES users(id),
    subject             VARCHAR(50),
    knowledge_mastery   JSONB DEFAULT '{}', -- {"函数概念": 0.8, "单调性": 0.6}
    difficulty_stats    JSONB DEFAULT '{}', -- {"easy": {correct: 5, total: 5}, ...}
    weekly_progress     JSONB DEFAULT '[]', -- [{week, avg_score, exercises_done}]
    last_updated        TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_slr_student ON student_learning_records(student_id);
CREATE INDEX IF NOT EXISTS idx_slr_mastery ON student_learning_records USING GIN (knowledge_mastery);

-- ===========================
-- 13. 异步任务队列表（SKIP LOCKED）
-- ===========================
CREATE TABLE IF NOT EXISTS job_queue (
    id              SERIAL PRIMARY KEY,
    job_type        VARCHAR(50),           -- 'generate_lesson_plan', 'analyze_answers', etc.
    payload         JSONB,                 -- 任务参数
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'done', 'failed')),
    result          JSONB,
    error           TEXT,
    created_at      TIMESTAMP DEFAULT NOW(),
    processed_at    TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status, created_at);

-- ===========================
-- LISTEN/NOTIFY 触发器（实时推送）
-- 当channel_state更新时，自动发送通知
-- ===========================
CREATE OR REPLACE FUNCTION notify_channel_update()
RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'channel_' || NEW.channel_id::text,
        json_build_object(
            'type', 'state_update',
            'channel_id', NEW.channel_id,
            'current_page', NEW.current_page,
            'quiz_active', NEW.quiz_active
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_channel_state_notify ON channel_state;
CREATE TRIGGER trigger_channel_state_notify
    AFTER INSERT OR UPDATE ON channel_state
    FOR EACH ROW EXECUTE FUNCTION notify_channel_update();

-- ===========================
-- 索引分析视图
-- ===========================
CREATE OR REPLACE VIEW v_channel_summary AS
SELECT
    c.id,
    c.channel_code,
    c.name,
    c.status,
    c.current_page,
    c.student_count,
    c.created_at,
    u.full_name AS teacher_name,
    lp.title AS lesson_title
FROM channels c
LEFT JOIN users u ON c.teacher_id = u.id
LEFT JOIN lesson_plans lp ON c.lesson_plan_id = lp.id;

COMMENT ON TABLE channels IS 'UNLOGGED表 - 频道状态，不持久化到WAL，速度快，崩溃恢复时清空';
COMMENT ON TABLE channel_members IS 'UNLOGGED表 - 频道成员实时状态';
COMMENT ON TABLE channel_state IS 'UNLOGGED表 - 频道课件状态，实时同步';
COMMENT ON TABLE quiz_answers IS 'UNLOGGED表 - 随堂测试临时答案，归档后持久化到student_answers';
COMMENT ON TABLE quiz_stats IS 'UNLOGGED表 - 随堂测试实时统计';
"""
