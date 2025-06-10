import asyncio
from typing import Dict, Any, List
from utils.metrics import PerformanceTracker
from data.data_structures import InteractionData, LearningPattern


class DynamicLearningSystem:
    def __init__(self):
        self.performance_tracker = PerformanceTracker()
        self.user_feedback_collector = UserFeedbackCollector()
        self.pattern_learner = PatternLearner()
        self.strategy_optimizer = StrategyOptimizer()
        self.learning_data = []

    async def learn_from_interaction(self, interaction_data: InteractionData):
        performance_metrics = self._extract_performance_metrics(interaction_data)
        await self.performance_tracker.record(performance_metrics)

        feedback_analysis = await self.user_feedback_collector.analyze_feedback(
            interaction_data.user_feedback
        )

        patterns = await self.pattern_learner.extract_patterns(
            interaction_data, performance_metrics, feedback_analysis
        )

        strategy_updates = await self.strategy_optimizer.optimize_strategies(patterns)

        await self._apply_strategy_updates(strategy_updates)

        self.learning_data.append({
            'interaction': interaction_data,
            'patterns': patterns,
            'updates': strategy_updates
        })

    def _extract_performance_metrics(self, interaction_data: InteractionData) -> Dict[str, float]:
        return {
            'response_time': interaction_data.total_processing_time,
            'accuracy_score': interaction_data.validation_result.overall_score if interaction_data.validation_result else 0.5,
            'user_satisfaction': interaction_data.user_satisfaction_score,
            'resource_usage': interaction_data.resource_consumption,
            'cost_efficiency': interaction_data.cost_per_interaction,
            'error_rate': interaction_data.error_count / max(interaction_data.total_steps, 1),
            'escalation_rate': 1.0 if interaction_data.was_escalated else 0.0
        }

    async def optimize_classification_thresholds(self, historical_data: List[InteractionData]) -> Dict[
        int, Dict[str, Any]]:
        optimization_result = {}

        for level in range(6):
            level_data = [data for data in historical_data if data.complexity_level == level]

            if not level_data:
                continue

            current_performance = self._analyze_level_performance(level_data)
            optimal_thresholds = await self._find_optimal_thresholds(level, level_data)

            optimization_result[level] = {
                'current_performance': current_performance,
                'optimal_thresholds': optimal_thresholds,
                'improvement_potential': self._calculate_improvement_potential(
                    current_performance, optimal_thresholds
                )
            }

        return optimization_result

    def _analyze_level_performance(self, level_data: List[InteractionData]) -> Dict[str, float]:
        if not level_data:
            return {'accuracy': 0.0, 'speed': 0.0, 'satisfaction': 0.0}

        total_accuracy = sum(
            data.validation_result.overall_score if data.validation_result else 0.5 for data in level_data)
        total_speed = sum(1.0 / max(data.total_processing_time, 0.1) for data in level_data)
        total_satisfaction = sum(data.user_satisfaction_score for data in level_data)

        count = len(level_data)

        return {
            'accuracy': total_accuracy / count,
            'speed': total_speed / count,
            'satisfaction': total_satisfaction / count
        }

    async def _find_optimal_thresholds(self, level: int, level_data: List[InteractionData]) -> Dict[str, float]:
        return {
            'complexity_threshold': 0.5 + level * 0.1,
            'quality_threshold': 0.7 + level * 0.05,
            'time_threshold': 5.0 + level * 3.0
        }

    def _calculate_improvement_potential(self, current: Dict[str, float], optimal: Dict[str, float]) -> float:
        improvements = []
        for metric in ['accuracy', 'speed', 'satisfaction']:
            if metric in current and metric in optimal:
                improvement = optimal[metric] - current[metric]
                improvements.append(max(0, improvement))

        return sum(improvements) / len(improvements) if improvements else 0.0

    async def _apply_strategy_updates(self, strategy_updates: Dict[str, Any]):
        for strategy_type, updates in strategy_updates.items():
            if strategy_type == 'classification_thresholds':
                await self._update_classification_thresholds(updates)
            elif strategy_type == 'routing_rules':
                await self._update_routing_rules(updates)
            elif strategy_type == 'model_selection':
                await self._update_model_selection(updates)

    async def _update_classification_thresholds(self, updates: Dict[str, float]):
        pass

    async def _update_routing_rules(self, updates: Dict[str, Any]):
        pass

    async def _update_model_selection(self, updates: Dict[str, Any]):
        pass


class UserFeedbackCollector:
    async def analyze_feedback(self, feedback: Dict[str, Any]) -> Dict[str, float]:
        if not feedback:
            return {'satisfaction': 0.5, 'relevance': 0.5, 'completeness': 0.5}

        analysis = {
            'satisfaction': feedback.get('rating', 3) / 5.0,
            'relevance': self._analyze_relevance(feedback.get('comments', '')),
            'completeness': self._analyze_completeness(feedback.get('comments', ''))
        }

        return analysis

    def _analyze_relevance(self, comments: str) -> float:
        positive_words = ['相关', '准确', '正确', '有用']
        negative_words = ['无关', '错误', '不准确', '没用']

        positive_count = sum(1 for word in positive_words if word in comments)
        negative_count = sum(1 for word in negative_words if word in comments)

        if positive_count + negative_count == 0:
            return 0.7

        return positive_count / (positive_count + negative_count)

    def _analyze_completeness(self, comments: str) -> float:
        complete_words = ['完整', '详细', '全面', '充分']
        incomplete_words = ['不完整', '简单', '不够', '缺少']

        complete_count = sum(1 for word in complete_words if word in comments)
        incomplete_count = sum(1 for word in incomplete_words if word in comments)

        if complete_count + incomplete_count == 0:
            return 0.7

        return complete_count / (complete_count + incomplete_count)


class PatternLearner:
    async def extract_patterns(self, interaction_data: InteractionData, performance_metrics: Dict[str, float],
                               feedback_analysis: Dict[str, float]) -> List[LearningPattern]:
        patterns = []

        question_pattern = self._extract_question_pattern(interaction_data.question)
        performance_pattern = self._extract_performance_pattern(performance_metrics)
        feedback_pattern = self._extract_feedback_pattern(feedback_analysis)

        patterns.append(LearningPattern('question_type', question_pattern))
        patterns.append(LearningPattern('performance', performance_pattern))
        patterns.append(LearningPattern('feedback', feedback_pattern))

        return patterns

    def _extract_question_pattern(self, question: str) -> Dict[str, Any]:
        return {
            'length': len(question),
            'word_count': len(question.split()),
            'question_type': self._classify_question_type(question),
            'complexity_indicators': self._count_complexity_indicators(question)
        }

    def _extract_performance_pattern(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        return {
            'high_performance': metrics.get('accuracy_score', 0) > 0.8,
            'fast_response': metrics.get('response_time', 10) < 5.0,
            'efficient': metrics.get('resource_usage', 1.0) < 0.8
        }

    def _extract_feedback_pattern(self, feedback: Dict[str, float]) -> Dict[str, Any]:
        return {
            'positive_feedback': feedback.get('satisfaction', 0.5) > 0.7,
            'relevant_response': feedback.get('relevance', 0.5) > 0.7,
            'complete_response': feedback.get('completeness', 0.5) > 0.7
        }

    def _classify_question_type(self, question: str) -> str:
        if any(word in question for word in ['什么', '是什么']):
            return 'definition'
        elif any(word in question for word in ['为什么', '原因']):
            return 'explanation'
        elif any(word in question for word in ['如何', '怎样']):
            return 'procedure'
        else:
            return 'general'

    def _count_complexity_indicators(self, question: str) -> int:
        indicators = ['复杂', '详细', '全面', '深入', '比较', '分析']
        return sum(1 for indicator in indicators if indicator in question)


class StrategyOptimizer:
    async def optimize_strategies(self, patterns: List[LearningPattern]) -> Dict[str, Any]:
        optimizations = {}

        question_patterns = [p for p in patterns if p.pattern_type == 'question_type']
        performance_patterns = [p for p in patterns if p.pattern_type == 'performance']
        feedback_patterns = [p for p in patterns if p.pattern_type == 'feedback']

        if question_patterns:
            optimizations['classification_thresholds'] = await self._optimize_classification(question_patterns)

        if performance_patterns:
            optimizations['routing_rules'] = await self._optimize_routing(performance_patterns)

        if feedback_patterns:
            optimizations['model_selection'] = await self._optimize_model_selection(feedback_patterns)

        return optimizations

    async def _optimize_classification(self, patterns: List[LearningPattern]) -> Dict[str, float]:
        return {
            'complexity_adjustment': 0.1,
            'domain_sensitivity': 0.05
        }

    async def _optimize_routing(self, patterns: List[LearningPattern]) -> Dict[str, Any]:
        return {
            'speed_weight_adjustment': 0.1,
            'quality_weight_adjustment': 0.05
        }

    async def _optimize_model_selection(self, patterns: List[LearningPattern]) -> Dict[str, Any]:
        return {
            'model_threshold_adjustment': 0.05,
            'ensemble_weight_adjustment': 0.1
        }