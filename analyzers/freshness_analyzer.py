import re
from typing import Dict, Any, List
from datetime import datetime, timedelta


class FreshnessAnalyzer:
    def __init__(self):
        self.temporal_keywords = {
            'real_time': {
                'keywords': [
                    '实时', '当前', '现在', '此刻', '目前', '正在',
                    '即时', '同步', '在线', '直播', 'live'
                ],
                'freshness_score': 1.0,
                'max_age_hours': 1
            },
            'recent': {
                'keywords': [
                    '最新', '最近', '近期', '新的', '新增', '刚刚',
                    '今天', '昨天', '这周', '本周', '这几天',
                    '最新消息', '最新动态', '最新进展'
                ],
                'freshness_score': 0.8,
                'max_age_hours': 24
            },
            'current': {
                'keywords': [
                    '当前', '现有', '目前', '现状', '状况', '情况',
                    '趋势', '发展', '变化', '更新', '改变'
                ],
                'freshness_score': 0.6,
                'max_age_hours': 168  # 1 week
            },
            'periodic': {
                'keywords': [
                    '定期', '每天', '每周', '每月', '每年', '周期性',
                    '更新', '发布', '报告', '统计', '数据'
                ],
                'freshness_score': 0.4,
                'max_age_hours': 720  # 1 month
            },
            'stable': {
                'keywords': [
                    '历史', '传统', '经典', '基础', '原理', '理论',
                    '定义', '概念', '常识', '知识', '学术', '研究'
                ],
                'freshness_score': 0.1,
                'max_age_hours': 8760  # 1 year
            }
        }

        self.domain_freshness_requirements = {
            'technology': {
                'base_freshness': 0.8,
                'keywords': [
                    '技术', '软件', '编程', '算法', '框架', '工具',
                    '更新', '版本', '发布', '特性', '功能'
                ]
            },
            'news': {
                'base_freshness': 1.0,
                'keywords': [
                    '新闻', '消息', '事件', '发生', '报道', '媒体',
                    '头条', '资讯', '动态', '进展'
                ]
            },
            'financial': {
                'base_freshness': 0.9,
                'keywords': [
                    '股价', '市场', '投资', '经济', '金融', '汇率',
                    '价格', '指数', '交易', '行情'
                ]
            },
            'science': {
                'base_freshness': 0.3,
                'keywords': [
                    '科学', '研究', '发现', '实验', '理论', '论文',
                    '学术', '期刊', '报告', '数据'
                ]
            },
            'weather': {
                'base_freshness': 1.0,
                'keywords': [
                    '天气', '气象', '温度', '降雨', '风速', '湿度',
                    '预报', '气候', '天气预报'
                ]
            },
            'general': {
                'base_freshness': 0.2,
                'keywords': []
            }
        }

        self.change_indicators = {
            'dynamic': [
                '变化', '改变', '更新', '修改', '调整', '发展',
                '进步', '进展', '演变', '转变', '升级', '优化'
            ],
            'static': [
                '不变', '固定', '稳定', '恒定', '永久', '持续',
                '一直', '始终', '长期', '传统', '经典', '基础'
            ]
        }

    async def analyze(self, question: str) -> Dict[str, Any]:
        temporal_analysis = self._analyze_temporal_keywords(question)
        domain_requirements = self._analyze_domain_freshness(question)
        change_analysis = self._analyze_change_indicators(question)
        urgency_impact = self._analyze_urgency_impact(question)

        freshness_requirement = self._calculate_freshness_requirement(
            temporal_analysis, domain_requirements, change_analysis, urgency_impact
        )

        return {
            'requires_fresh': freshness_requirement['requires_fresh'],
            'freshness_score': freshness_requirement['freshness_score'],
            'max_age_hours': freshness_requirement['max_age_hours'],
            'temporal_analysis': temporal_analysis,
            'domain_requirements': domain_requirements,
            'change_analysis': change_analysis,
            'confidence': self._calculate_confidence(temporal_analysis, domain_requirements)
        }

    def _analyze_temporal_keywords(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        temporal_scores = {}
        matched_keywords = {}

        for temporal_type, config in self.temporal_keywords.items():
            score = 0.0
            matched = []

            for keyword in config['keywords']:
                if keyword in question_lower:
                    keyword_weight = self._calculate_temporal_weight(keyword, question)
                    score += keyword_weight
                    matched.append(keyword)

            temporal_scores[temporal_type] = score
            matched_keywords[temporal_type] = matched

        dominant_temporal = max(temporal_scores.keys(), key=lambda k: temporal_scores[k]) if any(
            temporal_scores.values()) else 'stable'

        return {
            'dominant_temporal': dominant_temporal,
            'temporal_scores': temporal_scores,
            'matched_keywords': matched_keywords,
            'freshness_score': self.temporal_keywords[dominant_temporal]['freshness_score'],
            'max_age_hours': self.temporal_keywords[dominant_temporal]['max_age_hours']
        }

    def _calculate_temporal_weight(self, keyword: str, question: str) -> float:
        base_weight = 1.0
        question_lower = question.lower()

        if question_lower.startswith(keyword):
            base_weight += 0.5

        if keyword in ['实时', '当前', '现在', '最新']:
            base_weight += 0.3

        keyword_count = question_lower.count(keyword)
        if keyword_count > 1:
            base_weight += (keyword_count - 1) * 0.2

        return base_weight

    def _analyze_domain_freshness(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        domain_scores = {}

        for domain, config in self.domain_freshness_requirements.items():
            score = 0.0

            if config['keywords']:
                for keyword in config['keywords']:
                    if keyword in question_lower:
                        score += 1.0

            domain_scores[domain] = score

        if any(domain_scores.values()):
            identified_domain = max(domain_scores.keys(), key=lambda k: domain_scores[k])
        else:
            identified_domain = 'general'

        return {
            'identified_domain': identified_domain,
            'domain_scores': domain_scores,
            'base_freshness': self.domain_freshness_requirements[identified_domain]['base_freshness']
        }

    def _analyze_change_indicators(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()

        dynamic_score = sum(1 for indicator in self.change_indicators['dynamic'] if indicator in question_lower)
        static_score = sum(1 for indicator in self.change_indicators['static'] if indicator in question_lower)

        if dynamic_score > static_score:
            change_type = 'dynamic'
            freshness_modifier = 0.3
        elif static_score > dynamic_score:
            change_type = 'static'
            freshness_modifier = -0.3
        else:
            change_type = 'neutral'
            freshness_modifier = 0.0

        return {
            'change_type': change_type,
            'dynamic_score': dynamic_score,
            'static_score': static_score,
            'freshness_modifier': freshness_modifier
        }

    def _analyze_urgency_impact(self, question: str) -> float:
        urgency_keywords = ['紧急', '急需', '立即', '马上', '现在就', '尽快']
        question_lower = question.lower()

        urgency_count = sum(1 for keyword in urgency_keywords if keyword in question_lower)

        if urgency_count > 0:
            return 0.4
        elif '?' in question or '？' in question:
            return 0.1
        else:
            return 0.0

    def _calculate_freshness_requirement(self, temporal_analysis: Dict[str, Any],
                                         domain_requirements: Dict[str, Any],
                                         change_analysis: Dict[str, Any],
                                         urgency_impact: float) -> Dict[str, Any]:

        base_freshness = domain_requirements['base_freshness']
        temporal_freshness = temporal_analysis['freshness_score']
        change_modifier = change_analysis['freshness_modifier']

        final_freshness_score = min(
            base_freshness + temporal_freshness * 0.4 + change_modifier + urgency_impact,
            1.0
        )

        requires_fresh = final_freshness_score >= 0.5

        if requires_fresh:
            max_age_hours = temporal_analysis['max_age_hours']
        else:
            max_age_hours = 8760  # 1 year for non-fresh content

        if urgency_impact > 0.3:
            max_age_hours = min(max_age_hours, 1)
        elif final_freshness_score >= 0.8:
            max_age_hours = min(max_age_hours, 24)
        elif final_freshness_score >= 0.6:
            max_age_hours = min(max_age_hours, 168)

        return {
            'requires_fresh': requires_fresh,
            'freshness_score': final_freshness_score,
            'max_age_hours': max_age_hours
        }

    def _calculate_confidence(self, temporal_analysis: Dict[str, Any],
                              domain_requirements: Dict[str, Any]) -> float:
        confidence = 0.5

        temporal_score = sum(temporal_analysis['temporal_scores'].values())
        if temporal_score > 0:
            confidence += min(temporal_score * 0.1, 0.3)

        domain_score = sum(domain_requirements['domain_scores'].values())
        if domain_score > 0:
            confidence += min(domain_score * 0.1, 0.2)

        return min(confidence, 1.0)