import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from .tool_registry import ToolRegistry, BaseTool


class ToolDependencyGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_tool(self, tool: BaseTool, input_deps: List[str], output_deps: List[str]):
        self.nodes[tool.name] = {
            'tool': tool,
            'input_deps': input_deps,
            'output_deps': output_deps,
            'status': 'pending'
        }
        self.edges[tool.name] = output_deps

    def get_ready_tools(self) -> List[str]:
        ready = []
        for tool_name, node in self.nodes.items():
            if node['status'] == 'pending':
                if all(self.nodes[dep]['status'] == 'completed' for dep in node['input_deps']):
                    ready.append(tool_name)
        return ready

    def mark_completed(self, tool_name: str):
        if tool_name in self.nodes:
            self.nodes[tool_name]['status'] = 'completed'

    def mark_failed(self, tool_name: str):
        if tool_name in self.nodes:
            self.nodes[tool_name]['status'] = 'failed'

    def topological_sort(self) -> List[str]:
        result = []
        temp_graph = {name: node['input_deps'].copy() for name, node in self.nodes.items()}

        while temp_graph:
            ready = [name for name, deps in temp_graph.items() if not deps]
            if not ready:
                remaining = list(temp_graph.keys())
                return result + remaining

            for tool_name in ready:
                result.append(tool_name)
                del temp_graph[tool_name]

                for remaining_tool, deps in temp_graph.items():
                    if tool_name in deps:
                        deps.remove(tool_name)

        return result


class ExecutionPlan:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage):
        self.stages.append(stage)


class ExecutionStage:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)


class ToolTask:
    def __init__(self, tool_name: str, tool: BaseTool, params: Dict[str, Any], context: Dict[str, Any]):
        self.tool_name = tool_name
        self.tool = tool
        self.params = params
        self.context = context
        self.result = None
        self.error = None
        self.execution_time = 0.0
        self.status = 'pending'

    def is_successful(self) -> bool:
        return self.status == 'completed' and self.error is None


class IntelligentToolOrchestrator:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.dependency_analyzer = ToolDependencyAnalyzer()
        self.execution_planner = ExecutionPlanner()
        self.result_integrator = ResultIntegrator()
        self.max_parallel_tools = 3
        self.default_timeout = 30.0

    async def orchestrate_tools(self, question: str, tool_requirements: List[Dict[str, Any]],
                                knowledge_context: Dict[str, Any]) -> Dict[str, Any]:
        tool_graph = self.analyze_tool_dependencies(tool_requirements, question)
        execution_plan = self.generate_execution_plan(tool_graph, knowledge_context)
        execution_results = await self.execute_plan(execution_plan)
        integrated_results = self.integrate_results(execution_results, question)

        return integrated_results

    async def execute_tools(self, tool_names: List[str], question: str, knowledge_context: Dict[str, Any]) -> Dict[
        str, Any]:
        tool_requirements = []
        for tool_name in tool_names:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                tool_requirements.append({
                    'name': tool_name,
                    'params': self._generate_tool_params(tool_name, question, knowledge_context)
                })

        return await self.orchestrate_tools(question, tool_requirements, knowledge_context)

    def analyze_tool_dependencies(self, tool_requirements: List[Dict[str, Any]], question: str) -> ToolDependencyGraph:
        tool_graph = ToolDependencyGraph()

        for tool_spec in tool_requirements:
            tool_name = tool_spec['name']
            tool = self.tool_registry.get_tool(tool_name)

            if tool:
                input_deps = self.dependency_analyzer.analyze_input_dependencies(tool, question)
                output_deps = self.dependency_analyzer.analyze_output_dependencies(tool, tool_requirements)
                tool_graph.add_tool(tool, input_deps, output_deps)

        return tool_graph

    def generate_execution_plan(self, tool_graph: ToolDependencyGraph,
                                knowledge_context: Dict[str, Any]) -> ExecutionPlan:
        plan = ExecutionPlan()
        execution_order = tool_graph.topological_sort()
        parallel_groups = self._identify_parallel_groups(execution_order, tool_graph)

        for group in parallel_groups:
            stage = ExecutionStage()
            for tool_name in group:
                tool_node = tool_graph.nodes[tool_name]
                task = self._create_tool_task(tool_node['tool'], knowledge_context)
                stage.add_task(task)
            plan.add_stage(stage)

        return plan

    async def execute_plan(self, execution_plan: ExecutionPlan) -> Dict[str, Any]:
        results = {}

        for stage in execution_plan.stages:
            if len(stage.tasks) == 1:
                task = stage.tasks[0]
                result = await self._execute_tool_task(task)
                results[task.tool_name] = result
            else:
                stage_tasks = [self._execute_tool_task(task) for task in stage.tasks]
                stage_results = await asyncio.gather(*stage_tasks, return_exceptions=True)

                for task, result in zip(stage.tasks, stage_results):
                    results[task.tool_name] = result

            failed_tasks = [task for task in stage.tasks if not task.is_successful()]
            if failed_tasks:
                retry_results = await self._handle_failed_tasks(failed_tasks)
                results.update(retry_results)

        return results

    def integrate_results(self, execution_results: Dict[str, Any], question: str) -> Dict[str, Any]:
        return self.result_integrator.integrate_tool_results(execution_results, question)

    def _identify_parallel_groups(self, execution_order: List[str], tool_graph: ToolDependencyGraph) -> List[List[str]]:
        groups = []
        remaining_tools = execution_order.copy()

        while remaining_tools:
            current_group = []
            tools_to_remove = []

            for tool_name in remaining_tools:
                tool_node = tool_graph.nodes[tool_name]
                dependencies_satisfied = all(
                    dep not in remaining_tools for dep in tool_node['input_deps']
                )

                if dependencies_satisfied and len(current_group) < self.max_parallel_tools:
                    current_group.append(tool_name)
                    tools_to_remove.append(tool_name)

            if not current_group and remaining_tools:
                current_group.append(remaining_tools[0])
                tools_to_remove.append(remaining_tools[0])

            for tool_name in tools_to_remove:
                remaining_tools.remove(tool_name)

            if current_group:
                groups.append(current_group)

        return groups

    def _create_tool_task(self, tool: BaseTool, knowledge_context: Dict[str, Any]) -> ToolTask:
        params = self._generate_tool_params(tool.name, knowledge_context.get('question', ''), knowledge_context)
        return ToolTask(tool.name, tool, params, knowledge_context)

    def _generate_tool_params(self, tool_name: str, question: str, knowledge_context: Dict[str, Any]) -> Dict[str, Any]:
        base_params = {
            'query': question,
            'context': knowledge_context
        }

        tool_specific_params = {
            'web_search': {
                'query': question,
                'max_results': 5,
                'language': 'zh-CN'
            },
            'rag_retrieval': {
                'query': question,
                'top_k': 10,
                'threshold': 0.7
            },
            'calculator': {
                'expression': self._extract_math_expression(question)
            },
            'translator': {
                'text': question,
                'target_language': 'en' if '翻译' in question else 'zh'
            }
        }

        if tool_name in tool_specific_params:
            base_params.update(tool_specific_params[tool_name])

        return base_params

    async def _execute_tool_task(self, task: ToolTask) -> Dict[str, Any]:
        start_time = time.time()

        try:
            task.status = 'running'

            if not task.tool.validate_params(task.params):
                raise ValueError(f"Invalid parameters for tool {task.tool_name}")

            result = await asyncio.wait_for(
                task.tool.execute(task.params),
                timeout=getattr(task.tool, 'timeout', self.default_timeout)
            )

            task.result = result
            task.status = 'completed'
            task.execution_time = time.time() - start_time

            self.tool_registry.update_tool_performance(task.tool_name, task.execution_time, True)

            return {
                'tool_name': task.tool_name,
                'success': True,
                'result': result,
                'execution_time': task.execution_time
            }

        except Exception as e:
            task.error = str(e)
            task.status = 'failed'
            task.execution_time = time.time() - start_time

            self.tool_registry.update_tool_performance(task.tool_name, task.execution_time, False)

            return {
                'tool_name': task.tool_name,
                'success': False,
                'error': str(e),
                'execution_time': task.execution_time
            }

    async def _handle_failed_tasks(self, failed_tasks: List[ToolTask]) -> Dict[str, Any]:
        retry_results = {}

        for task in failed_tasks:
            if hasattr(task.tool, 'retry_count') and task.tool.retry_count > 0:
                retry_result = await self._retry_tool_task(task)
                retry_results[task.tool_name] = retry_result
            else:
                retry_results[task.tool_name] = {
                    'tool_name': task.tool_name,
                    'success': False,
                    'error': task.error,
                    'retry_attempted': False
                }

        return retry_results

    async def _retry_tool_task(self, task: ToolTask) -> Dict[str, Any]:
        max_retries = getattr(task.tool, 'retry_count', 1)

        for attempt in range(max_retries):
            try:
                await asyncio.sleep(min(2 ** attempt, 10))

                result = await asyncio.wait_for(
                    task.tool.execute(task.params),
                    timeout=getattr(task.tool, 'timeout', self.default_timeout)
                )

                return {
                    'tool_name': task.tool_name,
                    'success': True,
                    'result': result,
                    'retry_attempt': attempt + 1
                }

            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        'tool_name': task.tool_name,
                        'success': False,
                        'error': str(e),
                        'retry_attempts': max_retries
                    }

        return {
            'tool_name': task.tool_name,
            'success': False,
            'error': 'Max retries exceeded'
        }

    def _extract_math_expression(self, question: str) -> str:
        import re
        math_patterns = [
            r'(\d+(?:\.\d+)?)\s*[\+\-\*\/]\s*(\d+(?:\.\d+)?)',
            r'计算\s*(.+)',
            r'求\s*(.+)',
        ]

        for pattern in math_patterns:
            match = re.search(pattern, question)
            if match:
                return match.group(1) if 'calculate' in pattern or '计算' in pattern else match.group(0)

        return question


class ToolDependencyAnalyzer:
    def analyze_input_dependencies(self, tool: BaseTool, question: str) -> List[str]:
        dependency_rules = {
            'calculator': ['web_search', 'rag_retrieval'],
            'data_analyzer': ['web_search', 'rag_retrieval', 'file_manager'],
            'code_executor': ['rag_retrieval'],
            'translator': [],
            'web_search': [],
            'rag_retrieval': []
        }

        return dependency_rules.get(tool.name, [])

    def analyze_output_dependencies(self, tool: BaseTool, tool_requirements: List[Dict[str, Any]]) -> List[str]:
        other_tools = [req['name'] for req in tool_requirements if req['name'] != tool.name]

        output_rules = {
            'web_search': ['calculator', 'data_analyzer'],
            'rag_retrieval': ['calculator', 'data_analyzer', 'code_executor'],
            'calculator': [],
            'translator': [],
            'data_analyzer': [],
            'code_executor': []
        }

        potential_outputs = output_rules.get(tool.name, [])
        return [tool_name for tool_name in potential_outputs if tool_name in other_tools]


class ExecutionPlanner:
    pass


class ResultIntegrator:
    def integrate_tool_results(self, execution_results: Dict[str, Any], question: str) -> Dict[str, Any]:
        successful_results = {}
        failed_results = {}

        for tool_name, result in execution_results.items():
            if isinstance(result, dict) and result.get('success', False):
                successful_results[tool_name] = result.get('result', {})
            else:
                failed_results[tool_name] = result

        integrated_data = self._combine_successful_results(successful_results)
        confidence = self._calculate_integration_confidence(successful_results, failed_results)

        return {
            'integrated_data': integrated_data,
            'individual_results': successful_results,
            'failed_tools': failed_results,
            'confidence': confidence,
            'summary': self._generate_integration_summary(successful_results, question)
        }

    def _combine_successful_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        combined = {
            'search_results': [],
            'knowledge_base_results': [],
            'calculations': [],
            'translations': [],
            'analysis_results': []
        }

        for tool_name, result in results.items():
            if 'search' in tool_name:
                combined['search_results'].extend(result.get('results', []))
            elif 'rag' in tool_name or 'knowledge' in tool_name:
                combined['knowledge_base_results'].extend(result.get('results', []))
            elif 'calculator' in tool_name:
                combined['calculations'].append(result)
            elif 'translator' in tool_name:
                combined['translations'].append(result)
            else:
                combined['analysis_results'].append(result)

        return combined

    def _calculate_integration_confidence(self, successful: Dict[str, Any], failed: Dict[str, Any]) -> float:
        total_tools = len(successful) + len(failed)
        if total_tools == 0:
            return 0.0

        success_rate = len(successful) / total_tools

        critical_tools = ['web_search', 'rag_retrieval']
        critical_success = sum(1 for tool in critical_tools if tool in successful)
        critical_total = sum(1 for tool in critical_tools if tool in successful or tool in failed)

        if critical_total > 0:
            critical_success_rate = critical_success / critical_total
            return (success_rate * 0.6 + critical_success_rate * 0.4)

        return success_rate

    def _generate_integration_summary(self, results: Dict[str, Any], question: str) -> str:
        summary_parts = []

        if 'web_search' in results:
            search_count = len(results['web_search'].get('results', []))
            summary_parts.append(f"网络搜索找到 {search_count} 条相关信息")

        if 'rag_retrieval' in results:
            kb_count = len(results['rag_retrieval'].get('results', []))
            summary_parts.append(f"知识库检索到 {kb_count} 条相关内容")

        if 'calculator' in results:
            summary_parts.append("完成了数学计算")

        if 'translator' in results:
            summary_parts.append("完成了翻译任务")

        if summary_parts:
            return "工具执行结果：" + "，".join(summary_parts)
        else:
            return "所有工具执行完成"