"""
skills._base.soft_loader - Soft Skill (SKILL.md) 加载器

从文件系统加载 OpenClaw 风格的 SKILL.md 文件。
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedSkill:
    """解析后的 SKILL.md 数据"""
    name: str
    display_name: str
    description: str
    version: str
    author: str
    category: str
    tags: List[str]
    triggers: List[str]
    parameters: List[Dict[str, Any]]
    content: str
    runtime: Optional[str]
    timeout: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "tags": self.tags,
            "triggers": self.triggers,
            "parameters": self.parameters,
            "content": self.content,
            "runtime": self.runtime,
            "timeout": self.timeout,
            "skill_type": "soft",
        }


class SoftSkillLoader:
    """
    Soft Skill 加载器
    
    从指定目录加载所有 .SKILL.md 文件并解析。
    
    使用方式:
    ```python
    loader = SoftSkillLoader()
    
    # 加载目录
    skills = loader.load_directory("./skills/soft/skills")
    
    # 加载单个文件
    skill = loader.load_file("./skills/soft/skills/quick-lesson.SKILL.md")
    ```
    """
    
    def __init__(self):
        """初始化加载器"""
        self._loaded_skills: Dict[str, Dict[str, Any]] = {}
    
    def load_directory(self, directory: str) -> Dict[str, Dict[str, Any]]:
        """
        加载目录中的所有 SKILL.md 文件
        
        Args:
            directory: 目录路径
            
        Returns:
            {name: skill_data} 格式的字典
        """
        path = Path(directory)
        
        if not path.exists():
            logger.warning(f"Soft skills directory not found: {directory}")
            return {}
        
        if not path.is_dir():
            logger.warning(f"Path is not a directory: {directory}")
            return {}
        
        skills = {}
        
        # 递归查找所有 .SKILL.md 文件
        for skill_file in path.rglob("*.SKILL.md"):
            try:
                skill_data = self.load_file(str(skill_file))
                if skill_data:
                    name = skill_data["name"]
                    skills[name] = skill_data
                    logger.info(f"Loaded soft skill: {name} from {skill_file}")
            except Exception as e:
                logger.error(f"Failed to load skill from {skill_file}: {e}")
        
        self._loaded_skills.update(skills)
        return skills
    
    def load_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        加载单个 SKILL.md 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的技能数据，解析失败返回 None
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Skill file not found: {file_path}")
            return None
        
        try:
            content = path.read_text(encoding="utf-8")
            return self.parse_skill_md(content, file_path)
        except Exception as e:
            logger.error(f"Failed to read skill file {file_path}: {e}")
            return None
    
    def parse_skill_md(self, content: str, source: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        解析 SKILL.md 内容
        
        支持两种格式:
        1. OpenClaw 格式: YAML frontmatter + Markdown 正文
        2. 简化格式: 直接 YAML
        
        Args:
            content: 文件内容
            source: 来源标识（用于错误信息）
            
        Returns:
            解析后的技能数据
        """
        # 提取 YAML frontmatter
        frontmatter_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n?(.*)$',
            content,
            re.DOTALL
        )
        
        if frontmatter_match:
            yaml_content = frontmatter_match.group(1)
            markdown_content = frontmatter_match.group(2).strip()
        else:
            # 没有 frontmatter，整个内容作为 markdown
            yaml_content = ""
            markdown_content = content.strip()
        
        # 解析 YAML
        metadata = self._parse_yaml_frontmatter(yaml_content)
        
        if not metadata:
            # 尝试从 markdown 中提取信息
            metadata = self._extract_from_markdown(content)
        
        # 验证必需字段
        if "name" not in metadata:
            logger.error(f"Skill missing required 'name' field in {source}")
            return None
        
        # 构建结果
        result = {
            "name": metadata.get("name", "unnamed"),
            "display_name": metadata.get("display_name", self._to_display_name(metadata.get("name", ""))),
            "description": metadata.get("description", ""),
            "version": metadata.get("version", "1.0.0"),
            "author": metadata.get("author", "custom"),
            "category": metadata.get("category", "custom"),
            "tags": metadata.get("tags", []),
            "triggers": metadata.get("triggers", []),
            "parameters": metadata.get("parameters", []),
            "content": markdown_content or metadata.get("description", ""),
            "runtime": metadata.get("runtime"),
            "timeout": int(metadata.get("timeout", 60)),
            "skill_type": "soft",
        }
        
        return result
    
    def _parse_yaml_frontmatter(self, yaml_content: str) -> Dict[str, Any]:
        """解析 YAML frontmatter"""
        if not yaml_content.strip():
            return {}
        
        result = {}
        current_key = None
        current_list = []
        in_list = False
        
        for line in yaml_content.split("\n"):
            line = line.rstrip()
            
            # 检查是否是列表项
            if re.match(r"^\s+-\s+", line):
                if not in_list:
                    in_list = True
                    current_list = []
                # 提取列表项值
                value = re.sub(r"^\s+-\s+", "", line).strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                current_list.append(value)
                if current_key:
                    result[current_key] = current_list
                continue
            else:
                if in_list and current_key:
                    # 列表结束
                    in_list = False
            
            # 解析键值对
            match = re.match(r'^(\w+):\s*(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                
                # 处理值
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                
                current_key = key
                current_list = []
                result[key] = value
        
        return result
    
    def _extract_from_markdown(self, content: str) -> Dict[str, Any]:
        """从 Markdown 内容中提取信息"""
        result = {}
        
        # 提取标题作为名称
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            result["name"] = self._to_snake_case(title)
            result["display_name"] = title
            result["description"] = title
        
        return result
    
    def _to_display_name(self, name: str) -> str:
        """将名称转换为显示名称"""
        return name.replace("-", " ").replace("_", " ").title()
    
    def _to_snake_case(self, text: str) -> str:
        """转换为 snake_case"""
        s = re.sub(r"[^a-zA-Z0-9]", "-", text)
        s = re.sub(r"-+", "-", s)
        return s.strip("-").lower()
    
    def get_loaded_skills(self) -> Dict[str, Dict[str, Any]]:
        """获取已加载的技能"""
        return self._loaded_skills.copy()
    
    def clear(self) -> None:
        """清空已加载的技能"""
        self._loaded_skills.clear()
