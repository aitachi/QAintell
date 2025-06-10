import asyncio
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod


class BaseTool(ABC):
    def __init__(self, name: str, description: str, version: str = "1.0"):
        self.name = name
        self.description = description
        self.version = version
        self.capabilities = []
        self.dependencies = []
        self.timeout = 30.0
        self.retry_count = 2

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        pass

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies
        }


class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._tool_categories = {}
        self._tool_dependencies = {}
        self._tool_performance = {}
        self._initialize_default_tools()

    def _initialize_default_tools(self):
        from .web_search_tool import WebSearchTool
        from .rag_retrieval_tool import RAGRetrievalTool
        from .calculator_tool import CalculatorTool
        from .translator_tool import TranslatorTool

        default_tools = [
            WebSearchTool(),
            RAGRetrievalTool(),
            CalculatorTool(),
            TranslatorTool()
        ]

        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool) -> bool:
        if not isinstance(tool, BaseTool):
            return False

        self._tools[tool.name] = tool
        self._update_tool_categories(tool)
        self._update_dependencies(tool)
        self._initialize_performance_tracking(tool)

        return True

    def unregister_tool(self, tool_name: str) -> bool:
        if tool_name in self._tools:
            del self._tools[tool_name]
            self._cleanup_tool_data(tool_name)
            return True
        return False

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        return self._tools.get(tool_name)

    def list_tools(self, category: str = None) -> List[str]:
        if category:
            return self._tool_categories.get(category, [])
        return list(self._tools.keys())

    def find_tools_by_capability(self, capability: str) -> List[str]:
        matching_tools = []
        for tool_name, tool in self._tools.items():
            if capability in tool.capabilities:
                matching_tools.append(tool_name)
        return matching_tools

    def get_tool_dependencies(self, tool_name: str) -> List[str]:
        return self._tool_dependencies.get(tool_name, [])

    def validate_tool_chain(self, tool_chain: List[str]) -> Dict[str, Any]:
        validation_result = {
            "valid": True,
            "missing_tools": [],
            "dependency_issues": [],
            "circular_dependencies": []
        }

        for tool_name in tool_chain:
            if tool_name not in self._tools:
                validation_result["missing_tools"].append(tool_name)
                validation_result["valid"] = False

        dependency_graph = self._build_dependency_graph(tool_chain)
        circular_deps = self._detect_circular_dependencies(dependency_graph)

        if circular_deps:
            validation_result["circular_dependencies"] = circular_deps
            validation_result["valid"] = False

        return validation_result

    def get_optimal_tool_order(self, tool_names: List[str]) -> List[str]:
        dependency_graph = self._build_dependency_graph(tool_names)
        return self._topological_sort(dependency_graph)

    def get_tool_performance(self, tool_name: str) -> Dict[str, Any]:
        return self._tool_performance.get(tool_name, {
            "average_execution_time": 0.0,
            "success_rate": 1.0,
            "error_count": 0,
            "total_executions": 0
        })

    def update_tool_performance(self, tool_name: str, execution_time: float, success: bool):
        if tool_name not in self._tool_performance:
            self._initialize_performance_tracking_for_tool(tool_name)

        perf = self._tool_performance[tool_name]
        perf["total_executions"] += 1

        if success:
            current_avg = perf["average_execution_time"]
            total_execs = perf["total_executions"]
            perf["average_execution_time"] = (current_avg * (total_execs - 1) + execution_time) / total_execs
        else:
            perf["error_count"] += 1

        perf["success_rate"] = (perf["total_executions"] - perf["error_count"]) / perf["total_executions"]

    def get_recommended_tools(self, task_description: str, context: Dict[str, Any]) -> List[str]:
        task_lower = task_description.lower()
        recommended = []

        tool_keywords = {
            "web_search": ["搜索", "查找", "最新", "新闻", "信息"],
            "rag_retrieval": ["知识库", "文档", "资料", "参考"],
            "calculator": ["计算", "数学", "公式", "数字"],
            "translator": ["翻译", "英文", "中文", "语言"]
        }

        for tool_name, keywords in tool_keywords.items():
            if tool_name in self._tools:
                score = sum(1 for keyword in keywords if keyword in task_lower)
                if score > 0:
                    recommended.append((tool_name, score))

        recommended.sort(key=lambda x: x[1], reverse=True)
        return [tool_name for tool_name, score in recommended]

    def _update_tool_categories(self, tool: BaseTool):
        category = self._determine_tool_category(tool)
        if category not in self._tool_categories:
            self._tool_categories[category] = []
        if tool.name not in self._tool_categories[category]:
            self._tool_categories[category].append(tool.name)

    def _determine_tool_category(self, tool: BaseTool) -> str:
        category_mapping = {
            "search": ["web_search", "rag_retrieval"],
            "computation": ["calculator", "data_analyzer"],
            "communication": ["translator", "summarizer"],
            "file": ["file_manager", "document_processor"],
            "api": ["api_client", "webhook"]
        }

        for category, tool_patterns in category_mapping.items():
            if any(pattern in tool.name.lower() for pattern in tool_patterns):
                return category

        return "general"

    def _update_dependencies(self, tool: BaseTool):
        self._tool_dependencies[tool.name] = tool.dependencies.copy()

    def _initialize_performance_tracking(self, tool: BaseTool):
        self._initialize_performance_tracking_for_tool(tool.name)

    def _initialize_performance_tracking_for_tool(self, tool_name: str):
        self._tool_performance[tool_name] = {
            "average_execution_time": 0.0,
            "success_rate": 1.0,
            "error_count": 0,
            "total_executions": 0
        }

    def _cleanup_tool_data(self, tool_name: str):
        for category, tools in self._tool_categories.items():
            if tool_name in tools:
                tools.remove(tool_name)

        if tool_name in self._tool_dependencies:
            del self._tool_dependencies[tool_name]

        if tool_name in self._tool_performance:
            del self._tool_performance[tool_name]

    def _build_dependency_graph(self, tool_names: List[str]) -> Dict[str, List[str]]:
        graph = {}
        for tool_name in tool_names:
            if tool_name in self._tools:
                dependencies = self._tool_dependencies.get(tool_name, [])
                graph[tool_name] = [dep for dep in dependencies if dep in tool_names]
        return graph

    def _detect_circular_dependencies(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path + [node])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        in_degree = {node: 0 for node in graph}

        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1

        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result