import unittest
import asyncio
from core.router import IntelligentRoutingEngine
from data.data_structures import ProcessingRoute


class TestIntelligentRoutingEngine(unittest.TestCase):
    def setUp(self):
        self.router = IntelligentRoutingEngine()

    def test_fast_track_routing(self):
        async def run_test():
            classification_result = {
                'complexity_level': 1,
                'domain_type': 'general',
                'urgency_level': 'high',
                'requires_tools': False,
                'requires_fresh_data': False,
                'user_expertise': 'beginner',
                'recommended_strategy': 'fast_track'
            }
            system_status = {'load_factor': 1.0}

            route = await self.router.create_processing_pipeline(classification_result, system_status)

            self.assertIsInstance(route, ProcessingRoute)
            self.assertIn('preprocessing', route.stages)
            self.assertLessEqual(route.timeout, 10.0)
            self.assertEqual(route.model_preference, 'speed')

        asyncio.run(run_test())

    def test_comprehensive_routing(self):
        async def run_test():
            classification_result = {
                'complexity_level': 5,
                'domain_type': 'professional',
                'urgency_level': 'medium',
                'requires_tools': True,
                'requires_fresh_data': True,
                'user_expertise': 'expert',
                'recommended_strategy': 'comprehensive'
            }
            system_status = {'load_factor': 1.0}

            route = await self.router.create_processing_pipeline(classification_result, system_status)

            self.assertGreater(len(route.stages), 3)
            self.assertTrue(route.parallel_execution)
            self.assertEqual(route.model_preference, 'quality')

        asyncio.run(run_test())

    def test_tool_assisted_routing(self):
        async def run_test():
            classification_result = {
                'complexity_level': 3,
                'domain_type': 'specialized',
                'urgency_level': 'medium',
                'requires_tools': True,
                'requires_fresh_data': False,
                'user_expertise': 'intermediate',
                'recommended_strategy': 'tool_assisted'
            }
            system_status = {'load_factor': 1.0}

            route = await self.router.create_processing_pipeline(classification_result, system_status)

            self.assertIn('tool_planning', route.stages)
            self.assertIn('tool_execution', route.stages)
            self.assertIn('result_integration', route.stages)

        asyncio.run(run_test())

    def test_high_load_adaptation(self):
        async def run_test():
            classification_result = {
                'complexity_level': 3,
                'domain_type': 'general',
                'urgency_level': 'medium',
                'requires_tools': False,
                'requires_fresh_data': False,
                'user_expertise': 'intermediate',
                'recommended_strategy': 'standard'
            }
            system_status = {'load_factor': 2.5}

            route = await self.router.create_processing_pipeline(classification_result, system_status)

            self.assertLessEqual(route.timeout, 15.0)
            self.assertIn(route.model_preference, ['speed', 'balanced'])

        asyncio.run(run_test())

    def test_route_context_addition(self):
        async def run_test():
            classification_result = {
                'complexity_level': 2,
                'domain_type': 'general',
                'urgency_level': 'low',
                'requires_tools': False,
                'requires_fresh_data': False,
                'user_expertise': 'beginner',
                'recommended_strategy': 'standard'
            }
            system_status = {'load_factor': 1.0}

            route = await self.router.create_processing_pipeline(classification_result, system_status)

            self.assertIn('classification_result', route.context)
            self.assertIn('selected_model', route.context)
            self.assertIn('resource_allocation', route.context)

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()