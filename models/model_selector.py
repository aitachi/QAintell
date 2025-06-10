from typing import Dict, Any, List, Optional
from config.models_config import ModelsConfig


class ModelSelector:
    def __init__(self):
        self.models_config = ModelsConfig()
        self.performance_history = {}
        self.model_availability = {}
        self._initialize_availability()

    def _initialize_availability(self):
        for model_name in self.models_config.AVAILABLE_MODELS:
            self.model_availability[model_name] = True

    def select_best_model(self, question: str, available_models: List[str], preferences: Dict[str, Any] = None) -> str:
        if not available_models:
            return "qwen-turbo"

        if preferences is None:
            preferences = {"priority": "balanced"}

        complexity = self._estimate_complexity(question)
        priority = preferences.get("priority", "balanced")

        candidate_models = self._filter_available_models(available_models)
        scored_models = self._score_models(candidate_models, complexity, priority, preferences)

        if not scored_models:
            return available_models[0] if available_models else "qwen-turbo"

        best_model = max(scored_models.items(), key=lambda x: x[1])
        return best_model[0]

    def select_primary_model(self, question: str, available_models: List[str]) -> str:
        preferences = {"priority": "quality", "role": "primary"}
        return self.select_best_model(question, available_models, preferences)

    def select_secondary_model(self, question: str, available_models: List[str], primary_model: str = None) -> str:
        if primary_model and primary_model in available_models:
            available_models = [m for m in available_models if m != primary_model]

        preferences = {"priority": "speed", "role": "secondary"}
        return self.select_best_model(question, available_models, preferences)

    def select_ensemble_models(self, question: str, available_models: List[str], ensemble_size: int = 3) -> List[str]:
        if len(available_models) <= ensemble_size:
            return available_models

        complexity = self._estimate_complexity(question)
        selected_models = []
        remaining_models = available_models.copy()

        primary_model = self.select_primary_model(question, remaining_models)
        selected_models.append(primary_model)
        remaining_models.remove(primary_model)

        for i in range(min(ensemble_size - 1, len(remaining_models))):
            diverse_model = self._select_diverse_model(selected_models, remaining_models, complexity)
            selected_models.append(diverse_model)
            remaining_models.remove(diverse_model)

        return selected_models

    def get_model_recommendation(self, classification_result: Dict[str, Any],
                                 system_constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        complexity = classification_result.get('complexity_level', 2)
        domain = classification_result.get('domain_type', 'general')
        urgency = classification_result.get('urgency_level', 'medium')

        if system_constraints is None:
            system_constraints = {}

        max_cost = system_constraints.get('max_cost_per_token', float('inf'))
        max_time = system_constraints.get('max_response_time', 30.0)
        required_quality = system_constraints.get('min_quality_score', 6)

        suitable_models = self._get_suitable_models(complexity, domain, urgency)
        constrained_models = self._apply_constraints(suitable_models, max_cost, max_time, required_quality)

        if not constrained_models:
            constrained_models = ["qwen-turbo"]

        recommendation = {
            'primary_model': constrained_models[0],
            'alternative_models': constrained_models[1:3],
            'ensemble_recommended': len(constrained_models) >= 2 and complexity >= 3,
            'reasoning': self._generate_recommendation_reasoning(complexity, domain, urgency, constrained_models[0])
        }

        return recommendation

    def update_model_performance(self, model_name: str, performance_data: Dict[str, Any]):
        if model_name not in self.performance_history:
            self.performance_history[model_name] = {
                'response_times': [],
                'quality_scores': [],
                'success_rates': [],
                'total_requests': 0
            }

        history = self.performance_history[model_name]
        history['total_requests'] += 1

        if 'response_time' in performance_data:
            history['response_times'].append(performance_data['response_time'])
            if len(history['response_times']) > 100:
                history['response_times'] = history['response_times'][-100:]

        if 'quality_score' in performance_data:
            history['quality_scores'].append(performance_data['quality_score'])
            if len(history['quality_scores']) > 100:
                history['quality_scores'] = history['quality_scores'][-100:]

        if 'success' in performance_data:
            history['success_rates'].append(1.0 if performance_data['success'] else 0.0)
            if len(history['success_rates']) > 100:
                history['success_rates'] = history['success_rates'][-100:]

    def get_model_statistics(self, model_name: str) -> Dict[str, Any]:
        if model_name not in self.performance_history:
            return {
                'avg_response_time': 0.0,
                'avg_quality_score': 0.0,
                'success_rate': 1.0,
                'total_requests': 0,
                'available': self.model_availability.get(model_name, True)
            }

        history = self.performance_history[model_name]

        avg_response_time = sum(history['response_times']) / len(history['response_times']) if history[
            'response_times'] else 0.0
        avg_quality_score = sum(history['quality_scores']) / len(history['quality_scores']) if history[
            'quality_scores'] else 0.0
        success_rate = sum(history['success_rates']) / len(history['success_rates']) if history[
            'success_rates'] else 1.0

        return {
            'avg_response_time': avg_response_time,
            'avg_quality_score': avg_quality_score,
            'success_rate': success_rate,
            'total_requests': history['total_requests'],
            'available': self.model_availability.get(model_name, True)
        }

    def set_model_availability(self, model_name: str, available: bool):
        self.model_availability[model_name] = available

    def _estimate_complexity(self, question: str) -> int:
        length_score = min(len(question.split()) / 10, 2)

        technical_terms = ['算法', '架构', '系统', '优化', '分析', '设计', '实现']
        technical_score = sum(1 for term in technical_terms if term in question)

        depth_indicators = ['为什么', '如何实现', '原理', '机制', '深入']
        depth_score = sum(1 for indicator in depth_indicators if indicator in question)

        total_score = length_score + technical_score + depth_score

        if total_score >= 5:
            return 4
        elif total_score >= 3:
            return 3
        elif total_score >= 1:
            return 2
        else:
            return 1

    def _filter_available_models(self, models: List[str]) -> List[str]:
        return [model for model in models if self.model_availability.get(model, True)]

    def _score_models(self, models: List[str], complexity: int, priority: str, preferences: Dict[str, Any]) -> Dict[
        str, float]:
        scores = {}

        for model_name in models:
            if model_name not in self.models_config.AVAILABLE_MODELS:
                continue

            model_config = self.models_config.AVAILABLE_MODELS[model_name]

            complexity_fit = self._calculate_complexity_fit(complexity, model_config['suitable_complexity'])
            performance_score = self._calculate_performance_score(model_name)
            priority_score = self._calculate_priority_score(model_config, priority)

            weights = self._get_scoring_weights(priority, preferences)

            total_score = (
                    complexity_fit * weights['complexity'] +
                    performance_score * weights['performance'] +
                    priority_score * weights['priority']
            )

            scores[model_name] = total_score

        return scores

    def _calculate_complexity_fit(self, question_complexity: int, suitable_complexity: List[int]) -> float:
        if question_complexity in suitable_complexity:
            return 1.0

        distances = [abs(question_complexity - c) for c in suitable_complexity]
        min_distance = min(distances)

        return max(0, 1.0 - min_distance * 0.3)

    def _calculate_performance_score(self, model_name: str) -> float:
        stats = self.get_model_statistics(model_name)

        if not stats['available']:
            return 0.0

        if stats['total_requests'] == 0:
            return 0.8

        quality_score = stats['avg_quality_score'] / 10.0
        speed_score = max(0, 1.0 - stats['avg_response_time'] / 30.0)
        reliability_score = stats['success_rate']

        return (quality_score * 0.4 + speed_score * 0.3 + reliability_score * 0.3)

    def _calculate_priority_score(self, model_config: Dict[str, Any], priority: str) -> float:
        if priority == "speed":
            return model_config['speed_score'] / 10.0
        elif priority == "quality":
            return model_config['quality_score'] / 10.0
        elif priority == "cost":
            return max(0, 1.0 - model_config['cost_per_token'] * 1000)
        else:
            speed_norm = model_config['speed_score'] / 10.0
            quality_norm = model_config['quality_score'] / 10.0
            cost_norm = max(0, 1.0 - model_config['cost_per_token'] * 1000)

            return speed_norm * 0.3 + quality_norm * 0.5 + cost_norm * 0.2

    def _get_scoring_weights(self, priority: str, preferences: Dict[str, Any]) -> Dict[str, float]:
        role = preferences.get('role', 'primary')

        if priority == "speed":
            return {'complexity': 0.2, 'performance': 0.6, 'priority': 0.2}
        elif priority == "quality":
            return {'complexity': 0.3, 'performance': 0.4, 'priority': 0.3}
        elif role == "secondary":
            return {'complexity': 0.1, 'performance': 0.7, 'priority': 0.2}
        else:
            return {'complexity': 0.25, 'performance': 0.5, 'priority': 0.25}

    def _select_diverse_model(self, selected_models: List[str], remaining_models: List[str], complexity: int) -> str:
        if not remaining_models:
            return selected_models[0] if selected_models else "qwen-turbo"

        diversity_scores = {}

        for model in remaining_models:
            diversity_score = 0.0
            model_config = self.models_config.AVAILABLE_MODELS.get(model, {})

            for selected_model in selected_models:
                selected_config = self.models_config.AVAILABLE_MODELS.get(selected_model, {})

                speed_diff = abs(model_config.get('speed_score', 5) - selected_config.get('speed_score', 5))
                quality_diff = abs(model_config.get('quality_score', 5) - selected_config.get('quality_score', 5))

                diversity_score += (speed_diff + quality_diff) / 20.0

            complexity_fit = self._calculate_complexity_fit(complexity, model_config.get('suitable_complexity', [2]))

            diversity_scores[model] = diversity_score * 0.7 + complexity_fit * 0.3

        return max(diversity_scores.items(), key=lambda x: x[1])[0]

    def _get_suitable_models(self, complexity: int, domain: str, urgency: str) -> List[str]:
        suitable = []

        for model_name, config in self.models_config.AVAILABLE_MODELS.items():
            if complexity in config['suitable_complexity']:
                suitable.append(model_name)
            elif abs(complexity - max(config['suitable_complexity'])) <= 1:
                suitable.append(model_name)

        if urgency == "high":
            suitable.sort(key=lambda m: self.models_config.AVAILABLE_MODELS[m]['speed_score'], reverse=True)
        elif domain in ['professional', 'academic']:
            suitable.sort(key=lambda m: self.models_config.AVAILABLE_MODELS[m]['quality_score'], reverse=True)

        return suitable if suitable else list(self.models_config.AVAILABLE_MODELS.keys())

    def _apply_constraints(self, models: List[str], max_cost: float, max_time: float, min_quality: int) -> List[str]:
        constrained = []

        for model_name in models:
            if model_name not in self.models_config.AVAILABLE_MODELS:
                continue

            config = self.models_config.AVAILABLE_MODELS[model_name]
            stats = self.get_model_statistics(model_name)

            if config['cost_per_token'] <= max_cost:
                if stats['avg_response_time'] <= max_time or stats['total_requests'] == 0:
                    if config['quality_score'] >= min_quality:
                        constrained.append(model_name)

        return constrained

    def _generate_recommendation_reasoning(self, complexity: int, domain: str, urgency: str,
                                           recommended_model: str) -> str:
        reasoning_parts = []

        if complexity >= 4:
            reasoning_parts.append("问题复杂度较高，推荐使用高质量模型")
        elif complexity <= 1:
            reasoning_parts.append("问题相对简单，可以使用快速模型")

        if urgency == "high":
            reasoning_parts.append("需要快速响应，优先考虑速度")

        if domain in ['professional', 'academic']:
            reasoning_parts.append("专业领域问题，优先考虑准确性")

        model_config = self.models_config.AVAILABLE_MODELS.get(recommended_model, {})
        reasoning_parts.append(f"推荐模型 {recommended_model}，质量评分: {model_config.get('quality_score', 'N/A')}")

        return "；".join(reasoning_parts)