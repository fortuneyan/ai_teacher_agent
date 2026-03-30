-- AI教师Agent - 数据库初始化脚本
-- PostgreSQL 16+
-- 执行方式: psql -U postgres -d ai_teacher_agent -f init_db.sql

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    hashed_password VARCHAR(200) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'student',  -- teacher/student/admin/group_leader
    subject VARCHAR(50),  -- 任教学科（教师）
    grade VARCHAR(50),    -- 所在班级（学生）
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 教案表
CREATE TABLE IF NOT EXISTS lesson_plans (
    id SERIAL PRIMARY KEY,
    teacher_id INT REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    subject VARCHAR(50),
    level VARCHAR(20),    -- primary/middle/high/university
    grade VARCHAR(50),
    topic VARCHAR(200),
    duration INT DEFAULT 1,
    objectives TEXT,
    content TEXT,
    content_html TEXT,
    status VARCHAR(20) DEFAULT 'draft',  -- draft/completed/archived
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 频道表（UNLOGGED - 高性能，重启后数据可以从 channels 重建）
CREATE UNLOGGED TABLE IF NOT EXISTS channels (
    channel_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    teacher_id INT REFERENCES users(id),
    lesson_plan_id INT REFERENCES lesson_plans(id),
    invite_code VARCHAR(20) UNIQUE,
    max_students INT DEFAULT 50,
    status VARCHAR(20) DEFAULT 'active',  -- active/ended/archived
    current_page INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

-- 频道成员表（UNLOGGED）
CREATE UNLOGGED TABLE IF NOT EXISTS channel_members (
    id SERIAL PRIMARY KEY,
    channel_id VARCHAR(64) REFERENCES channels(channel_id),
    user_id INT REFERENCES users(id),
    role VARCHAR(20),
    joined_at TIMESTAMP DEFAULT NOW(),
    left_at TIMESTAMP,
    UNIQUE(channel_id, user_id)
);

-- 习题表
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    teacher_id INT REFERENCES users(id),
    title TEXT NOT NULL,
    content TEXT,
    type VARCHAR(30),     -- single_choice/multi_choice/fill_blank/judge/short_answer/calculation
    difficulty INT DEFAULT 2,  -- 1-4
    subject VARCHAR(50),
    grade VARCHAR(50),
    answer TEXT,
    analysis TEXT,
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 学生答题记录
CREATE TABLE IF NOT EXISTS student_answers (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES users(id),
    exercise_id INT REFERENCES exercises(id),
    channel_id VARCHAR(64),
    answer TEXT,
    score FLOAT,
    is_correct BOOLEAN,
    submitted_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_lesson_plans_teacher ON lesson_plans(teacher_id);
CREATE INDEX IF NOT EXISTS idx_lesson_plans_status ON lesson_plans(status);
CREATE INDEX IF NOT EXISTS idx_exercises_teacher ON exercises(teacher_id);
CREATE INDEX IF NOT EXISTS idx_student_answers_student ON student_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_channels_invite ON channels(invite_code) WHERE status = 'active';

-- 插入演示数据
-- 管理员账号（密码: admin123）
INSERT INTO users (username, email, hashed_password, full_name, role, is_active)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- admin123
    '系统管理员',
    'admin',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- 教师账号（密码: demo123）
INSERT INTO users (username, email, hashed_password, full_name, role, subject, is_active)
VALUES (
    'teacher01',
    'teacher01@example.com',
    '$2b$12$LowRSFNnVWuMm3fHDWVOUuORCGpfZ9ZHQ5bDxJOvhR.R1A3WJjnPu',  -- demo123
    '张老师',
    'teacher',
    'math',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- 学生账号（密码: demo123）
INSERT INTO users (username, email, hashed_password, full_name, role, grade, is_active)
VALUES (
    'student01',
    'student01@example.com',
    '$2b$12$LowRSFNnVWuMm3fHDWVOUuORCGpfZ9ZHQ5bDxJOvhR.R1A3WJjnPu',  -- demo123
    '王小明',
    'student',
    '高一3班',
    TRUE
) ON CONFLICT (username) DO NOTHING;
