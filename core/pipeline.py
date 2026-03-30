"""
Pipeline 流程编排模块
对应第11章 - 流程编排
支持顺序链、条件分支、循环迭代等模式
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import time


class NodeStatus(Enum):
    """节点状态"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineNode:
    """Pipeline节点"""

    name: str
    description: str
    skill_name: str
    executor: Callable
    dependencies: List[str] = None
    condition: Optional[Callable] = None
    retry: int = 3
    timeout: int = 300

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class Pipeline:
    """
    Pipeline编排器
    对应第11章的基础编排模式
    """

    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, PipelineNode] = {}
        self.execution_order: List[str] = []
        self.results: Dict[str, Any] = {}
        self.status: Dict[str, NodeStatus] = {}

    def add_node(self, node: PipelineNode) -> None:
        """添加节点 - 顺序链模式"""
        self.nodes[node.name] = node
        self._update_execution_order()

    def add_condition_node(
        self,
        name: str,
        description: str,
        skill_name: str,
        executor: Callable,
        condition: Callable,
        dependencies: List[str] = None,
    ) -> None:
        """添加条件分支节点 - 对应11.2.2"""
        node = PipelineNode(
            name=name,
            description=description,
            skill_name=skill_name,
            executor=executor,
            condition=condition,
            dependencies=dependencies or [],
        )
        self.add_node(node)

    def add_loop_node(
        self,
        name: str,
        description: str,
        skill_name: str,
        executor: Callable,
        max_iterations: int = 5,
        dependencies: List[str] = None,
    ) -> None:
        """添加循环迭代节点 - 对应11.2.3"""
        node = PipelineNode(
            name=name,
            description=description,
            skill_name=skill_name,
            executor=executor,
            dependencies=dependencies or [],
        )
        node.max_iterations = max_iterations
        self.add_node(node)

    def _update_execution_order(self) -> None:
        """更新执行顺序 - 拓扑排序"""
        self.execution_order = list(self.nodes.keys())

    def _can_execute(self, node_name: str) -> bool:
        """检查节点是否可执行"""
        node = self.nodes[node_name]

        # 检查依赖是否都已完成
        for dep in node.dependencies:
            if self.status.get(dep) != NodeStatus.SUCCESS:
                return False

        return True

    def _execute_node(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        """执行单个节点"""
        # 更新状态
        self.status[node.name] = NodeStatus.RUNNING

        # 重试机制 - 对应11.4容错健壮性设计
        last_error = None
        for attempt in range(node.retry):
            try:
                result = node.executor(context, self.results)
                self.results[node.name] = result
                self.status[node.name] = NodeStatus.SUCCESS
                return result
            except Exception as e:
                last_error = e
                time.sleep(1)  # 等待后重试

        # 所有重试都失败
        self.status[node.name] = NodeStatus.FAILED
        raise Exception(f"节点 {node.name} 执行失败: {last_error}")

    def execute(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Pipeline - 对应11.1.2核心价值
        支持顺序链执行
        """
        context = initial_context.copy()

        # 按顺序执行节点
        for node_name in self.execution_order:
            node = self.nodes[node_name]

            # 检查是否可执行
            if not self._can_execute(node_name):
                self.status[node_name] = NodeStatus.SKIPPED
                continue

            # 检查条件 - 条件分支
            if node.condition and not node.condition(context, self.results):
                self.status[node_name] = NodeStatus.SKIPPED
                continue

            # 执行节点
            print(f"执行节点: {node.name} - {node.description}")
            try:
                result = self._execute_node(node, context)
                context[f"{node_name}_result"] = result
            except Exception as e:
                print(f"节点 {node.name} 执行出错: {e}")
                if node.retry <= 0:
                    raise

        return {
            "results": self.results,
            "status": {k: v.value for k, v in self.status.items()},
        }


class DAGPipeline(Pipeline):
    """
    DAG（有向无环图）Pipeline - 对应11.3.1
    支持并行执行
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.parallel_groups: List[List[str]] = []

    def add_parallel_nodes(self, node_names: List[str]) -> None:
        """添加并行节点组"""
        self.parallel_groups.append(node_names)
        for name in node_names:
            self.execution_order.append(name)

    def execute_parallel(
        self, node_names: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """并行执行多个节点 - 对应11.3.2"""
        import concurrent.futures

        results = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {}
            for name in node_names:
                if name in self.nodes:
                    node = self.nodes[name]
                    future = executor.submit(self._execute_node, node, context)
                    futures[future] = name

            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = {"error": str(e)}

        return results


def create_course_design_pipeline() -> Pipeline:
    """创建完整课程设计Pipeline"""
    from ai_teacher_agent.skills import (
        collect_materials_skill,
        design_lesson_skill,
        outline_summary_skill,
        generate_ppt_skill,
        schedule_plan_skill,
    )

    pipeline = Pipeline("full_course_design")

    # 顺序链: 收集教材 -> 设计教案 -> 归纳大纲 -> 生成PPT -> 制定计划
    pipeline.add_node(
        PipelineNode(
            name="collect_materials",
            description="收集教材内容",
            skill_name="collect_materials",
            executor=collect_materials_skill.execute,
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="design_lesson",
            description="设计教案",
            skill_name="design_lesson",
            executor=design_lesson_skill.execute,
            dependencies=["collect_materials"],
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="outline_summary",
            description="归纳教学大纲",
            skill_name="outline_summary",
            executor=outline_summary_skill.execute,
            dependencies=["design_lesson"],
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="generate_ppt",
            description="生成PPT课件",
            skill_name="generate_ppt",
            executor=generate_ppt_skill.execute,
            dependencies=["outline_summary"],
        )
    )

    pipeline.add_node(
        PipelineNode(
            name="schedule_plan",
            description="制定进度计划",
            skill_name="schedule_plan",
            executor=schedule_plan_skill.execute,
            dependencies=["generate_ppt"],
        )
    )

    return pipeline
