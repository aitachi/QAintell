import re
import math
from typing import Dict, Any, List
import jieba
import jieba.posseg as pseg


class ComplexityAnalyzer:
    def __init__(self):
        self.complexity_keywords = {
            0: ['是什么', '什么是', '简单', '基本'],
            1: ['如何', '怎么', '方法', '步骤'],
            2: ['为什么', '原因', '解释', '说明'],
            3: ['分析', '比较', '评估', '讨论'],
            4: ['深入', '详细', '全面', '系统', '复杂'],
            5: ['研究', '理论', '模型', '框架', '架构']
        }

        self.technical_terms = [
            '算法', '数据结构', '机器学习', '深度学习', '神经网络',
            '分布式', '微服务', '架构', '系统设计', '优化',
            '量子', '区块链', '人工智能', '云计算', '大数据'
        ]

        self.reasoning_indicators = [
            '因此', '所以', '由于', '考虑到', '基于', '根据',
            '假设', '如果', '那么', '推导', '证明', '论证'
        ]

    async def analyze(self, question: str) -> int:
        features = {
            'lexical_complexity': self.calculate_lexical_complexity(question),
            'syntactic_complexity': self.calculate_syntactic_complexity(question),
            'semantic_complexity': self.calculate_semantic_complexity(question),
            'reasoning_depth': self.estimate_reasoning_depth(question),
            'knowledge_breadth': self.estimate_knowledge_breadth(question)
        }

        weights = [0.1, 0.2, 0.3, 0.25, 0.15]
        complexity_score = sum(features[k] * w for k, w in zip(features.keys(), weights))

        if complexity_score < 1.5:
            return 0
        elif complexity_score < 2.5:
            return 1
        elif complexity_score < 4.0:
            return 2
        elif complexity_score < 6.0:
            return 3
        elif complexity_score < 8.0:
            return 4
        else:
            return 5

    def calculate_lexical_complexity(self, question: str) -> float:
        words = jieba.lcut(question)
        word_count = len(words)

        if word_count <= 5:
            return 1.0
        elif word_count <= 10:
            return 2.0
        elif word_count <= 20:
            return 4.0
        else:
            return 6.0

    def calculate_syntactic_complexity(self, question: str) -> float:
        complexity_score = 0.0

        clauses = question.count('，') + question.count('；') + 1
        complexity_score += clauses * 0.5

        subordinate_markers = ['因为', '虽然', '如果', '当', '由于']
        subordinate_count = sum(1 for marker in subordinate_markers if marker in question)
        complexity_score += subordinate_count * 1.0

        question_markers = ['什么', '为什么', '如何', '哪个', '何时']
        question_count = sum(1 for marker in question_markers if marker in question)
        complexity_score += question_count * 0.3

        return min(complexity_score, 8.0)

    def calculate_semantic_complexity(self, question: str) -> float:
        complexity_score = 0.0

        technical_count = sum(1 for term in self.technical_terms if term in question)
        complexity_score += technical_count * 1.5

        abstract_concepts = ['概念', '理论', '模型', '框架', '思想', '原理']
        abstract_count = sum(1 for concept in abstract_concepts if concept in question)
        complexity_score += abstract_count * 1.0

        domain_specific = self._count_domain_specific_terms(question)
        complexity_score += domain_specific * 0.8

        return min(complexity_score, 10.0)

    def estimate_reasoning_depth(self, question: str) -> float:
        depth_score = 0.0

        causal_indicators = ['为什么', '原因', '导致', '影响', '结果']
        causal_count = sum(1 for indicator in causal_indicators if indicator in question)
        depth_score += causal_count * 1.0

        reasoning_count = sum(1 for indicator in self.reasoning_indicators if indicator in question)
        depth_score += reasoning_count * 0.8

        comparison_indicators = ['比较', '对比', '差异', '相同', '不同']
        comparison_count = sum(1 for indicator in comparison_indicators if indicator in question)
        depth_score += comparison_count * 1.2

        evaluation_indicators = ['评估', '判断', '分析', '优缺点', '利弊']
        evaluation_count = sum(1 for indicator in evaluation_indicators if indicator in question)
        depth_score += evaluation_count * 1.5

        return min(depth_score, 8.0)

    def estimate_knowledge_breadth(self, question: str) -> float:
        breadth_score = 0.0

        multi_domain_indicators = ['跨领域', '综合', '整体', '全面', '系统']
        multi_domain_count = sum(1 for indicator in multi_domain_indicators if indicator in question)
        breadth_score += multi_domain_count * 1.5

        interdisciplinary_terms = ['交叉', '融合', '结合', '应用于', '相关性']
        interdisciplinary_count = sum(1 for term in interdisciplinary_terms if term in question)
        breadth_score += interdisciplinary_count * 1.2

        scope_indicators = ['全球', '国际', '历史', '未来', '趋势']
        scope_count = sum(1 for indicator in scope_indicators if indicator in question)
        breadth_score += scope_count * 0.8

        return min(breadth_score, 6.0)

    def _count_domain_specific_terms(self, question: str) -> int:
        domain_terms = {
            'tech': ['编程', '代码', '软件', '硬件', '网络', '数据库'],
            'science': ['实验', '假设', '理论', '公式', '计算', '测量'],
            'business': ['市场', '营销', '管理', '战略', '投资', '财务'],
            'medicine': ['诊断', '治疗', '症状', '病理', '药物', '手术'],
            'law': ['法律', '法规', '条例', '判决', '诉讼', '合同']
        }

        count = 0
        for domain, terms in domain_terms.items():
            count += sum(1 for term in terms if term in question)

        return count