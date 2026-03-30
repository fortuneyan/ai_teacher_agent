"""
搜索工具集
对应第4章 - Function Calling
用于收集教材内容、查询课程标准等
"""

from typing import List, Dict, Any, Optional
import re


class SearchTool:
    """搜索工具基类"""

    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def search(self, query: str) -> List[Dict[str, str]]:
        """执行搜索"""
        raise NotImplementedError


class DuckDuckGoSearchTool(SearchTool):
    """DuckDuckGo搜索工具"""

    def __init__(self, max_results: int = 10):
        super().__init__(max_results)

    def search(self, query: str) -> List[Dict[str, str]]:
        """
        使用DuckDuckGo搜索
        注意: 需要安装 duckduckgo-search 库
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            ddgs = DDGS()
            for r in ddgs.text(query, max_results=self.max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "content": r.get("body", ""),
                    }
                )
            return results
        except ImportError:
            return self._mock_search(query)

    def _mock_search(self, query: str) -> List[Dict[str, str]]:
        """模拟搜索结果（用于测试）"""
        return [
            {
                "title": f"关于{query}的教材内容",
                "url": "https://example.com/textbook",
                "content": f"这是{query}的教材内容摘要...",
            }
        ]


class WebContentFetcher:
    """网页内容获取工具"""

    @staticmethod
    def fetch(url: str) -> str:
        """
        获取网页内容

        Args:
            url: 网页URL

        Returns:
            网页文本内容
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()

            # 获取文本
            text = soup.get_text()

            # 清理空白
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text[:5000]  # 限制长度
        except ImportError:
            return "需要安装 requests 和 beautifulsoup4 库"
        except Exception as e:
            return f"获取失败: {str(e)}"


class TextbookCollector:
    """
    教材收集器 - 对应AI_Teacher的核心功能
    收集指定课程的教材内容
    """

    def __init__(self, search_tool: SearchTool):
        self.search_tool = search_tool
        self.content_fetcher = WebContentFetcher()

    def collect(self, course_name: str, course_type: str = None) -> Dict[str, Any]:
        """
        收集教材内容

        Args:
            course_name: 课程名称
            course_type: 课程类型

        Returns:
            收集到的教材内容
        """
        # 构建搜索查询
        queries = self._build_queries(course_name, course_type)

        all_results = []

        for query in queries:
            results = self.search_tool.search(query)
            all_results.extend(results)

        # 去重
        unique_results = self._deduplicate_results(all_results)

        # 提取关键内容
        materials = self._extract_materials(unique_results, course_name)

        return {
            "course_name": course_name,
            "course_type": course_type,
            "materials": materials,
            "source_count": len(unique_results),
        }

    def _build_queries(self, course_name: str, course_type: str = None) -> List[str]:
        """构建搜索查询列表"""
        queries = [
            f"{course_name} 教材",
            f"{course_name} 教学大纲",
            f"{course_name} 课程标准",
        ]

        if course_type:
            queries.append(f"{course_type} {course_name} 教程")

        return queries

    def _deduplicate_results(
        self, results: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """去重搜索结果"""
        seen = set()
        unique = []

        for r in results:
            if r.get("url") not in seen:
                seen.add(r.get("url"))
                unique.append(r)

        return unique

    def _extract_materials(
        self, results: List[Dict[str, str]], course_name: str
    ) -> List[Dict[str, Any]]:
        """从搜索结果中提取教材内容"""
        materials = []

        for r in results:
            material = {
                "title": r.get("title", ""),
                "source": r.get("url", ""),
                "content": self._clean_content(r.get("content", "")),
                "type": self._identify_content_type(r.get("title", "")),
            }
            materials.append(material)

        return materials

    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余空白
        content = re.sub(r"\s+", " ", content)
        # 移除特殊字符
        content = re.sub(r"[^\w\s\u4e00-\u9fff,.!?;:()（）【】《》]", "", content)
        return content.strip()

    def _identify_content_type(self, title: str) -> str:
        """识别内容类型"""
        title_lower = title.lower()

        if "教材" in title or "课本" in title:
            return "textbook"
        elif "大纲" in title or "目录" in title:
            return "syllabus"
        elif "标准" in title or "规范" in title:
            return "standard"
        elif "教案" in title or "教学" in title:
            return "lesson_plan"
        else:
            return "general"


class CurriculumStandardFetcher:
    """课程标准获取器"""

    def __init__(self, search_tool: SearchTool):
        self.search_tool = search_tool

    def fetch(self, course_name: str, education_level: str = "高中") -> Dict[str, Any]:
        """
        获取课程标准

        Args:
            course_name: 课程名称
            education_level: 教育阶段（高中、初中、小学、大学等）

        Returns:
            课程标准信息
        """
        query = f"{education_level} {course_name} 课程标准"
        results = self.search_tool.search(query)

        standards = []
        for r in results:
            standards.append(
                {
                    "title": r.get("title", ""),
                    "source": r.get("url", ""),
                    "content": r.get("content", ""),
                }
            )

        return {
            "course_name": course_name,
            "education_level": education_level,
            "standards": standards,
        }
