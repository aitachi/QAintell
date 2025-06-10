import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[]
    )

    logger = logging.getLogger("intelligent_qa_system")
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    error_log_file = log_file.replace('.log', '_error.log') if log_file else 'logs/error.log'
    os.makedirs(os.path.dirname(error_log_file), exist_ok=True)

    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)

    logger.info("Logging system initialized")
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"intelligent_qa_system.{name}")


class StructuredLogger:
    def __init__(self, logger_name: str):
        self.logger = get_logger(logger_name)

    def log_interaction(self, interaction_data: Dict[str, Any]):
        self.logger.info(
            f"Interaction processed - "
            f"Question: {interaction_data.get('question', '')[:100]}... - "
            f"Processing time: {interaction_data.get('processing_time', 0):.2f}s - "
            f"Success: {interaction_data.get('success', False)}"
        )

    def log_performance(self, metrics: Dict[str, Any]):
        self.logger.info(
            f"Performance metrics - "
            f"Response time: {metrics.get('response_time', 0):.2f}s - "
            f"Accuracy: {metrics.get('accuracy_score', 0):.2f} - "
            f"Resource usage: {metrics.get('resource_usage', 0):.2f}"
        )

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        context_str = ""
        if context:
            context_str = f" - Context: {context}"

        self.logger.error(
            f"Error occurred: {type(error).__name__}: {str(error)}{context_str}",
            exc_info=True
        )

    def log_classification(self, question: str, classification_result: Dict[str, Any]):
        self.logger.debug(
            f"Question classified - "
            f"Question: {question[:50]}... - "
            f"Complexity: {classification_result.get('complexity_level', 'unknown')} - "
            f"Domain: {classification_result.get('domain_type', 'unknown')} - "
            f"Urgency: {classification_result.get('urgency_level', 'unknown')}"
        )

    def log_routing(self, route_decision: Dict[str, Any]):
        self.logger.debug(
            f"Route selected - "
            f"Strategy: {route_decision.get('recommended_strategy', 'unknown')} - "
            f"Model: {route_decision.get('selected_model', 'unknown')} - "
            f"Timeout: {route_decision.get('timeout', 0)}s"
        )

    def log_tool_execution(self, tool_name: str, execution_result: Dict[str, Any]):
        success = execution_result.get('success', False)
        execution_time = execution_result.get('execution_time', 0)

        self.logger.debug(
            f"Tool executed - "
            f"Tool: {tool_name} - "
            f"Success: {success} - "
            f"Time: {execution_time:.2f}s"
        )

    def log_quality_check(self, validation_result: Dict[str, Any]):
        overall_score = validation_result.get('overall_score', 0)
        confidence = validation_result.get('confidence', 0)

        self.logger.debug(
            f"Quality check completed - "
            f"Overall score: {overall_score:.2f} - "
            f"Confidence: {confidence:.2f}"
        )


class MetricsLogger:
    def __init__(self):
        self.logger = get_logger("metrics")
        self.metrics_buffer = []
        self.buffer_size = 100

    def log_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        timestamp = datetime.now().isoformat()
        metric_entry = {
            'timestamp': timestamp,
            'metric': metric_name,
            'value': value,
            'tags': tags or {}
        }

        self.metrics_buffer.append(metric_entry)

        if len(self.metrics_buffer) >= self.buffer_size:
            self._flush_metrics()

    def log_response_time(self, response_time: float, complexity_level: int):
        self.log_metric(
            'response_time',
            response_time,
            {'complexity': str(complexity_level)}
        )

    def log_accuracy(self, accuracy_score: float, domain: str):
        self.log_metric(
            'accuracy_score',
            accuracy_score,
            {'domain': domain}
        )

    def log_resource_usage(self, cpu_usage: float, memory_usage: float):
        self.log_metric('cpu_usage', cpu_usage)
        self.log_metric('memory_usage', memory_usage)

    def log_user_satisfaction(self, satisfaction_score: float, user_type: str):
        self.log_metric(
            'user_satisfaction',
            satisfaction_score,
            {'user_type': user_type}
        )

    def _flush_metrics(self):
        if not self.metrics_buffer:
            return

        for metric in self.metrics_buffer:
            self.logger.info(
                f"METRIC - {metric['metric']}: {metric['value']} "
                f"at {metric['timestamp']} "
                f"tags={metric['tags']}"
            )

        self.metrics_buffer.clear()