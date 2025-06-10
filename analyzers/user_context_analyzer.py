import re
from typing import Dict, Any, List
from datetime import datetime, timedelta


class UserContextAnalyzer:
    def __init__(self):
        self.expertise_indicators = {
            'beginner': {
                'keywords': [
                    '新手', '初学者', '入门', '基础', '简单', '容易',
                    '不懂', '不会', '学习', '开始', '如何', '什么是',
                    '初级', '零基础', '刚开始', '刚接触'
                ],
                'patterns': [
                    r'我是.*新手',
                    r'刚.*学',
                    r'不太.*懂',
                    r'完全.*不会'
                ]
            },
            'intermediate': {
                'keywords': [
                    '有一些', '了解一点', '中级', '进阶', '深入',
                    '更多', '详细', '具体', '比较', '优化',
                    '改进', '提升', '扩展', '应用'
                ],
                'patterns': [
                    r'有.*经验',
                    r'了解.*基础',
                    r'想要.*深入',
                    r'如何.*优化'
                ]
            },
            'advanced': {
                'keywords': [
                    '专业', '高级', '复杂', '系统', '架构', '设计',
                    '实现', '优化', '性能', '算法', '原理', '底层',
                    '源码', '核心', '深层', '机制', '框架'
                ],
                'patterns': [
                    r'深入.*原理',
                    r'底层.*实现',
                    r'架构.*设计',
                    r'性能.*优化'
                ]
            },
            'expert': {
                'keywords': [
                    '专家', '资深', '架构师', '技术负责人', 'CTO',
                    '研究', '论文', '理论', '创新', '突破', '前沿',
                    '行业', '标准', '规范', '最佳实践'
                ],
                'patterns': [
                    r'作为.*专家',
                    r'在.*领域.*年',
                    r'负责.*架构',
                    r'研究.*方向'
                ]
            }
        }

        self.learning_style_indicators = {
            'theoretical': {
                'keywords': [
                    '原理', '理论', '概念', '定义', '为什么', '机制',
                    '背景', '历史', '发展', '演进', '思想', '哲学'
                ]
            },
            'practical': {
                'keywords': [
                    '实际', '实践', '操作', '步骤', '如何做', '怎么办',
                    '例子', '示例', '案例', '应用', '使用', '工具'
                ]
            },
            'visual': {
                'keywords': [
                    '图', '图表', '示意图', '流程图', '架构图', '图片',
                    '可视化', '展示', '演示', '界面', '截图'
                ]
            },
            'systematic': {
                'keywords': [
                    '系统', '全面', '完整', '详细', '结构', '框架',
                    '体系', '整体', '综合', '总结', '梳理'
                ]
            }
        }

        self.urgency_preferences = {
            'immediate': {
                'keywords': ['立即', '马上', '现在', '紧急', '急需', '尽快']
            },
            'planned': {
                'keywords': ['计划', '安排', '准备', '学习', '研究', '了解']
            },
            'exploratory': {
                'keywords': ['探索', '发现', '了解', '看看', '研究', '调查']
            }
        }

        self.communication_preferences = {
            'concise': {
                'keywords': ['简单', '简洁', '简短', '直接', '要点', '总结']
            },
            'detailed': {
                'keywords': ['详细', '具体', '全面', '完整', '深入', '扩展']
            },
            'structured': {
                'keywords': ['结构', '条理', '步骤', '分类', '整理', '组织']
            }
        }

    async def analyze(self, user_context: Dict[str, Any], conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        current_question_analysis = self._analyze_current_question(user_context.get('current_question', ''))
        history_analysis = self._analyze_conversation_history(conversation_history)
        profile_analysis = self._analyze_user_profile(user_context)

        combined_analysis = self._combine_analyses(current_question_analysis, history_analysis, profile_analysis)

        return {
            'expertise_level': combined_analysis['expertise_level'],
            'learning_style': combined_analysis['learning_style'],
            'urgency_preference': combined_analysis['urgency_preference'],
            'communication_preference': combined_analysis['communication_preference'],
            'domain_experience': combined_analysis['domain_experience'],
            'interaction_patterns': combined_analysis['interaction_patterns'],
            'confidence': combined_analysis['confidence']
        }

    def _analyze_current_question(self, question: str) -> Dict[str, Any]:
        if not question:
            return self._get_default_analysis()

        question_lower = question.lower()

        expertise_scores = {}
        for level, config in self.expertise_indicators.items():
            score = 0.0

            for keyword in config['keywords']:
                if keyword in question_lower:
                    score += 1.0

            for pattern in config['patterns']:
                if re.search(pattern, question):
                    score += 2.0

            expertise_scores[level] = score

        expertise_level = max(expertise_scores.keys(), key=lambda k: expertise_scores[k]) if any(
            expertise_scores.values()) else 'intermediate'

        learning_style_scores = {}
        for style, config in self.learning_style_indicators.items():
            score = sum(1 for keyword in config['keywords'] if keyword in question_lower)
            learning_style_scores[style] = score

        learning_style = max(learning_style_scores.keys(), key=lambda k: learning_style_scores[k]) if any(
            learning_style_scores.values()) else 'practical'

        urgency_scores = {}
        for urgency, config in self.urgency_preferences.items():
            score = sum(1 for keyword in config['keywords'] if keyword in question_lower)
            urgency_scores[urgency] = score

        urgency_preference = max(urgency_scores.keys(), key=lambda k: urgency_scores[k]) if any(
            urgency_scores.values()) else 'planned'

        communication_scores = {}
        for comm_type, config in self.communication_preferences.items():
            score = sum(1 for keyword in config['keywords'] if keyword in question_lower)
            communication_scores[comm_type] = score

        communication_preference = max(communication_scores.keys(), key=lambda k: communication_scores[k]) if any(
            communication_scores.values()) else 'detailed'

        return {
            'expertise_level': expertise_level,
            'learning_style': learning_style,
            'urgency_preference': urgency_preference,
            'communication_preference': communication_preference,
            'expertise_scores': expertise_scores,
            'confidence': self._calculate_question_confidence(expertise_scores, learning_style_scores)
        }

    def _analyze_conversation_history(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not conversation_history:
            return self._get_default_history_analysis()

        recent_questions = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history

        expertise_progression = self._analyze_expertise_progression(recent_questions)
        topic_consistency = self._analyze_topic_consistency(recent_questions)
        question_complexity = self._analyze_question_complexity_trend(recent_questions)
        interaction_frequency = self._analyze_interaction_frequency(conversation_history)

        return {
            'expertise_progression': expertise_progression,
            'topic_consistency': topic_consistency,
            'question_complexity': question_complexity,
            'interaction_frequency': interaction_frequency,
            'session_length': len(conversation_history),
            'engagement_level': self._calculate_engagement_level(conversation_history)
        }

    def _analyze_user_profile(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        profile = user_context.get('profile', {})

        return {
            'declared_expertise': profile.get('expertise_level', 'unknown'),
            'preferred_domains': profile.get('domains', []),
            'learning_goals': profile.get('goals', []),
            'time_constraints': profile.get('time_constraints', 'flexible'),
            'previous_interactions': profile.get('interaction_count', 0),
            'feedback_history': profile.get('feedback_scores', [])
        }

    def _combine_analyses(self, current: Dict[str, Any], history: Dict[str, Any], profile: Dict[str, Any]) -> Dict[
        str, Any]:
        weights = {
            'current_question': 0.5,
            'conversation_history': 0.3,
            'user_profile': 0.2
        }

        expertise_mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}

        current_expertise = expertise_mapping.get(current['expertise_level'], 2)

        if history.get('expertise_progression'):
            history_expertise = expertise_mapping.get(history['expertise_progression']['current_level'], 2)
        else:
            history_expertise = current_expertise

        profile_expertise = expertise_mapping.get(profile.get('declared_expertise', 'intermediate'), 2)

        combined_expertise_score = (
                current_expertise * weights['current_question'] +
                history_expertise * weights['conversation_history'] +
                profile_expertise * weights['user_profile']
        )

        final_expertise_level = {1: 'beginner', 2: 'intermediate', 3: 'advanced', 4: 'expert'}[
            round(combined_expertise_score)]

        domain_experience = self._calculate_domain_experience(current, history, profile)
        interaction_patterns = self._analyze_interaction_patterns(history, profile)
        confidence = self._calculate_overall_confidence(current, history, profile)

        return {
            'expertise_level': final_expertise_level,
            'learning_style': current['learning_style'],
            'urgency_preference': current['urgency_preference'],
            'communication_preference': current['communication_preference'],
            'domain_experience': domain_experience,
            'interaction_patterns': interaction_patterns,
            'confidence': confidence
        }

    def _analyze_expertise_progression(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not questions:
            return {'trend': 'stable', 'current_level': 'intermediate'}

        complexity_scores = []
        for q in questions:
            question_text = q.get('question', '')
            complexity = self._calculate_question_complexity(question_text)
            complexity_scores.append(complexity)

        if len(complexity_scores) >= 3:
            recent_avg = sum(complexity_scores[-3:]) / 3
            early_avg = sum(complexity_scores[:3]) / min(3, len(complexity_scores))

            if recent_avg > early_avg + 0.3:
                trend = 'increasing'
            elif recent_avg < early_avg - 0.3:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        current_complexity = complexity_scores[-1] if complexity_scores else 0.5
        current_level = self._complexity_to_expertise(current_complexity)

        return {
            'trend': trend,
            'current_level': current_level,
            'complexity_scores': complexity_scores
        }

    def _analyze_topic_consistency(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not questions:
            return {'consistency': 'unknown', 'main_topics': []}

        topics = []
        for q in questions:
            question_text = q.get('question', '')
            question_topics = self._extract_topics(question_text)
            topics.extend(question_topics)

        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        if not topic_counts:
            return {'consistency': 'unknown', 'main_topics': []}

        total_topics = len(topics)
        main_topic_ratio = max(topic_counts.values()) / total_topics if total_topics > 0 else 0

        if main_topic_ratio >= 0.7:
            consistency = 'high'
        elif main_topic_ratio >= 0.4:
            consistency = 'medium'
        else:
            consistency = 'low'

        main_topics = sorted(topic_counts.keys(), key=lambda x: topic_counts[x], reverse=True)[:3]

        return {
            'consistency': consistency,
            'main_topics': main_topics,
            'topic_distribution': topic_counts
        }

    def _analyze_question_complexity_trend(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not questions:
            return {'trend': 'unknown', 'average_complexity': 0.5}

        complexities = [self._calculate_question_complexity(q.get('question', '')) for q in questions]
        average_complexity = sum(complexities) / len(complexities)

        if len(complexities) >= 3:
            recent_trend = complexities[-3:]
            if all(recent_trend[i] <= recent_trend[i + 1] for i in range(len(recent_trend) - 1)):
                trend = 'increasing'
            elif all(recent_trend[i] >= recent_trend[i + 1] for i in range(len(recent_trend) - 1)):
                trend = 'decreasing'
            else:
                trend = 'variable'
        else:
            trend = 'insufficient_data'

        return {
            'trend': trend,
            'average_complexity': average_complexity,
            'complexity_scores': complexities
        }

    def _analyze_interaction_frequency(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not conversation_history:
            return {'frequency': 'unknown', 'pattern': 'irregular'}

        timestamps = []
        for interaction in conversation_history:
            timestamp = interaction.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    timestamps.append(datetime.fromisoformat(timestamp))
                elif isinstance(timestamp, datetime):
                    timestamps.append(timestamp)

        if len(timestamps) < 2:
            return {'frequency': 'insufficient_data', 'pattern': 'unknown'}

        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i - 1]).total_seconds() / 3600  # hours
            intervals.append(interval)

        avg_interval = sum(intervals) / len(intervals)

        if avg_interval <= 1:
            frequency = 'very_high'
        elif avg_interval <= 24:
            frequency = 'high'
        elif avg_interval <= 168:  # 1 week
            frequency = 'medium'
        else:
            frequency = 'low'

        interval_variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)

        if interval_variance < avg_interval * 0.1:
            pattern = 'regular'
        else:
            pattern = 'irregular'

        return {
            'frequency': frequency,
            'pattern': pattern,
            'average_interval_hours': avg_interval,
            'total_interactions': len(conversation_history)
        }

    def _calculate_question_complexity(self, question: str) -> float:
        if not question:
            return 0.5

        complexity_factors = {
            'length': min(len(question.split()) / 20, 1.0) * 0.2,
            'technical_terms': self._count_technical_terms(question) / 5 * 0.3,
            'question_depth': self._analyze_question_depth(question) * 0.3,
            'specificity': self._analyze_specificity(question) * 0.2
        }

        return sum(complexity_factors.values())

    def _count_technical_terms(self, question: str) -> int:
        technical_terms = [
            '算法', '架构', '框架', '模式', '协议', '接口', '数据结构',
            '优化', '性能', '并发', '分布式', '微服务', '容器', '集群'
        ]
        return sum(1 for term in technical_terms if term in question.lower())

    def _analyze_question_depth(self, question: str) -> float:
        depth_indicators = ['为什么', '如何', '原理', '机制', '深入', '底层']
        depth_score = sum(1 for indicator in depth_indicators if indicator in question.lower())
        return min(depth_score / 3, 1.0)

    def _analyze_specificity(self, question: str) -> float:
        specific_indicators = ['具体', '详细', '准确', '精确', '特定', '明确']
        general_indicators = ['一般', '通常', '大概', '基本', '简单']

        specific_count = sum(1 for indicator in specific_indicators if indicator in question.lower())
        general_count = sum(1 for indicator in general_indicators if indicator in question.lower())

        if specific_count > general_count:
            return 0.8
        elif general_count > specific_count:
            return 0.3
        else:
            return 0.5

    def _extract_topics(self, question: str) -> List[str]:
        topic_keywords = {
            'programming': ['编程', '代码', '程序', '开发', '软件'],
            'data_science': ['数据', '分析', '机器学习', '算法', '模型'],
            'web': ['网站', '前端', '后端', '服务器', 'API'],
            'mobile': ['移动', '手机', 'app', '应用'],
            'database': ['数据库', 'SQL', '查询', '存储'],
            'network': ['网络', '协议', '通信', '连接'],
            'security': ['安全', '加密', '认证', '权限'],
            'business': ['商业', '管理', '市场', '销售']
        }

        found_topics = []
        question_lower = question.lower()

        for topic, keywords in topic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                found_topics.append(topic)

        return found_topics

    def _complexity_to_expertise(self, complexity: float) -> str:
        if complexity >= 0.8:
            return 'expert'
        elif complexity >= 0.6:
            return 'advanced'
        elif complexity >= 0.4:
            return 'intermediate'
        else:
            return 'beginner'

    def _calculate_domain_experience(self, current: Dict[str, Any], history: Dict[str, Any], profile: Dict[str, Any]) -> \
    Dict[str, str]:
        main_topics = history.get('topic_consistency', {}).get('main_topics', [])
        preferred_domains = profile.get('preferred_domains', [])

        domain_experience = {}

        for topic in main_topics[:3]:
            if topic in preferred_domains:
                domain_experience[topic] = 'high'
            else:
                domain_experience[topic] = 'medium'

        return domain_experience

    def _analyze_interaction_patterns(self, history: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'session_behavior': 'focused' if history.get('topic_consistency', {}).get(
                'consistency') == 'high' else 'exploratory',
            'learning_pace': 'fast' if history.get('interaction_frequency', {}).get('frequency') in ['high',
                                                                                                     'very_high'] else 'moderate',
            'engagement_depth': 'deep' if history.get('question_complexity', {}).get('average_complexity',
                                                                                     0) > 0.6 else 'surface'
        }

    def _calculate_engagement_level(self, conversation_history: List[Dict[str, Any]]) -> str:
        if len(conversation_history) >= 10:
            return 'high'
        elif len(conversation_history) >= 5:
            return 'medium'
        else:
            return 'low'

    def _calculate_question_confidence(self, expertise_scores: Dict[str, float],
                                       learning_style_scores: Dict[str, float]) -> float:
        expertise_confidence = 0.5 + min(max(expertise_scores.values()) * 0.1, 0.3) if expertise_scores else 0.5
        style_confidence = 0.5 + min(max(learning_style_scores.values()) * 0.1, 0.2) if learning_style_scores else 0.5

        return min((expertise_confidence + style_confidence) / 2, 1.0)

    def _calculate_overall_confidence(self, current: Dict[str, Any], history: Dict[str, Any],
                                      profile: Dict[str, Any]) -> float:
        current_confidence = current.get('confidence', 0.5)

        history_confidence = 0.5
        if history.get('session_length', 0) > 3:
            history_confidence += 0.2

        profile_confidence = 0.5
        if profile.get('previous_interactions', 0) > 0:
            profile_confidence += 0.2

        return min((current_confidence + history_confidence + profile_confidence) / 3, 1.0)

    def _get_default_analysis(self) -> Dict[str, Any]:
        return {
            'expertise_level': 'intermediate',
            'learning_style': 'practical',
            'urgency_preference': 'planned',
            'communication_preference': 'detailed',
            'expertise_scores': {},
            'confidence': 0.5
        }

    def _get_default_history_analysis(self) -> Dict[str, Any]:
        return {
            'expertise_progression': {'trend': 'stable', 'current_level': 'intermediate'},
            'topic_consistency': {'consistency': 'unknown', 'main_topics': []},
            'question_complexity': {'trend': 'unknown', 'average_complexity': 0.5},
            'interaction_frequency': {'frequency': 'unknown', 'pattern': 'irregular'},
            'session_length': 0,
            'engagement_level': 'low'
        }