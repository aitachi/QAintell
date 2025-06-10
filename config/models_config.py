from typing import Dict, Any, List


class ModelsConfig:
    AVAILABLE_MODELS = {
        "qwen-turbo": {
            "name": "qwen-turbo",
            "max_tokens": 8000,
            "cost_per_token": 0.001,
            "speed_score": 9,
            "quality_score": 6,
            "suitable_complexity": [0, 1, 2]
        },
        "qwen-plus": {
            "name": "qwen-plus",
            "max_tokens": 32000,
            "cost_per_token": 0.002,
            "speed_score": 7,
            "quality_score": 8,
            "suitable_complexity": [2, 3, 4]
        },
        "qwen-max": {
            "name": "qwen-max",
            "max_tokens": 128000,
            "cost_per_token": 0.005,
            "speed_score": 5,
            "quality_score": 10,
            "suitable_complexity": [3, 4, 5]
        }
    }

    MODEL_SELECTION_RULES = {
        "speed_priority": {
            "primary_factor": "speed_score",
            "secondary_factor": "cost_per_token",
            "quality_threshold": 6
        },
        "quality_priority": {
            "primary_factor": "quality_score",
            "secondary_factor": "suitable_complexity",
            "cost_threshold": 0.003
        },
        "balanced": {
            "speed_weight": 0.3,
            "quality_weight": 0.5,
            "cost_weight": 0.2
        }
    }

    ENSEMBLE_CONFIGS = {
        "consensus": {
            "models": ["qwen-plus", "qwen-max"],
            "voting_strategy": "weighted",
            "weights": [0.4, 0.6]
        },
        "diverse": {
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "voting_strategy": "majority",
            "weights": [0.2, 0.4, 0.4]
        }
    }