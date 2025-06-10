import os
from typing import Dict, Any, List


class Settings:
    def __init__(self):
        self.API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-3ddaf4f032064a88ac72019e8e1e09df")
        self.BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

        self.ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "qa_knowledge_base")

        self.COMPLEXITY_THRESHOLDS = {
            0: {"max_tokens": 100, "response_time": 1.0},
            1: {"max_tokens": 200, "response_time": 2.0},
            2: {"max_tokens": 500, "response_time": 5.0},
            3: {"max_tokens": 1000, "response_time": 10.0},
            4: {"max_tokens": 2000, "response_time": 20.0},
            5: {"max_tokens": 4000, "response_time": 30.0}
        }

        self.QUALITY_THRESHOLDS = {
            "min_confidence": 0.7,
            "min_overall_score": 0.6,
            "fact_check_threshold": 0.8
        }

        self.CACHE_SETTINGS = {
            "ttl": 3600,
            "max_size": 1000
        }

        self.LEARNING_SETTINGS = {
            "batch_size": 100,
            "update_frequency": 3600
        }

        self.MCP_SETTINGS = {
            "server_url": os.getenv("MCP_SERVER_URL", "http://localhost:8080"),
            "timeout": 30
        }

    def get_model_config(self, complexity_level: int) -> Dict[str, Any]:
        if complexity_level <= 1:
            return {"model": "qwen-turbo", "temperature": 0.1}
        elif complexity_level <= 3:
            return {"model": "qwen-plus", "temperature": 0.3}
        else:
            return {"model": "qwen-max", "temperature": 0.5}