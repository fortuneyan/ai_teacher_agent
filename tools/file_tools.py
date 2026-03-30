"""
文件操作工具集
对应第4章 - Function Calling
用于创建和管理Markdown、JSON文件
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class FileTool:
    """文件操作工具类"""

    def __init__(
        self,
        base_dir: str = "./knowledge_base",
        output_dir: str = "./output",
        course_name: str = "",
        textbook_name: str = "",
    ):
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.course_name = course_name
        self.textbook_name = textbook_name

        # 确保目录存在
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

    def _get_output_path(self, subdir: str = None) -> str:
        """获取输出路径，支持按课程名称和教材名称分目录"""
        if self.course_name and self.textbook_name:
            base = os.path.join(self.output_dir, self.course_name, self.textbook_name)
        elif self.course_name:
            base = os.path.join(self.output_dir, self.course_name)
        else:
            base = self.output_dir

        if subdir:
            base = os.path.join(base, subdir)

        os.makedirs(base, exist_ok=True)
        return base

    def save_markdown(self, content: str, filename: str, subdir: str = None) -> str:
        """
        保存Markdown文件

        Args:
            content: Markdown内容
            filename: 文件名
            subdir: 子目录

        Returns:
            保存的文件路径
        """
        dir_path = self._get_output_path(subdir)
        file_path = os.path.join(dir_path, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def save_json(self, data: Dict[str, Any], filename: str, subdir: str = None) -> str:
        """
        保存JSON文件

        Args:
            data: 要保存的字典数据
            filename: 文件名
            subdir: 子目录

        Returns:
            保存的文件路径
        """
        dir_path = self._get_output_path(subdir)
        file_path = os.path.join(dir_path, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return file_path

    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_files(self, directory: str = None, extension: str = None) -> List[str]:
        """
        列出目录下的文件

        Args:
            directory: 目录路径
            extension: 文件扩展名过滤

        Returns:
            文件列表
        """
        if directory is None:
            directory = self.base_dir

        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if extension is None or filename.endswith(extension):
                    files.append(os.path.join(root, filename))

        return files

    def file_exists(self, filename: str, directory: str = None) -> bool:
        """检查文件是否存在"""
        if directory is None:
            directory = self.output_dir

        file_path = os.path.join(directory, filename)
        return os.path.exists(file_path)

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        if not os.path.exists(file_path):
            return {"exists": False}

        stat = os.stat(file_path)
        return {
            "exists": True,
            "path": file_path,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }


class MarkdownGenerator:
    """Markdown文档生成器"""

    @staticmethod
    def generate_lesson_plan(
        course_name: str, course_info: Dict[str, Any], content: Dict[str, Any]
    ) -> str:
        """
        生成教案Markdown

        Args:
            course_name: 课程名称
            course_info: 课程基本信息
            content: 教案内容

        Returns:
            Markdown格式的教案
        """
        md = f"""# {course_name} 教案

## 课程基本信息

- **课程名称**: {course_name}
- **课程类型**: {course_info.get("course_type", "待定")}
- **目标受众**: {course_info.get("target_audience", "待定")}
- **总课时**: {course_info.get("teaching_hours", "待定")}课时
- **创建时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 教学目标

### 知识目标
{content.get("knowledge_objectives", "")}

### 能力目标
{content.get("ability_objectives", "")}

### 情感目标
{content.get("emotion_objectives", "")}

---

## 教学重难点

### 重点
{content.get("key_points", "")}

### 难点
{content.get("difficult_points", "")}

---

## 教学方法

{content.get("teaching_methods", "")}

---

## 教学过程

{content.get("teaching_process", "")}

---

## 教学评价

{content.get("evaluation", "")}

---

## 课后反思

{content.get("reflection", "")}

"""
        return md

    @staticmethod
    def generate_syllabus(
        course_name: str, course_info: Dict[str, Any], chapters: List[Dict[str, Any]]
    ) -> str:
        """
        生成教学大纲Markdown

        Args:
            course_name: 课程名称
            course_info: 课程基本信息
            chapters: 章节列表

        Returns:
            Markdown格式的教学大纲
        """
        md = f"""# {course_name} 教学大纲

## 课程基本信息

- **课程名称**: {course_name}
- **课程类型**: {course_info.get("course_type", "待定")}
- **目标受众**: {course_info.get("target_audience", "待定")}
- **总课时**: {course_info.get("teaching_hours", "待定")}课时
- **创建时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 课程概述

{course_info.get("overview", "")}

---

## 课程目录

"""
        for i, chapter in enumerate(chapters, 1):
            md += f"""
### 第{i}章 {chapter.get("title", "待定")}

**课时**: {chapter.get("hours", "待定")}课时

**内容**:
{chapter.get("content", "")}

**目标**:
{chapter.get("objectives", "")}

"""

        md += """
---

## 考核方式

- 平时成绩: {}%
- 期末考试: {}%

---

## 参考教材

{}
"""
        return md

    @staticmethod
    def generate_ppt_content(course_name: str, slides: List[Dict[str, Any]]) -> str:
        """
        生成PPT大纲Markdown（可用于转换为PPT）

        Args:
            course_name: 课程名称
            slides: 幻灯片列表

        Returns:
            Markdown格式的PPT大纲
        """
        md = f"""# {course_name} 课件

## 幻灯片大纲

"""
        for i, slide in enumerate(slides, 1):
            md += f"""
### 第{i}页: {slide.get("title", "待定")}

**类型**: {slide.get("type", "内容页")}

**内容**:
{slide.get("content", "")}

**备注**:
{slide.get("notes", "")}

"""

        return md


class JsonGenerator:
    """JSON数据生成器"""

    @staticmethod
    def generate_schedule(
        course_name: str, teaching_hours: int, schedule: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成课程进度计划JSON

        Args:
            course_name: 课程名称
            teaching_hours: 总课时
            schedule: 进度计划列表

        Returns:
            JSON格式的进度计划
        """
        return {
            "course_name": course_name,
            "total_hours": teaching_hours,
            "created_at": datetime.now().isoformat(),
            "schedule": schedule,
            "metadata": {"version": "1.0", "format": "course_schedule"},
        }

    @staticmethod
    def generate_weekly_plan(
        week: int, topics: List[str], objectives: List[str], activities: List[str]
    ) -> Dict[str, Any]:
        """
        生成周计划JSON

        Args:
            week: 周次
            topics: 主题列表
            objectives: 目标列表
            activities: 活动列表

        Returns:
            周计划字典
        """
        return {
            "week": week,
            "topics": topics,
            "learning_objectives": objectives,
            "activities": activities,
            "homework": [],
            "notes": "",
        }
