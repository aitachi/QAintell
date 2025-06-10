import re
from typing import Dict, Any, List


class ToolRequirementAnalyzer:
    def __init__(self):
        self.tool_indicators = {
            'search': {
                'keywords': [
                    '搜索', '查找', '寻找', '检索', '搜查', '搜集',
                    '最新', '近期', '最近', '当前', '现在的', '实时',
                    '新闻', '资讯', '信息', '数据', '报告', '统计',
                    '趋势', '发展', '动态', '状况', '情况'
                ],
                'tool_name': 'web_search',
                'priority': 'high'
            },
            'calculation': {
                'keywords': [
                    '计算', '算', '求', '公式', '方程', '等式',
                    '数学', '数字', '数值', '统计', '概率', '比例',
                    '百分比', '平均', '总和', '差值', '乘积', '除法',
                    '开方', '指数', '对数', '三角函数', '积分', '导数'
                ],
                'tool_name': 'calculator',
                'priority': 'high'
            },
            'knowledge_retrieval': {
                'keywords': [
                    '知识库', '文档', '资料', '参考', '引用', '来源',
                    '研究', '论文', '书籍', '文献', '报告', '手册',
                    '指南', '教程', '说明', '介绍', '解释', '定义',
                    '概念', '理论', '原理', '背景', '历史', '发展'
                ],
                'tool_name': 'rag_retrieval',
                'priority': 'high'
            },
            'translation': {
                'keywords': [
                    '翻译', '转换', '英文', '中文', '日文', '韩文',
                    '法文', '德文', '俄文', '西班牙文', '意大利文',
                    '翻译成', '用英语', '用中文', '怎么说', '如何表达',
                    'translate', 'English', 'Chinese', 'Japanese'
                ],
                'tool_name': 'translator',
                'priority': 'medium'
            },
            'image_analysis': {
                'keywords': [
                    '图片', '图像', '照片', '图表', '图形', '视觉',
                    '分析图片', '识别图像', '看图', '图像识别', '视觉分析',
                    '截图', '画面', '视频', '画像', '图解', '示意图'
                ],
                'tool_name': 'image_analyzer',
                'priority': 'medium'
            },
            'code_execution': {
                'keywords': [
                    '代码', '编程', '脚本', '程序', '执行', '运行',
                    'Python', 'JavaScript', 'Java', 'C++', 'SQL',
                    '算法', '函数', '方法', '类', '对象', '模块',
                    '调试', '测试', '编译', '部署', '开发'
                ],
                'tool_name': 'code_executor',
                'priority': 'medium'
            },
            'data_analysis': {
                'keywords': [
                    '数据分析', '数据处理', '统计分析', '可视化', '图表',
                    '数据挖掘', '机器学习', '预测', '建模', '回归',
                    'Excel', 'CSV', 'JSON', '数据库', '查询',
                    '清洗数据', '特征工程', '模型训练', '评估'
                ],
                'tool_name': 'data_analyzer',
                'priority': 'medium'
            },
            'scheduling': {
                'keywords': [
                    '日程', '安排', '计划', '时间表', '日历', '预约',
                    '会议', '任务', '提醒', '定时', '调度', '排期',
                    '时间管理', '进度', '截止日期', '里程碑'
                ],
                'tool_name': 'scheduler',
                'priority': 'low'
            },
            'file_operations': {
                'keywords': [
                    '文件', '下载', '上传', '保存', '读取', '写入',
                    '创建文件', '删除文件', '移动文件', '复制文件',
                    '文件夹', '目录', '路径', '格式转换', '压缩', '解压'
                ],
                'tool_name': 'file_manager',
                'priority': 'low'
            }
        }

        self.context_modifiers = {
            'real_time': {
                'keywords': ['实时', '当前', '现在', '立即', '最新'],
                'modifier': 'requires_fresh_data'
            },
            'historical': {
                'keywords': ['历史', '过去', '以前', '曾经', '之前'],
                'modifier': 'requires_historical_data'
            },
            'comparative': {
                'keywords': ['比较', '对比', '差异', '相同', '不同', '优劣'],
                'modifier': 'requires_multiple_sources'
            },
            'detailed': {
                'keywords': ['详细', '具体', '深入', '全面', '完整'],
                'modifier': 'requires_comprehensive_search'
            }
        }

        self.complexity_indicators = {
            'simple': {
                'keywords': ['简单', '基本', '入门', '初级'],
                'tool_complexity': 'low'
            },
            'intermediate': {
                'keywords': ['中级', '进阶', '深入', '详细'],
                'tool_complexity': 'medium'
            },
            'advanced': {
                'keywords': ['高级', '专业', '复杂', '系统', '架构'],
                'tool_complexity': 'high'
            }
        }

    async def analyze(self, question: str) -> Dict[str, Any]:
        required_tools = self._identify_required_tools(question)
        tool_priorities = self._calculate_tool_priorities(question, required_tools)
        context_modifiers = self._analyze_context_modifiers(question)
        complexity_level = self._analyze_tool_complexity(question)
        tool_chain = self._determine_tool_chain(required_tools, context_modifiers)

        return {
            'required': len(required_tools) > 0,
            'tools': required_tools,
            'priorities': tool_priorities,
            'context_modifiers': context_modifiers,
            'complexity_level': complexity_level,
            'tool_chain': tool_chain,
            'execution_strategy': self._determine_execution_strategy(required_tools, complexity_level)
        }

    def _identify_required_tools(self, question: str) -> List[Dict[str, Any]]:
        question_lower = question.lower()
        required_tools = []

        for tool_type, config in self.tool_indicators.items():
            tool_score = 0.0
            matched_keywords = []

            for keyword in config['keywords']:
                if keyword.lower() in question_lower:
                    tool_score += self._calculate_keyword_relevance(keyword, question)
                    matched_keywords.append(keyword)

            if tool_score > 0:
                required_tools.append({
                    'tool_type': tool_type,
                    'tool_name': config['tool_name'],
                    'score': tool_score,
                    'priority': config['priority'],
                    'matched_keywords': matched_keywords,
                    'confidence': min(tool_score / 5.0, 1.0)
                })

        required_tools.sort(key=lambda x: x['score'], reverse=True)
        return required_tools

    def _calculate_keyword_relevance(self, keyword: str, question: str) -> float:
        base_score = 1.0

        question_lower = question.lower()
        keyword_lower = keyword.lower()

        if question_lower.startswith(keyword_lower):
            base_score += 0.5

        if keyword_lower in question_lower:
            keyword_count = question_lower.count(keyword_lower)
            base_score += (keyword_count - 1) * 0.2

        question_length = len(question.split())
        if question_length <= 10:
            base_score += 0.3

        return base_score

    def _calculate_tool_priorities(self, question: str, required_tools: List[Dict[str, Any]]) -> Dict[str, str]:
        priorities = {}

        for tool in required_tools:
            base_priority = tool['priority']
            score = tool['score']

            if score >= 3.0 and base_priority == 'medium':
                priorities[tool['tool_name']] = 'high'
            elif score >= 2.0 and base_priority == 'low':
                priorities[tool['tool_name']] = 'medium'
            else:
                priorities[tool['tool_name']] = base_priority

        return priorities

    def _analyze_context_modifiers(self, question: str) -> List[str]:
        question_lower = question.lower()
        modifiers = []

        for modifier_type, config in self.context_modifiers.items():
            for keyword in config['keywords']:
                if keyword in question_lower:
                    modifiers.append(config['modifier'])
                    break

        return list(set(modifiers))

    def _analyze_tool_complexity(self, question: str) -> str:
        question_lower = question.lower()
        complexity_scores = {}

        for complexity_level, config in self.complexity_indicators.items():
            score = 0.0
            for keyword in config['keywords']:
                if keyword in question_lower:
                    score += 1.0
            complexity_scores[complexity_level] = score

        if complexity_scores['advanced'] > 0:
            return 'high'
        elif complexity_scores['intermediate'] > 0:
            return 'medium'
        elif complexity_scores['simple'] > 0:
            return 'low'
        else:
            question_length = len(question.split())
            if question_length >= 20:
                return 'high'
            elif question_length >= 10:
                return 'medium'
            else:
                return 'low'

    def _determine_tool_chain(self, required_tools: List[Dict[str, Any]],
                              context_modifiers: List[str]) -> Dict[str, Any]:
        if not required_tools:
            return {'type': 'none', 'sequence': []}

        if len(required_tools) == 1:
            return {
                'type': 'single',
                'sequence': [required_tools[0]['tool_name']],
                'execution': 'sequential'
            }

        high_priority_tools = [tool for tool in required_tools if tool['priority'] == 'high']

        if len(high_priority_tools) >= 2:
            if 'requires_multiple_sources' in context_modifiers:
                return {
                    'type': 'parallel',
                    'sequence': [tool['tool_name'] for tool in high_priority_tools],
                    'execution': 'parallel'
                }
            else:
                return {
                    'type': 'sequential',
                    'sequence': [tool['tool_name'] for tool in required_tools[:3]],
                    'execution': 'sequential'
                }

        tool_dependencies = self._analyze_tool_dependencies(required_tools)

        return {
            'type': 'complex',
            'sequence': self._optimize_tool_sequence(required_tools, tool_dependencies),
            'execution': 'mixed',
            'dependencies': tool_dependencies
        }

    def _analyze_tool_dependencies(self, required_tools: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        dependencies = {}
        tool_names = [tool['tool_name'] for tool in required_tools]

        dependency_rules = {
            'web_search': [],
            'rag_retrieval': [],
            'calculator': ['web_search', 'rag_retrieval'],
            'data_analyzer': ['web_search', 'rag_retrieval', 'file_manager'],
            'code_executor': ['rag_retrieval'],
            'translator': [],
            'image_analyzer': [],
            'scheduler': ['web_search'],
            'file_manager': []
        }

        for tool_name in tool_names:
            tool_deps = dependency_rules.get(tool_name, [])
            dependencies[tool_name] = [dep for dep in tool_deps if dep in tool_names]

        return dependencies

    def _optimize_tool_sequence(self, required_tools: List[Dict[str, Any]],
                                dependencies: Dict[str, List[str]]) -> List[str]:
        tools_by_priority = {
            'high': [tool['tool_name'] for tool in required_tools if tool['priority'] == 'high'],
            'medium': [tool['tool_name'] for tool in required_tools if tool['priority'] == 'medium'],
            'low': [tool['tool_name'] for tool in required_tools if tool['priority'] == 'low']
        }

        sequence = []
        processed = set()

        for priority in ['high', 'medium', 'low']:
            for tool_name in tools_by_priority[priority]:
                if tool_name not in processed:
                    deps = dependencies.get(tool_name, [])
                    for dep in deps:
                        if dep not in processed and dep in [t['tool_name'] for t in required_tools]:
                            sequence.append(dep)
                            processed.add(dep)

                    sequence.append(tool_name)
                    processed.add(tool_name)

        return sequence

    def _determine_execution_strategy(self, required_tools: List[Dict[str, Any]],
                                      complexity_level: str) -> Dict[str, Any]:
        if not required_tools:
            return {'strategy': 'none'}

        if len(required_tools) == 1:
            return {
                'strategy': 'single_tool',
                'timeout': self._calculate_timeout(required_tools[0], complexity_level),
                'retries': 2
            }

        if complexity_level == 'high' or len(required_tools) >= 3:
            return {
                'strategy': 'orchestrated',
                'timeout': 30.0,
                'parallel_limit': 2,
                'retries': 1,
                'fallback_enabled': True
            }

        return {
            'strategy': 'sequential',
            'timeout': 15.0,
            'retries': 2,
            'early_termination': True
        }

    def _calculate_timeout(self, tool: Dict[str, Any], complexity_level: str) -> float:
        base_timeouts = {
            'web_search': 10.0,
            'rag_retrieval': 5.0,
            'calculator': 2.0,
            'translator': 3.0,
            'image_analyzer': 8.0,
            'code_executor': 15.0,
            'data_analyzer': 20.0,
            'scheduler': 5.0,
            'file_manager': 3.0
        }

        base_timeout = base_timeouts.get(tool['tool_name'], 10.0)

        complexity_multipliers = {
            'low': 1.0,
            'medium': 1.5,
            'high': 2.0
        }

        multiplier = complexity_multipliers.get(complexity_level, 1.0)

        return base_timeout * multiplier