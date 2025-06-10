import unittest
import asyncio
from core.classifier import MultiDimensionalClassifier


class TestMultiDimensionalClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = MultiDimensionalClassifier()

    def test_simple_question_classification(self):
        async def run_test():
            question = "什么是Python?"
            user_context = {}
            conversation_history = []

            result = await self.classifier.classify_question(question, user_context, conversation_history)

            self.assertIn('complexity_level', result)
            self.assertIn('domain_type', result)
            self.assertIn('urgency_level', result)
            self.assertLessEqual(result['complexity_level'], 2)

        asyncio.run(run_test())

    def test_complex_question_classification(self):
        async def run_test():
            question = "请详细分析深度学习中的注意力机制原理，并解释其在自然语言处理中的应用"
            user_context = {}
            conversation_history = []

            result = await self.classifier.classify_question(question, user_context, conversation_history)

            self.assertGreaterEqual(result['complexity_level'], 3)
            self.assertEqual(result['domain_type'], 'professional')

        asyncio.run(run_test())

    def test_urgent_question_classification(self):
        async def run_test():
            question = "紧急！服务器宕机了，如何立即恢复？"
            user_context = {}
            conversation_history = []

            result = await self.classifier.classify_question(question, user_context, conversation_history)

            self.assertEqual(result['urgency_level'], 'high')
            self.assertTrue(result['requires_tools'])

        asyncio.run(run_test())

    def test_tool_requirement_detection(self):
        async def run_test():
            question = "请搜索最新的AI发展趋势并计算相关数据"
            user_context = {}
            conversation_history = []

            result = await self.classifier.classify_question(question, user_context, conversation_history)

            self.assertTrue(result['requires_tools'])
            self.assertTrue(result['requires_fresh_data'])

        asyncio.run(run_test())

    def test_user_context_influence(self):
        async def run_test():
            question = "如何优化算法性能？"
            user_context = {'expertise_level': 'expert', 'domains': ['computer_science']}
            conversation_history = []

            result = await self.classifier.classify_question(question, user_context, conversation_history)

            self.assertEqual(result['user_expertise'], 'expert')
            self.assertIn('recommended_strategy', result)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()