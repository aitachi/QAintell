import re
import asyncio
from typing import Dict, Any, List
from analyzers.complexity_analyzer import ComplexityAnalyzer
from analyzers.domain_analyzer import DomainAnalyzer
from analyzers.urgency_analyzer import UrgencyAnalyzer
from analyzers.tool_requirement_analyzer import ToolRequirementAnalyzer
from analyzers.freshness_analyzer import FreshnessAnalyzer
from analyzers.user_context_analyzer import UserContextAnalyzer


class MultiDimensionalClassifier:
    def __init__(self):
        self.dimension_analyzers = {
            'complexity': ComplexityAnalyzer(),
            'domain': DomainAnalyzer(),
            'urgency': UrgencyAnalyzer(),
            'tool_requirement': ToolRequirementAnalyzer(),
            'knowledge_freshness': FreshnessAnalyzer(),
            'user_context': UserContextAnalyzer()
        }

    async def classify_question(self, question: str, user_context: Dict[str, Any],
                                conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        analysis_result = {}

        analysis_result['complexity'] = await self.dimension_analyzers['complexity'].analyze(question)
        analysis_result['domain'] = await self.dimension_analyzers['domain'].analyze(question)
        analysis_result['urgency'] = await self.dimension_analyzers['urgency'].analyze(question)
        analysis_result['tool_needs'] = await self.dimension_analyzers['tool_requirement'].analyze(question)
        analysis_result['freshness_need'] = await self.dimension_analyzers['knowledge_freshness'].analyze(question)
        analysis_result['user_profile'] = await self.dimension_analyzers['user_context'].analyze(user_context,
                                                                                                 conversation_history)

        return self.synthesize_routing_decision(analysis_result)

    def synthesize_routing_decision(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        complexity = analysis_result['complexity']
        domain = analysis_result['domain']
        urgency = analysis_result['urgency']

        routing_decision = {
            'complexity_level': complexity,
            'domain_type': domain,
            'urgency_level': urgency,
            'requires_tools': analysis_result['tool_needs']['required'],
            'requires_fresh_data': analysis_result['freshness_need']['requires_fresh'],
            'user_expertise': analysis_result['user_profile']['expertise_level'],
            'recommended_strategy': self._determine_strategy(analysis_result)
        }

        return routing_decision

    def _determine_strategy(self, analysis_result: Dict[str, Any]) -> str:
        complexity = analysis_result['complexity']
        urgency = analysis_result['urgency']

        if urgency == 'high' and complexity <= 2:
            return 'fast_track'
        elif complexity >= 4:
            return 'comprehensive'
        elif analysis_result['tool_needs']['required']:
            return 'tool_assisted'
        else:
            return 'standard'