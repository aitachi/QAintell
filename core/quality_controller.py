import asyncio
from typing import Dict, Any, List
from data.data_structures import ValidationResult


class AdaptiveQualityController:
    def __init__(self):
        self.quality_metrics = QualityMetrics()
        self.confidence_calculator = ConfidenceCalculator()
        self.fact_checker = FactChecker()
        self.consistency_verifier = ConsistencyVerifier()
        self.completeness_assessor = CompletenessAssessor()

    async def validate_response(self, question: str, response: str,
                                processing_context: Dict[str, Any]) -> ValidationResult:
        validation_result = ValidationResult()

        basic_quality = await self._check_basic_quality(response)
        validation_result.add_check('basic_quality', basic_quality)

        if processing_context.get('requires_fact_checking', False):
            fact_accuracy = await self.fact_checker.verify_facts(response,
                                                                 processing_context.get('knowledge_sources', []))
            validation_result.add_check('fact_accuracy', fact_accuracy)

        consistency = await self.consistency_verifier.check_consistency(
            response,
            processing_context.get('retrieved_knowledge', {}),
            processing_context.get('tool_results', {})
        )
        validation_result.add_check('consistency', consistency)

        completeness = await self.completeness_assessor.assess_completeness(question, response)
        validation_result.add_check('completeness', completeness)

        confidence = await self.confidence_calculator.calculate_confidence(
            response, processing_context, validation_result
        )
        validation_result.set_confidence(confidence)

        improvement_decision = await self._decide_improvement_action(validation_result, processing_context)
        validation_result.set_improvement_action(improvement_decision)

        return validation_result

    async def _check_basic_quality(self, response: str) -> float:
        if not response or len(response.strip()) < 10:
            return 0.0

        quality_score = 0.0

        if len(response) >= 50:
            quality_score += 0.3

        sentences = response.split('。')
        if len(sentences) >= 2:
            quality_score += 0.3

        if any(char.isdigit() for char in response):
            quality_score += 0.2

        if '因为' in response or '由于' in response or '所以' in response:
            quality_score += 0.2

        return min(quality_score, 1.0)

    async def _decide_improvement_action(self, validation_result: ValidationResult,
                                         processing_context: Dict[str, Any]) -> Dict[str, Any]:
        overall_score = validation_result.get_overall_score()
        confidence = validation_result.confidence

        if overall_score < 0.6 or confidence < 0.7:
            return await self._plan_improvement_strategy(validation_result, processing_context)
        elif overall_score < 0.8 and processing_context.get('allows_enhancement', True):
            return {'action': 'enhance', 'strategy': 'add_details'}
        else:
            return {'action': 'approve', 'strategy': None}

    async def _plan_improvement_strategy(self, validation_result: ValidationResult,
                                         processing_context: Dict[str, Any]) -> Dict[str, Any]:
        weak_aspects = validation_result.get_weak_aspects()
        improvement_strategy = {}

        if 'fact_accuracy' in weak_aspects:
            improvement_strategy['fact_verification'] = 'use_additional_sources'

        if 'completeness' in weak_aspects:
            improvement_strategy['enhancement'] = 'gather_more_information'

        if 'consistency' in weak_aspects:
            improvement_strategy['reasoning'] = 'use_stronger_model'

        return {
            'action': 'improve',
            'strategy': improvement_strategy,
            'escalation_level': self._calculate_escalation_level(weak_aspects)
        }

    def _calculate_escalation_level(self, weak_aspects: List[str]) -> int:
        if len(weak_aspects) >= 3:
            return 3
        elif len(weak_aspects) == 2:
            return 2
        else:
            return 1


class QualityMetrics:
    def calculate_readability(self, text: str) -> float:
        sentences = len(text.split('。'))
        words = len(text.split())
        if sentences == 0:
            return 0.0
        avg_sentence_length = words / sentences
        return max(0, 1.0 - (avg_sentence_length - 15) / 30)

    def calculate_informativeness(self, text: str) -> float:
        info_keywords = ['因为', '由于', '所以', '因此', '根据', '基于', '数据', '研究', '分析']
        keyword_count = sum(1 for keyword in info_keywords if keyword in text)
        return min(keyword_count / 5, 1.0)


class ConfidenceCalculator:
    async def calculate_confidence(self, response: str, processing_context: Dict[str, Any],
                                   validation_result: ValidationResult) -> float:
        base_confidence = 0.5

        if validation_result.get_check_result('basic_quality', 0) > 0.7:
            base_confidence += 0.2

        if processing_context.get('knowledge_sources'):
            base_confidence += 0.15

        if processing_context.get('tool_results'):
            base_confidence += 0.1

        validation_score = validation_result.get_overall_score()
        final_confidence = base_confidence * validation_score

        return min(final_confidence, 1.0)


class FactChecker:
    async def verify_facts(self, response: str, knowledge_sources: List[Dict[str, Any]]) -> float:
        if not knowledge_sources:
            return 0.5

        fact_statements = self._extract_fact_statements(response)
        verified_count = 0

        for statement in fact_statements:
            if await self._verify_statement(statement, knowledge_sources):
                verified_count += 1

        if not fact_statements:
            return 0.8

        return verified_count / len(fact_statements)

    def _extract_fact_statements(self, response: str) -> List[str]:
        sentences = response.split('。')
        fact_statements = []

        for sentence in sentences:
            if any(indicator in sentence for indicator in ['是', '为', '有', '达到', '约']):
                fact_statements.append(sentence.strip())

        return fact_statements

    async def _verify_statement(self, statement: str, knowledge_sources: List[Dict[str, Any]]) -> bool:
        for source in knowledge_sources:
            if any(word in source.get('content', '') for word in statement.split()[:3]):
                return True
        return False


class ConsistencyVerifier:
    async def check_consistency(self, response: str, retrieved_knowledge: Dict[str, Any],
                                tool_results: Dict[str, Any]) -> float:
        consistency_score = 1.0

        if retrieved_knowledge:
            knowledge_consistency = await self._check_knowledge_consistency(response, retrieved_knowledge)
            consistency_score = min(consistency_score, knowledge_consistency)

        if tool_results:
            tool_consistency = await self._check_tool_consistency(response, tool_results)
            consistency_score = min(consistency_score, tool_consistency)

        return consistency_score

    async def _check_knowledge_consistency(self, response: str, knowledge: Dict[str, Any]) -> float:
        return 0.85

    async def _check_tool_consistency(self, response: str, tool_results: Dict[str, Any]) -> float:
        return 0.9


class CompletenessAssessor:
    async def assess_completeness(self, question: str, response: str) -> float:
        question_aspects = self._analyze_question_aspects(question)
        covered_aspects = self._analyze_covered_aspects(response, question_aspects)

        if not question_aspects:
            return 0.8

        return len(covered_aspects) / len(question_aspects)

    def _analyze_question_aspects(self, question: str) -> List[str]:
        aspects = []

        if '什么' in question or '是什么' in question:
            aspects.append('definition')
        if '为什么' in question or '原因' in question:
            aspects.append('reason')
        if '如何' in question or '怎样' in question:
            aspects.append('method')
        if '何时' in question or '什么时候' in question:
            aspects.append('time')
        if '哪里' in question or '在哪' in question:
            aspects.append('location')

        return aspects if aspects else ['general']

    def _analyze_covered_aspects(self, response: str, question_aspects: List[str]) -> List[str]:
        covered = []

        for aspect in question_aspects:
            if aspect == 'definition' and ('是' in response or '指' in response):
                covered.append(aspect)
            elif aspect == 'reason' and ('因为' in response or '由于' in response):
                covered.append(aspect)
            elif aspect == 'method' and ('通过' in response or '方法' in response):
                covered.append(aspect)
            elif aspect == 'time' and any(time_word in response for time_word in ['时', '年', '月', '日']):
                covered.append(aspect)
            elif aspect == 'location' and ('在' in response or '位于' in response):
                covered.append(aspect)
            elif aspect == 'general':
                covered.append(aspect)

        return covered