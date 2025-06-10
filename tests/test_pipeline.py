import unittest
import asyncio
from core.pipeline import AdvancedProcessingPipeline
from data.data_structures import ProcessingResult


class TestAdvancedProcessingPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = AdvancedProcessingPipeline()

    def test_simple_pipeline_execution(self):
        async def run_test():
            question = "什么是机器学习？"
            route_config = {
                'stages': ['preprocessing', 'simple_reasoning', 'basic_validation'],
                'model_preference': 'speed',
                'timeout': 10.0
            }
            context = {}

            result = await self.pipeline.execute_pipeline(question, route_config, context)

            self.assertIsInstance(result, ProcessingResult)
            self.assertTrue(result.success)
            self.assertGreater(len(result.response), 10)
            self.assertGreater(result.confidence, 0.0)

        asyncio.run(run_test())

    def test_comprehensive_pipeline_execution(self):
        async def run_test():
            question = "请分析深度学习的发展趋势"
            route_config = {
                'stages': ['preprocessing', 'multi_source_retrieval', 'advanced_reasoning', 'multi_stage_validation'],
                'model_preference': 'quality',
                'timeout': 30.0
            }
            context = {}

            result = await self.pipeline.execute_pipeline(question, route_config, context)

            self.assertIsInstance(result, ProcessingResult)
            self.assertGreater(len(result.knowledge_sources), 0)
            self.assertGreater(result.confidence, 0.5)

        asyncio.run(run_test())

    def test_tool_orchestration_pipeline(self):
        async def run_test():
            question = "搜索最新的AI新闻并总结"
            route_config = {
                'stages': ['preprocessing', 'tool_planning', 'tool_execution', 'result_integration', 'validation'],
                'model_preference': 'balanced',
                'timeout': 25.0
            }
            context = {}

            result = await self.pipeline.execute_pipeline(question, route_config, context)

            self.assertIsInstance(result, ProcessingResult)
            if result.success:
                self.assertIn('tool_results', result.metadata or {})

        asyncio.run(run_test())

    def test_validation_pipeline(self):
        async def run_test():
            question = "解释量子计算的基本原理"
            route_config = {
                'stages': ['preprocessing', 'knowledge_retrieval', 'reasoning', 'fact_checking', 'validation'],
                'model_preference': 'quality',
                'timeout': 20.0
            }
            context = {}

            result = await self.pipeline.execute_pipeline(question, route_config, context)

            self.assertIsInstance(result, ProcessingResult)
            self.assertIn('validation_results', result.__dict__)

        asyncio.run(run_test())

    def test_error_handling(self):
        async def run_test():
            question = ""
            route_config = {
                'stages': ['invalid_stage'],
                'model_preference': 'speed',
                'timeout': 5.0
            }
            context = {}

            result = await self.pipeline.execute_pipeline(question, route_config, context)

            self.assertIsInstance(result, ProcessingResult)
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)

        asyncio.run(run_test())

    def test_pipeline_performance(self):
        async def run_test():
            question = "简单问题测试"
            route_config = {
                'stages': ['preprocessing', 'simple_reasoning'],
                'model_preference': 'speed',
                'timeout': 5.0
            }
            context = {}

            start_time = asyncio.get_event_loop().time()
            result = await self.pipeline.execute_pipeline(question, route_config, context)
            end_time = asyncio.get_event_loop().time()

            execution_time = end_time - start_time

            self.assertLess(execution_time, 10.0)
            self.assertLess(result.processing_time, 10.0)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()