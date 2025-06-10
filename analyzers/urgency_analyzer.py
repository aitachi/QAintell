import re
from typing import Dict, Any, List
from datetime import datetime, timedelta


class UrgencyAnalyzer:
    def __init__(self):
        self.urgency_keywords = {
            'high': {
                'keywords': [
                    '紧急', '急需', '立即', '马上', '现在', '尽快',
                    '快速', '迅速', '即时', '实时', '当前', '正在',
                    '突发', '紧急情况', '危急', '严重', '重要', '关键',
                    '今天', '现在就', '必须', '务必', '刻不容缓'
                ],
                'weight': 1.0
            },
            'medium': {
                'keywords': [
                    '尽量', '希望', '最好', '应该', '建议', '推荐',
                    '明天', '这周', '近期', '最近', '不久', '很快',
                    '及时', '适时', '合适', '方便时', '有空时'
                ],
                'weight': 0.6
            },
            'low': {
                'keywords': [
                    '有时间', '方便的话', '可以的话', '随时', '闲暇',
                    '空闲', '未来', '以后', '将来', '长期', '计划',
                    '考虑', '思考', '了解', '学习', '研究', '探讨'
                ],
                'weight': 0.3
            }
        }

        self.time_indicators = {
            'immediate': [
                '现在', '立即', '马上', '当前', '此刻', '正在',
                '实时', '即时', '瞬间', '立刻'
            ],
            'today': [
                '今天', '今日', '当天', '本日', '今天内'
            ],
            'this_week': [
                '这周', '本周', '这星期', '本星期', '周内'
            ],
            'this_month': [
                '这个月', '本月', '月内', '这月'
            ],
            'future': [
                '以后', '将来', '未来', '长期', '远期'
            ]
        }

        self.action_urgency = {
            'critical': [
                '救命', '求救', '帮助', '解决', '修复', '处理',
                '停止', '阻止', '预防', '避免', '紧急处理'
            ],
            'important': [
                '完成', '实现', '达成', '执行', '操作', '运行',
                '开始', '启动', '进行', '继续', '推进'
            ],
            'routine': [
                '了解', '学习', '研究', '探索', '发现', '查看',
                '观察', '分析', '思考', '考虑', '讨论'
            ]
        }

    async def analyze(self, question: str) -> Dict[str, Any]:
        urgency_scores = self._calculate_urgency_scores(question)
        time_sensitivity = self._analyze_time_sensitivity(question)
        action_type = self._analyze_action_type(question)
        context_urgency = self._analyze_context_urgency(question)

        overall_urgency = self._calculate_overall_urgency(
            urgency_scores, time_sensitivity, action_type, context_urgency
        )

        return {
            'urgency_level': overall_urgency,
            'urgency_scores': urgency_scores,
            'time_sensitivity': time_sensitivity,
            'action_type': action_type,
            'context_urgency': context_urgency,
            'confidence': self._calculate_confidence(urgency_scores, time_sensitivity)
        }

    def _calculate_urgency_scores(self, question: str) -> Dict[str, float]:
        question_lower = question.lower()
        scores = {}

        for level, config in self.urgency_keywords.items():
            score = 0.0
            keywords = config['keywords']
            weight = config['weight']

            for keyword in keywords:
                if keyword in question_lower:
                    keyword_score = self._calculate_keyword_urgency_weight(keyword, question)
                    score += keyword_score * weight

            scores[level] = score

        return scores

    def _calculate_keyword_urgency_weight(self, keyword: str, question: str) -> float:
        base_weight = 1.0

        question_lower = question.lower()
        keyword_lower = keyword.lower()

        if question_lower.startswith(keyword_lower):
            base_weight += 0.5

        if '?' in question or '？' in question:
            if keyword_lower in ['现在', '立即', '马上']:
                base_weight += 0.3

        if '!' in question or '！' in question:
            base_weight += 0.4

        keyword_count = question_lower.count(keyword_lower)
        if keyword_count > 1:
            base_weight += (keyword_count - 1) * 0.2

        return base_weight

    def _analyze_time_sensitivity(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        time_scores = {}

        for time_frame, indicators in self.time_indicators.items():
            score = 0.0
            for indicator in indicators:
                if indicator in question_lower:
                    score += 1.0
            time_scores[time_frame] = score

        if any(score > 0 for score in time_scores.values()):
            dominant_time_frame = max(time_scores.keys(), key=lambda k: time_scores[k])
        else:
            dominant_time_frame = 'unspecified'

        urgency_mapping = {
            'immediate': 'high',
            'today': 'high',
            'this_week': 'medium',
            'this_month': 'medium',
            'future': 'low',
            'unspecified': 'medium'
        }

        return {
            'time_frame': dominant_time_frame,
            'time_scores': time_scores,
            'urgency_level': urgency_mapping.get(dominant_time_frame, 'medium')
        }

    def _analyze_action_type(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        action_scores = {}

        for action_level, actions in self.action_urgency.items():
            score = 0.0
            for action in actions:
                if action in question_lower:
                    score += 1.0
            action_scores[action_level] = score

        if any(score > 0 for score in action_scores.values()):
            dominant_action = max(action_scores.keys(), key=lambda k: action_scores[k])
        else:
            dominant_action = 'routine'

        urgency_mapping = {
            'critical': 'high',
            'important': 'medium',
            'routine': 'low'
        }

        return {
            'action_type': dominant_action,
            'action_scores': action_scores,
            'urgency_level': urgency_mapping.get(dominant_action, 'medium')
        }

    def _analyze_context_urgency(self, question: str) -> Dict[str, Any]:
        context_indicators = {
            'problem_solving': {
                'keywords': ['问题', '错误', '失败', '故障', '不工作', '无法', '无效'],
                'urgency': 'high'
            },
            'learning': {
                'keywords': ['学习', '了解', '知识', '教程', '指南', '原理'],
                'urgency': 'low'
            },
            'decision_making': {
                'keywords': ['选择', '决定', '比较', '评估', '建议', '推荐'],
                'urgency': 'medium'
            },
            'planning': {
                'keywords': ['计划', '准备', '安排', '设计', '规划', '策略'],
                'urgency': 'medium'
            }
        }

        question_lower = question.lower()
        context_scores = {}

        for context_type, config in context_indicators.items():
            score = 0.0
            for keyword in config['keywords']:
                if keyword in question_lower:
                    score += 1.0
            context_scores[context_type] = score

        if any(score > 0 for score in context_scores.values()):
            dominant_context = max(context_scores.keys(), key=lambda k: context_scores[k])
            urgency_level = context_indicators[dominant_context]['urgency']
        else:
            dominant_context = 'general'
            urgency_level = 'medium'

        return {
            'context_type': dominant_context,
            'context_scores': context_scores,
            'urgency_level': urgency_level
        }

    def _calculate_overall_urgency(self, urgency_scores: Dict[str, float],
                                   time_sensitivity: Dict[str, Any],
                                   action_type: Dict[str, Any],
                                   context_urgency: Dict[str, Any]) -> str:

        urgency_points = {
            'high': 3,
            'medium': 2,
            'low': 1
        }

        weights = {
            'keyword_urgency': 0.4,
            'time_sensitivity': 0.3,
            'action_type': 0.2,
            'context_urgency': 0.1
        }

        keyword_urgency_level = self._determine_keyword_urgency_level(urgency_scores)

        total_points = (
                urgency_points.get(keyword_urgency_level, 2) * weights['keyword_urgency'] +
                urgency_points.get(time_sensitivity['urgency_level'], 2) * weights['time_sensitivity'] +
                urgency_points.get(action_type['urgency_level'], 2) * weights['action_type'] +
                urgency_points.get(context_urgency['urgency_level'], 2) * weights['context_urgency']
        )

        if total_points >= 2.5:
            return 'high'
        elif total_points >= 1.5:
            return 'medium'
        else:
            return 'low'

    def _determine_keyword_urgency_level(self, urgency_scores: Dict[str, float]) -> str:
        if urgency_scores.get('high', 0) > 0:
            return 'high'
        elif urgency_scores.get('medium', 0) > urgency_scores.get('low', 0):
            return 'medium'
        else:
            return 'low'

    def _calculate_confidence(self, urgency_scores: Dict[str, float],
                              time_sensitivity: Dict[str, Any]) -> float:

        total_keyword_score = sum(urgency_scores.values())
        time_score = sum(time_sensitivity['time_scores'].values())

        confidence = 0.5

        if total_keyword_score > 0:
            confidence += min(total_keyword_score * 0.1, 0.3)

        if time_score > 0:
            confidence += min(time_score * 0.1, 0.2)

        return min(confidence, 1.0)