import time
import asyncio
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict


class PerformanceTracker:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.real_time_metrics = {}
        self.aggregated_metrics = {}
        self._last_update = time.time()

    async def record(self, metrics: Dict[str, float]):
        timestamp = time.time()
        metrics_entry = {
            'timestamp': timestamp,
            'metrics': metrics.copy()
        }

        self.metrics_history.append(metrics_entry)
        self._update_real_time_metrics(metrics)

        if timestamp - self._last_update > 60:
            self._update_aggregated_metrics()
            self._last_update = timestamp

    def get_metric_trend(self, metric_name: str, time_window: int = 300) -> Dict[str, Any]:
        current_time = time.time()
        recent_entries = [
            entry for entry in self.metrics_history
            if current_time - entry['timestamp'] <= time_window
               and metric_name in entry['metrics']
        ]

        if not recent_entries:
            return {'trend': 'unknown', 'values': [], 'avg': 0.0}

        values = [entry['metrics'][metric_name] for entry in recent_entries]

        if len(values) < 3:
            return {'trend': 'insufficient_data', 'values': values, 'avg': statistics.mean(values)}

        first_half = values[:len(values) // 2]
        second_half = values[len(values) // 2:]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        if second_avg > first_avg * 1.1:
            trend = 'increasing'
        elif second_avg < first_avg * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'values': values,
            'avg': statistics.mean(values),
            'recent_avg': second_avg,
            'change_rate': (second_avg - first_avg) / first_avg if first_avg > 0 else 0
        }

    def get_performance_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        current_time = time.time()
        recent_entries = [
            entry for entry in self.metrics_history
            if current_time - entry['timestamp'] <= time_window
        ]

        if not recent_entries:
            return {'summary': 'no_data', 'period': time_window}

        all_metrics = defaultdict(list)
        for entry in recent_entries:
            for metric_name, value in entry['metrics'].items():
                all_metrics[metric_name].append(value)

        summary = {}
        for metric_name, values in all_metrics.items():
            summary[metric_name] = {
                'count': len(values),
                'avg': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'median': statistics.median(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0
            }

        return {
            'summary': summary,
            'period': time_window,
            'total_entries': len(recent_entries)
        }

    def _update_real_time_metrics(self, metrics: Dict[str, float]):
        for metric_name, value in metrics.items():
            if metric_name not in self.real_time_metrics:
                self.real_time_metrics[metric_name] = {
                    'current': value,
                    'rolling_avg': value,
                    'count': 1
                }
            else:
                current_data = self.real_time_metrics[metric_name]
                current_data['current'] = value
                current_data['count'] += 1

                alpha = 0.1
                current_data['rolling_avg'] = (
                        alpha * value + (1 - alpha) * current_data['rolling_avg']
                )

    def _update_aggregated_metrics(self):
        if not self.metrics_history:
            return

        time_windows = [300, 900, 3600]
        current_time = time.time()

        for window in time_windows:
            window_entries = [
                entry for entry in self.metrics_history
                if current_time - entry['timestamp'] <= window
            ]

            if not window_entries:
                continue

            window_key = f'{window}s'
            if window_key not in self.aggregated_metrics:
                self.aggregated_metrics[window_key] = {}

            all_metrics = defaultdict(list)
            for entry in window_entries:
                for metric_name, value in entry['metrics'].items():
                    all_metrics[metric_name].append(value)

            for metric_name, values in all_metrics.items():
                self.aggregated_metrics[window_key][metric_name] = {
                    'avg': statistics.mean(values),
                    'p95': self._percentile(values, 95),
                    'p99': self._percentile(values, 99)
                }

    def _percentile(self, values: List[float], percentile: int) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


class PerformanceOptimizer:
    def __init__(self):
        self.optimization_rules = {}
        self.performance_baselines = {}
        self.optimization_history = []

    def analyze_performance_bottlenecks(self, metrics_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        bottlenecks = []

        for metric_name, stats in metrics_summary.get('summary', {}).items():
            if metric_name == 'response_time':
                if stats['avg'] > 10.0:
                    bottlenecks.append({
                        'type': 'high_response_time',
                        'severity': 'high' if stats['avg'] > 20.0 else 'medium',
                        'metric': metric_name,
                        'current_value': stats['avg'],
                        'recommendation': 'optimize_model_selection'
                    })

            elif metric_name == 'error_rate':
                if stats['avg'] > 0.1:
                    bottlenecks.append({
                        'type': 'high_error_rate',
                        'severity': 'high' if stats['avg'] > 0.2 else 'medium',
                        'metric': metric_name,
                        'current_value': stats['avg'],
                        'recommendation': 'improve_error_handling'
                    })

            elif metric_name == 'resource_usage':
                if stats['avg'] > 0.8:
                    bottlenecks.append({
                        'type': 'high_resource_usage',
                        'severity': 'high' if stats['avg'] > 0.9 else 'medium',
                        'metric': metric_name,
                        'current_value': stats['avg'],
                        'recommendation': 'scale_resources'
                    })

        return bottlenecks

    def generate_optimization_suggestions(self, bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        suggestions = []

        for bottleneck in bottlenecks:
            suggestion_map = {
                'optimize_model_selection': {
                    'action': 'adjust_model_thresholds',
                    'priority': 'high',
                    'description': '调整模型选择阈值以提高响应速度'
                },
                'improve_error_handling': {
                    'action': 'enhance_retry_logic',
                    'priority': 'high',
                    'description': '改进错误处理和重试机制'
                },
                'scale_resources': {
                    'action': 'increase_capacity',
                    'priority': 'medium',
                    'description': '增加系统资源容量'
                }
            }

            if bottleneck['recommendation'] in suggestion_map:
                suggestion = suggestion_map[bottleneck['recommendation']].copy()
                suggestion['bottleneck'] = bottleneck
                suggestions.append(suggestion)

        return suggestions


class ResourceManager:
    def __init__(self):
        self.resource_limits = {
            'cpu_cores': 8,
            'memory_gb': 32,
            'concurrent_requests': 100,
            'api_calls_per_minute': 1000
        }
        self.current_usage = {
            'cpu_cores': 0,
            'memory_gb': 0,
            'concurrent_requests': 0,
            'api_calls_per_minute': 0
        }
        self.usage_history = deque(maxlen=100)
        self.load_factor = 1.0

    def allocate_resources(self, request: Dict[str, Any]) -> Dict[str, Any]:
        required_resources = {
            'cpu_cores': request.get('cpu_cores', 1),
            'memory_gb': request.get('memory_gb', 2),
            'estimated_time': request.get('estimated_time', 5.0)
        }

        if self._can_allocate(required_resources):
            self._update_usage(required_resources, 'allocate')
            return {
                'allocated': True,
                'resources': required_resources,
                'allocation_id': f"alloc_{int(time.time())}"
            }
        else:
            return {
                'allocated': False,
                'reason': 'insufficient_resources',
                'available_resources': self._get_available_resources()
            }

    def release_resources(self, allocation_id: str, used_resources: Dict[str, Any]):
        self._update_usage(used_resources, 'release')

    def is_high_load(self) -> bool:
        total_load = 0
        resource_count = 0

        for resource, limit in self.resource_limits.items():
            if resource in self.current_usage:
                usage_ratio = self.current_usage[resource] / limit
                total_load += usage_ratio
                resource_count += 1

        if resource_count == 0:
            return False

        average_load = total_load / resource_count
        return average_load > 0.8

    def get_load_factor(self) -> float:
        if not self.usage_history:
            return 1.0

        recent_usage = list(self.usage_history)[-10:]
        avg_load = sum(usage['total_load'] for usage in recent_usage) / len(recent_usage)

        self.load_factor = max(1.0, avg_load * 2)
        return self.load_factor

    def _can_allocate(self, required: Dict[str, Any]) -> bool:
        for resource, amount in required.items():
            if resource in self.resource_limits:
                available = self.resource_limits[resource] - self.current_usage.get(resource, 0)
                if amount > available:
                    return False
        return True

    def _update_usage(self, resources: Dict[str, Any], operation: str):
        multiplier = 1 if operation == 'allocate' else -1

        for resource, amount in resources.items():
            if resource in self.current_usage:
                self.current_usage[resource] += amount * multiplier
                self.current_usage[resource] = max(0, self.current_usage[resource])

        self._record_usage()

    def _get_available_resources(self) -> Dict[str, Any]:
        available = {}
        for resource, limit in self.resource_limits.items():
            used = self.current_usage.get(resource, 0)
            available[resource] = max(0, limit - used)
        return available

    def _record_usage(self):
        total_load = 0
        for resource, limit in self.resource_limits.items():
            if resource in self.current_usage and limit > 0:
                total_load += self.current_usage[resource] / limit

        usage_entry = {
            'timestamp': time.time(),
            'usage': self.current_usage.copy(),
            'total_load': total_load / len(self.resource_limits)
        }
        self.usage_history.append(usage_entry)


class QualityPredictor:
    def __init__(self):
        self.quality_models = {}
        self.feature_weights = {
            'complexity_match': 0.3,
            'model_performance': 0.25,
            'resource_adequacy': 0.2,
            'historical_success': 0.25
        }

    async def predict_quality(self, route, classification_result: Dict[str, Any]) -> float:
        features = self._extract_quality_features(route, classification_result)
        quality_score = self._calculate_quality_score(features)

        return min(max(quality_score, 0.0), 1.0)

    def _extract_quality_features(self, route, classification_result: Dict[str, Any]) -> Dict[str, float]:
        features = {}

        complexity_level = classification_result.get('complexity_level', 2)
        route_complexity = self._estimate_route_complexity(route)
        complexity_match = 1.0 - abs(complexity_level - route_complexity) / 5.0
        features['complexity_match'] = complexity_match

        model_preference = getattr(route, 'model_preference', 'balanced')
        model_performance = self._get_model_performance_score(model_preference)
        features['model_performance'] = model_performance

        timeout = getattr(route, 'timeout', 15.0)
        resource_adequacy = min(timeout / 30.0, 1.0)
        features['resource_adequacy'] = resource_adequacy

        features['historical_success'] = 0.8

        return features

    def _calculate_quality_score(self, features: Dict[str, float]) -> float:
        total_score = 0.0
        total_weight = 0.0

        for feature_name, value in features.items():
            if feature_name in self.feature_weights:
                weight = self.feature_weights[feature_name]
                total_score += value * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.5

    def _estimate_route_complexity(self, route) -> float:
        if hasattr(route, 'stages'):
            stage_count = len(route.stages)
            if stage_count <= 2:
                return 1.0
            elif stage_count <= 4:
                return 2.5
            else:
                return 4.0
        return 2.0

    def _get_model_performance_score(self, model_preference: str) -> float:
        performance_map = {
            'speed': 0.7,
            'quality': 0.9,
            'balanced': 0.8
        }
        return performance_map.get(model_preference, 0.75)


class RealTimePerformanceMonitor:
    def __init__(self):
        self.monitoring_active = False
        self.metrics_collectors = []
        self.alert_thresholds = {
            'response_time': 20.0,
            'error_rate': 0.15,
            'resource_usage': 0.85
        }
        self.current_status = {
            'load_factor': 1.0,
            'available_models': ['qwen-turbo', 'qwen-plus', 'qwen-max'],
            'resource_usage': 0.5,
            'error_rate': 0.02,
            'avg_response_time': 5.0
        }
        self.anomaly_detector = AnomalyDetector()
        self.auto_tuner = AutoTuner()

    async def start_monitoring(self):
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        self.monitoring_active = False

    def get_current_status(self) -> Dict[str, Any]:
        return self.current_status.copy()

    async def _monitoring_loop(self):
        while self.monitoring_active:
            try:
                await self._collect_metrics()
                await self._check_anomalies()
                await self._apply_auto_tuning()
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(10)

    async def _collect_metrics(self):
        import random

        self.current_status.update({
            'load_factor': 1.0 + random.uniform(-0.2, 0.5),
            'resource_usage': 0.5 + random.uniform(-0.2, 0.3),
            'error_rate': 0.02 + random.uniform(-0.01, 0.08),
            'avg_response_time': 5.0 + random.uniform(-2.0, 10.0)
        })

    async def _check_anomalies(self):
        anomalies = self.anomaly_detector.detect_anomalies(self.current_status)

        if anomalies:
            adjustments = self.auto_tuner.generate_adjustments(anomalies)
            await self._apply_adjustments(adjustments)

    async def _apply_auto_tuning(self):
        if self.current_status['load_factor'] > 1.5:
            self.current_status['available_models'] = ['qwen-turbo']
        elif self.current_status['load_factor'] < 0.8:
            self.current_status['available_models'] = ['qwen-turbo', 'qwen-plus', 'qwen-max']

    async def _apply_adjustments(self, adjustments: List[Dict[str, Any]]):
        for adjustment in adjustments:
            if adjustment.get('type') == 'resource_scaling':
                self.current_status['load_factor'] *= 0.9
            elif adjustment.get('type') == 'threshold_adjustment':
                pass
            elif adjustment.get('type') == 'routing_modification':
                pass


class AnomalyDetector:
    def __init__(self):
        self.thresholds = {
            'response_time_high': 15.0,
            'error_rate_high': 0.1,
            'resource_usage_high': 0.85,
            'load_factor_high': 2.0
        }

    def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        anomalies = []

        if metrics.get('avg_response_time', 0) > self.thresholds['response_time_high']:
            anomalies.append({
                'type': 'high_response_time',
                'severity': 'high',
                'value': metrics['avg_response_time'],
                'threshold': self.thresholds['response_time_high']
            })

        if metrics.get('error_rate', 0) > self.thresholds['error_rate_high']:
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'value': metrics['error_rate'],
                'threshold': self.thresholds['error_rate_high']
            })

        if metrics.get('resource_usage', 0) > self.thresholds['resource_usage_high']:
            anomalies.append({
                'type': 'high_resource_usage',
                'severity': 'medium',
                'value': metrics['resource_usage'],
                'threshold': self.thresholds['resource_usage_high']
            })

        return anomalies


class AutoTuner:
    def generate_adjustments(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        adjustments = []

        for anomaly in anomalies:
            if anomaly['type'] == 'high_response_time':
                adjustments.append({
                    'type': 'resource_scaling',
                    'parameters': {'scale_factor': 1.2},
                    'reason': 'high_response_time'
                })
            elif anomaly['type'] == 'high_error_rate':
                adjustments.append({
                    'type': 'threshold_adjustment',
                    'parameters': {'retry_count': 3},
                    'reason': 'high_error_rate'
                })
            elif anomaly['type'] == 'high_resource_usage':
                adjustments.append({
                    'type': 'routing_modification',
                    'parameters': {'prefer_fast_models': True},
                    'reason': 'high_resource_usage'
                })

        return adjustments