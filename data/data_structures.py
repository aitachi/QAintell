from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class ProcessingRoute:
    stages: List[str] = field(default_factory=list)
    parallel_execution: bool = False
    timeout: float = 15.0
    model_preference: str = "balanced"
    context: Dict[str, Any] = field(default_factory=dict)

    def copy(self):
        return ProcessingRoute(
            stages=self.stages.copy(),
            parallel_execution=self.parallel_execution,
            timeout=self.timeout,
            model_preference=self.model_preference,
            context=self.context.copy()
        )

    def add_stage(self, stage_name: str):
        if stage_name not in self.stages:
            self.stages.append(stage_name)

    def remove_stage(self, stage_name: str):
        if stage_name in self.stages:
            self.stages.remove(stage_name)

    def add_context(self, key: str, value: Any):
        self.context[key] = value


@dataclass
class RouteEvaluation:
    predicted_quality: float = 0.0
    estimated_time: float = 0.0
    resource_cost: float = 0.0
    risk_assessment: float = 0.0
    user_satisfaction_prediction: float = 0.0
    overall_score: float = 0.0

    def __post_init__(self):
        self._validate_scores()

    def _validate_scores(self):
        for field_name in ['predicted_quality', 'risk_assessment', 'user_satisfaction_prediction', 'overall_score']:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                setattr(self, field_name, max(0.0, min(1.0, value)))


@dataclass
class PipelineState:
    question: str
    route_config: Dict[str, Any]
    context: Dict[str, Any]
    processed_question: str = ""
    response: str = ""
    confidence: float = 0.0
    status: ProcessingStatus = ProcessingStatus.PENDING
    knowledge_results: Dict[str, Any] = field(default_factory=dict)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=lambda: datetime.now().timestamp())

    def add_knowledge_results(self, source: str, results: Any):
        self.knowledge_results[source] = results

    def add_tool_results(self, results: Dict[str, Any]):
        self.tool_results.update(results)

    def add_validation_result(self, check_name: str, result: bool):
        self.validation_results[check_name] = result

    def add_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    def add_error(self, error: str):
        self.errors.append(error)

    def set_response(self, response: str):
        self.response = response

    def set_confidence(self, confidence: float):
        self.confidence = max(0.0, min(1.0, confidence))

    def get_consolidated_knowledge(self) -> str:
        consolidated = []
        for source, results in self.knowledge_results.items():
            if isinstance(results, list):
                for result in results:
                    if isinstance(result, dict) and 'content' in result:
                        consolidated.append(result['content'])
                    elif isinstance(result, str):
                        consolidated.append(result)
            elif isinstance(results, str):
                consolidated.append(results)

        return "\n".join(consolidated)

    def get_consolidated_tool_results(self) -> str:
        consolidated = []
        for tool_name, result in self.tool_results.items():
            if isinstance(result, dict):
                if 'result' in result:
                    consolidated.append(f"{tool_name}: {result['result']}")
                elif 'response' in result:
                    consolidated.append(f"{tool_name}: {result['response']}")
            elif isinstance(result, str):
                consolidated.append(f"{tool_name}: {result}")

        return "\n".join(consolidated)

    @property
    def knowledge_context(self) -> Dict[str, Any]:
        return {
            'question': self.processed_question or self.question,
            'knowledge_results': self.knowledge_results,
            'tool_results': self.tool_results,
            'metadata': self.metadata
        }

    def get_final_result(self) -> 'ProcessingResult':
        processing_time = datetime.now().timestamp() - self.start_time

        return ProcessingResult(
            response=self.response,
            confidence=self.confidence,
            success=len(self.errors) == 0 and bool(self.response),
            processing_time=processing_time,
            knowledge_sources=list(self.knowledge_results.keys()),
            tool_results=self.tool_results,
            validation_results=self.validation_results,
            metadata=self.metadata,
            errors=self.errors.copy()
        )


@dataclass
class ProcessingResult:
    response: str = ""
    confidence: float = 0.0
    success: bool = False
    processing_time: float = 0.0
    knowledge_sources: List[str] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'response': self.response,
            'confidence': self.confidence,
            'success': self.success,
            'processing_time': self.processing_time,
            'knowledge_sources': self.knowledge_sources,
            'tool_results': self.tool_results,
            'validation_results': self.validation_results,
            'metadata': self.metadata,
            'errors': self.errors,
            'error': self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingResult':
        return cls(
            response=data.get('response', ''),
            confidence=data.get('confidence', 0.0),
            success=data.get('success', False),
            processing_time=data.get('processing_time', 0.0),
            knowledge_sources=data.get('knowledge_sources', []),
            tool_results=data.get('tool_results', {}),
            validation_results=data.get('validation_results', {}),
            metadata=data.get('metadata', {}),
            errors=data.get('errors', []),
            error=data.get('error')
        )


@dataclass
class ValidationResult:
    checks: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    improvement_action: Dict[str, Any] = field(default_factory=dict)
    overall_score: float = 0.0
    status: ValidationStatus = ValidationStatus.PENDING

    def add_check(self, check_name: str, score: float):
        self.checks[check_name] = max(0.0, min(1.0, score))
        self._recalculate_overall_score()

    def get_check_result(self, check_name: str, default: float = 0.0) -> float:
        return self.checks.get(check_name, default)

    def set_confidence(self, confidence: float):
        self.confidence = max(0.0, min(1.0, confidence))

    def set_improvement_action(self, action: Dict[str, Any]):
        self.improvement_action = action

    def get_overall_score(self) -> float:
        return self.overall_score

    def get_weak_aspects(self) -> List[str]:
        threshold = 0.6
        return [check_name for check_name, score in self.checks.items() if score < threshold]

    def _recalculate_overall_score(self):
        if not self.checks:
            self.overall_score = 0.0
            return

        self.overall_score = sum(self.checks.values()) / len(self.checks)

        if self.overall_score >= 0.8:
            self.status = ValidationStatus.PASSED
        elif self.overall_score >= 0.6:
            self.status = ValidationStatus.WARNING
        else:
            self.status = ValidationStatus.FAILED


@dataclass
class InteractionData:
    question: str = ""
    classification: Dict[str, Any] = field(default_factory=dict)
    processing_route: Dict[str, Any] = field(default_factory=dict)
    result: Optional[ProcessingResult] = None
    total_processing_time: float = 0.0
    complexity_level: int = 0
    user_satisfaction_score: float = 0.0
    resource_consumption: float = 0.0
    cost_per_interaction: float = 0.0
    error_count: int = 0
    total_steps: int = 0
    was_escalated: bool = False
    user_feedback: Dict[str, Any] = field(default_factory=dict)
    validation_result: Optional[ValidationResult] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'classification': self.classification,
            'processing_route': self.processing_route,
            'result': self.result.to_dict() if self.result else None,
            'total_processing_time': self.total_processing_time,
            'complexity_level': self.complexity_level,
            'user_satisfaction_score': self.user_satisfaction_score,
            'resource_consumption': self.resource_consumption,
            'cost_per_interaction': self.cost_per_interaction,
            'error_count': self.error_count,
            'total_steps': self.total_steps,
            'was_escalated': self.was_escalated,
            'user_feedback': self.user_feedback,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class LearningPattern:
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence: float = 0.0
    frequency: int = 1
    last_seen: datetime = field(default_factory=datetime.now)

    def update_frequency(self):
        self.frequency += 1
        self.last_seen = datetime.now()

    def calculate_relevance(self) -> float:
        time_decay = 1.0
        days_since_last_seen = (datetime.now() - self.last_seen).days
        if days_since_last_seen > 0:
            time_decay = max(0.1, 1.0 - (days_since_last_seen / 30))

        frequency_score = min(1.0, self.frequency / 10)

        return self.confidence * 0.4 + frequency_score * 0.3 + time_decay * 0.3


@dataclass
class UserProfile:
    user_id: str
    expertise_level: str = "intermediate"
    preferred_domains: List[str] = field(default_factory=list)
    learning_style: str = "practical"
    communication_preference: str = "detailed"
    interaction_history: List[InteractionData] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.now)

    def add_interaction(self, interaction: InteractionData):
        self.interaction_history.append(interaction)
        self.last_active = datetime.now()

        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]

        self._update_performance_metrics(interaction)

    def get_recent_interactions(self, limit: int = 10) -> List[InteractionData]:
        return self.interaction_history[-limit:]

    def _update_performance_metrics(self, interaction: InteractionData):
        if interaction.result:
            current_avg = self.performance_metrics.get('avg_satisfaction', 0.0)
            total_interactions = len(self.interaction_history)

            new_avg = (current_avg * (
                        total_interactions - 1) + interaction.user_satisfaction_score) / total_interactions
            self.performance_metrics['avg_satisfaction'] = new_avg

            self.performance_metrics['total_interactions'] = total_interactions
            self.performance_metrics['success_rate'] = sum(
                1 for i in self.interaction_history if i.result and i.result.success) / total_interactions


@dataclass
class SystemMetrics:
    timestamp: datetime = field(default_factory=datetime.now)
    response_time_avg: float = 0.0
    response_time_p95: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    active_users: int = 0
    cache_hit_rate: float = 0.0
    model_performance: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'response_time_avg': self.response_time_avg,
            'response_time_p95': self.response_time_p95,
            'error_rate': self.error_rate,
            'throughput': self.throughput,
            'resource_utilization': self.resource_utilization,
            'active_users': self.active_users,
            'cache_hit_rate': self.cache_hit_rate,
            'model_performance': self.model_performance
        }