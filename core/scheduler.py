import asyncio
import time
from typing import Dict, Any, List, Optional
from core.classifier import MultiDimensionalClassifier
from core.router import IntelligentRoutingEngine
from core.pipeline import AdvancedProcessingPipeline
from core.quality_controller import AdaptiveQualityController
from core.learning_system import DynamicLearningSystem
from utils.metrics import RealTimePerformanceMonitor
from data.data_structures import InteractionData, ProcessingResult


class UnifiedScheduler:
    def __init__(self):
        self.classifier = MultiDimensionalClassifier()
        self.routing_engine = IntelligentRoutingEngine()
        self.pipeline_executor = AdvancedProcessingPipeline()
        self.quality_controller = AdaptiveQualityController()
        self.learning_system = DynamicLearningSystem()
        self.performance_monitor = RealTimePerformanceMonitor()
        self.system_status = {
            'load_factor': 1.0,
            'available_models': ['qwen-turbo', 'qwen-plus', 'qwen-max'],
            'resource_usage': 0.5
        }

    async def initialize(self):
        await self.performance_monitor.start_monitoring()
        await self._load_learning_history()

    async def process_question(self, question: str, user_context: Dict[str, Any],
                               conversation_history: List[Dict[str, Any]]) -> ProcessingResult:
        start_time = time.time()

        try:
            classification = await self.classifier.classify_question(
                question, user_context, conversation_history
            )

            processing_route = await self.routing_engine.create_processing_pipeline(
                classification, self._get_system_status()
            )

            initial_result = await self.pipeline_executor.execute_pipeline(
                question, processing_route.__dict__, user_context
            )

            validation_result = await self.quality_controller.validate_response(
                question, initial_result.response, initial_result.__dict__
            )

            final_result = await self._handle_improvement_suggestions(
                initial_result, validation_result, processing_route.__dict__
            )

            interaction_data = self._create_interaction_data(
                question, classification, processing_route.__dict__, final_result,
                time.time() - start_time
            )

            await self.learning_system.learn_from_interaction(interaction_data)

            return final_result

        except Exception as e:
            return await self._handle_processing_error(question, e, user_context, time.time() - start_time)

    def _get_system_status(self) -> Dict[str, Any]:
        current_status = self.performance_monitor.get_current_status()
        self.system_status.update(current_status)
        return self.system_status

    async def _handle_improvement_suggestions(self, initial_result: ProcessingResult, validation_result,
                                              processing_route: Dict[str, Any]) -> ProcessingResult:
        improvement_action = validation_result.improvement_action

        if improvement_action['action'] == 'approve':
            initial_result.confidence = validation_result.confidence
            return initial_result

        elif improvement_action['action'] == 'enhance':
            enhanced_result = await self._enhance_response(initial_result, improvement_action['strategy'])
            enhanced_result.confidence = validation_result.confidence
            return enhanced_result

        elif improvement_action['action'] == 'improve':
            improved_result = await self._improve_response(initial_result, improvement_action['strategy'],
                                                           processing_route)
            return improved_result

        else:
            initial_result.confidence = validation_result.confidence
            return initial_result

    async def _enhance_response(self, result: ProcessingResult, strategy: str) -> ProcessingResult:
        if strategy == 'add_details':
            enhanced_response = f"{result.response}\n\n补充说明：这个回答基于当前可用的信息，如需更详细的内容，请提供更具体的问题。"
            result.response = enhanced_response

        return result

    async def _improve_response(self, result: ProcessingResult, strategy: Dict[str, str],
                                processing_route: Dict[str, Any]) -> ProcessingResult:
        improvement_route = processing_route.copy()

        if 'fact_verification' in strategy:
            improvement_route['stages'].append('additional_fact_check')

        if 'enhancement' in strategy:
            improvement_route['stages'].append('information_gathering')

        if 'reasoning' in strategy:
            improvement_route['model_preference'] = 'quality'

        try:
            improved_result = await self.pipeline_executor.execute_pipeline(
                result.original_question if hasattr(result, 'original_question') else "重新处理的问题",
                improvement_route,
                {}
            )
            return improved_result
        except Exception:
            return result

    async def _handle_processing_error(self, question: str, error: Exception, user_context: Dict[str, Any],
                                       processing_time: float) -> ProcessingResult:
        error_result = ProcessingResult()
        error_result.response = f"抱歉，处理您的问题时遇到了技术问题。错误信息：{str(error)[:100]}"
        error_result.success = False
        error_result.error = str(error)
        error_result.processing_time = processing_time
        error_result.confidence = 0.0

        await self._log_error(question, error, user_context)

        return error_result

    def _create_interaction_data(self, question: str, classification: Dict[str, Any], processing_route: Dict[str, Any],
                                 result: ProcessingResult, processing_time: float) -> InteractionData:
        interaction_data = InteractionData()
        interaction_data.question = question
        interaction_data.classification = classification
        interaction_data.processing_route = processing_route
        interaction_data.result = result
        interaction_data.total_processing_time = processing_time
        interaction_data.complexity_level = classification.get('complexity_level', 0)
        interaction_data.user_satisfaction_score = 0.8
        interaction_data.resource_consumption = self._calculate_resource_consumption(processing_route)
        interaction_data.cost_per_interaction = self._calculate_cost(processing_route, processing_time)
        interaction_data.error_count = 0 if result.success else 1
        interaction_data.total_steps = len(processing_route.get('stages', []))
        interaction_data.was_escalated = processing_route.get('escalated', False)

        return interaction_data

    def _calculate_resource_consumption(self, processing_route: Dict[str, Any]) -> float:
        base_consumption = len(processing_route.get('stages', [])) * 0.1
        if processing_route.get('parallel_execution', False):
            base_consumption *= 1.3
        return base_consumption

    def _calculate_cost(self, processing_route: Dict[str, Any], processing_time: float) -> float:
        model = processing_route.get('model_preference', 'qwen-turbo')
        cost_per_second = {
            'qwen-turbo': 0.001,
            'qwen-plus': 0.002,
            'qwen-max': 0.005
        }
        return cost_per_second.get(model, 0.001) * processing_time

    async def _load_learning_history(self):
        pass

    async def _log_error(self, question: str, error: Exception, user_context: Dict[str, Any]):
        pass

    async def shutdown(self):
        await self.performance_monitor.stop_monitoring()