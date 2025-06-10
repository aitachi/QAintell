import asyncio
from typing import Dict, Any, List, Tuple
from utils.metrics import PerformanceOptimizer, ResourceManager, QualityPredictor
from data.data_structures import ProcessingRoute, RouteEvaluation


class IntelligentRoutingEngine:
    def __init__(self):
        self.route_templates = self._initialize_route_templates()
        self.performance_optimizer = PerformanceOptimizer()
        self.resource_manager = ResourceManager()
        self.quality_predictor = QualityPredictor()

    def _initialize_route_templates(self) -> Dict[str, ProcessingRoute]:
        return {
            'fast_track': ProcessingRoute(
                stages=['preprocessing', 'simple_reasoning', 'basic_validation'],
                parallel_execution=False,
                timeout=5.0,
                model_preference='speed'
            ),
            'standard': ProcessingRoute(
                stages=['preprocessing', 'knowledge_retrieval', 'reasoning', 'validation'],
                parallel_execution=True,
                timeout=15.0,
                model_preference='balanced'
            ),
            'comprehensive': ProcessingRoute(
                stages=['preprocessing', 'multi_source_retrieval', 'tool_orchestration', 'advanced_reasoning',
                        'multi_stage_validation'],
                parallel_execution=True,
                timeout=30.0,
                model_preference='quality'
            ),
            'tool_assisted': ProcessingRoute(
                stages=['preprocessing', 'tool_planning', 'tool_execution', 'result_integration', 'validation'],
                parallel_execution=True,
                timeout=25.0,
                model_preference='balanced'
            )
        }

    async def create_processing_pipeline(self, classification_result: Dict[str, Any],
                                         system_status: Dict[str, Any]) -> ProcessingRoute:
        candidate_routes = self._generate_candidate_routes(classification_result)

        evaluated_routes = []
        for route in candidate_routes:
            evaluation = await self._evaluate_route(route, classification_result, system_status)
            evaluated_routes.append((route, evaluation))

        optimal_route = self._select_optimal_route(evaluated_routes)

        return self._build_processing_pipeline(optimal_route, classification_result)

    def _generate_candidate_routes(self, classification_result: Dict[str, Any]) -> List[ProcessingRoute]:
        routes = []

        strategy = classification_result['recommended_strategy']
        base_route = self.route_templates[strategy].copy()
        routes.append(base_route)

        urgency = classification_result['urgency_level']
        if urgency == 'high':
            speed_route = self._create_speed_optimized_route(base_route)
            routes.append(speed_route)

        domain = classification_result['domain_type']
        if domain in ['professional', 'academic', 'technical']:
            quality_route = self._create_quality_optimized_route(base_route)
            routes.append(quality_route)

        if self.resource_manager.is_high_load():
            efficient_route = self._create_resource_efficient_route(base_route)
            routes.append(efficient_route)

        return routes

    async def _evaluate_route(self, route: ProcessingRoute, classification_result: Dict[str, Any],
                              system_status: Dict[str, Any]) -> RouteEvaluation:
        evaluation = RouteEvaluation()

        evaluation.predicted_quality = await self.quality_predictor.predict_quality(route, classification_result)
        evaluation.estimated_time = self._estimate_processing_time(route, system_status)
        evaluation.resource_cost = self._calculate_resource_cost(route, system_status)
        evaluation.risk_assessment = self._assess_risk(route, classification_result)
        evaluation.user_satisfaction_prediction = self._predict_user_satisfaction(route, classification_result)

        evaluation.overall_score = self._calculate_overall_score(evaluation, classification_result)

        return evaluation

    def _select_optimal_route(self, evaluated_routes: List[Tuple[ProcessingRoute, RouteEvaluation]]) -> ProcessingRoute:
        best_route = None
        best_score = -1

        for route, evaluation in evaluated_routes:
            if evaluation.overall_score > best_score:
                best_score = evaluation.overall_score
                best_route = route

        return best_route

    def _build_processing_pipeline(self, route: ProcessingRoute,
                                   classification_result: Dict[str, Any]) -> ProcessingRoute:
        route.add_context('classification_result', classification_result)
        route.add_context('selected_model', self._select_model(route, classification_result))
        route.add_context('resource_allocation', self._allocate_resources(route))

        return route

    def _create_speed_optimized_route(self, base_route: ProcessingRoute) -> ProcessingRoute:
        speed_route = base_route.copy()
        speed_route.timeout = min(speed_route.timeout, 10.0)
        speed_route.model_preference = 'speed'
        speed_route.remove_stage('multi_stage_validation')
        return speed_route

    def _create_quality_optimized_route(self, base_route: ProcessingRoute) -> ProcessingRoute:
        quality_route = base_route.copy()
        quality_route.model_preference = 'quality'
        quality_route.add_stage('fact_checking')
        quality_route.add_stage('expert_validation')
        return quality_route

    def _create_resource_efficient_route(self, base_route: ProcessingRoute) -> ProcessingRoute:
        efficient_route = base_route.copy()
        efficient_route.parallel_execution = False
        efficient_route.model_preference = 'speed'
        efficient_route.remove_stage('multi_source_retrieval')
        return efficient_route

    def _estimate_processing_time(self, route: ProcessingRoute, system_status: Dict[str, Any]) -> float:
        base_time = len(route.stages) * 2.0
        load_factor = system_status.get('load_factor', 1.0)
        return base_time * load_factor

    def _calculate_resource_cost(self, route: ProcessingRoute, system_status: Dict[str, Any]) -> float:
        base_cost = len(route.stages) * 0.1
        if route.parallel_execution:
            base_cost *= 1.5
        return base_cost

    def _assess_risk(self, route: ProcessingRoute, classification_result: Dict[str, Any]) -> float:
        risk_score = 0.0
        if route.timeout < 10.0:
            risk_score += 0.2
        if classification_result['complexity_level'] > 3 and route.model_preference == 'speed':
            risk_score += 0.3
        return min(risk_score, 1.0)

    def _predict_user_satisfaction(self, route: ProcessingRoute, classification_result: Dict[str, Any]) -> float:
        satisfaction = 0.8
        if route.model_preference == 'quality':
            satisfaction += 0.1
        if route.timeout <= classification_result.get('expected_time', 15.0):
            satisfaction += 0.1
        return min(satisfaction, 1.0)

    def _calculate_overall_score(self, evaluation: RouteEvaluation, classification_result: Dict[str, Any]) -> float:
        weights = {
            'quality': 0.3,
            'time': 0.25,
            'cost': 0.2,
            'risk': 0.1,
            'satisfaction': 0.15
        }

        score = (
                evaluation.predicted_quality * weights['quality'] +
                (1.0 - min(evaluation.estimated_time / 30.0, 1.0)) * weights['time'] +
                (1.0 - min(evaluation.resource_cost, 1.0)) * weights['cost'] +
                (1.0 - evaluation.risk_assessment) * weights['risk'] +
                evaluation.user_satisfaction_prediction * weights['satisfaction']
        )

        return score

    def _select_model(self, route: ProcessingRoute, classification_result: Dict[str, Any]) -> str:
        complexity = classification_result['complexity_level']
        preference = route.model_preference

        if preference == 'speed':
            return 'qwen-turbo'
        elif preference == 'quality':
            return 'qwen-max'
        else:
            if complexity <= 2:
                return 'qwen-turbo'
            elif complexity <= 4:
                return 'qwen-plus'
            else:
                return 'qwen-max'

    def _allocate_resources(self, route: ProcessingRoute) -> Dict[str, Any]:
        return {
            'cpu_cores': 2 if route.parallel_execution else 1,
            'memory_mb': len(route.stages) * 512,
            'timeout': route.timeout
        }