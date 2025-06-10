import asyncio
import statistics
from typing import Dict, Any, List, Optional, Tuple
from config.models_config import ModelsConfig


class EnsembleCoordinator:
    def __init__(self):
        self.models_config = ModelsConfig()
        self.voting_strategies = {
            'majority': self._majority_voting,
            'weighted': self._weighted_voting,
            'confidence': self._confidence_based_voting,
            'quality': self._quality_based_voting,
            'consensus': self._consensus_building
        }

    async def coordinate_responses(self, responses: List[Dict[str, Any]], question: str, strategy: str = 'weighted') -> \
    Dict[str, Any]:
        if not responses:
            return self._create_empty_response()

        if len(responses) == 1:
            return self._format_single_response(responses[0])

        voting_strategy = self.voting_strategies.get(strategy, self._weighted_voting)
        coordinated_response = await voting_strategy(responses, question)

        coordination_metadata = self._generate_coordination_metadata(responses, strategy)
        coordinated_response.update(coordination_metadata)

        return coordinated_response

    async def parallel_inference(self, models: List[str], question: str, context: Dict[str, Any]) -> List[
        Dict[str, Any]]:
        tasks = []
        for model_name in models:
            task = self._single_model_inference(model_name, question, context)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        valid_responses = []
        for i, response in enumerate(responses):
            if not isinstance(response, Exception):
                valid_responses.append({
                    'model': models[i],
                    'response': response.get('response', ''),
                    'confidence': response.get('confidence', 0.5),
                    'processing_time': response.get('processing_time', 0.0),
                    'quality_indicators': response.get('quality_indicators', {})
                })
            else:
                valid_responses.append({
                    'model': models[i],
                    'response': f"模型 {models[i]} 处理失败: {str(response)}",
                    'confidence': 0.0,
                    'processing_time': 0.0,
                    'error': str(response)
                })

        return valid_responses

    async def adaptive_ensemble(self, question: str, context: Dict[str, Any], available_models: List[str]) -> Dict[
        str, Any]:
        complexity = self._estimate_question_complexity(question)

        if complexity <= 2:
            selected_models = available_models[:1]
            strategy = 'single'
        elif complexity <= 3:
            selected_models = available_models[:2]
            strategy = 'weighted'
        else:
            selected_models = available_models[:3]
            strategy = 'consensus'

        if len(selected_models) == 1:
            response = await self._single_model_inference(selected_models[0], question, context)
            return self._format_single_response(response)

        responses = await self.parallel_inference(selected_models, question, context)
        return await self.coordinate_responses(responses, question, strategy)

    async def _majority_voting(self, responses: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        if len(responses) < 3:
            return await self._weighted_voting(responses, question)

        response_groups = self._group_similar_responses(responses)

        largest_group = max(response_groups, key=len)

        if len(largest_group) == 1 and len(responses) >= 3:
            weighted_response = await self._weighted_voting(responses, question)
            weighted_response['voting_method'] = 'fallback_to_weighted'
            return weighted_response

        group_confidence = sum(r['confidence'] for r in largest_group) / len(largest_group)
        representative_response = max(largest_group, key=lambda r: r['confidence'])

        return {
            'response': representative_response['response'],
            'confidence': group_confidence,
            'ensemble_size': len(responses),
            'consensus_size': len(largest_group),
            'voting_method': 'majority',
            'contributing_models': [r['model'] for r in largest_group]
        }

    async def _weighted_voting(self, responses: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        weights = self._calculate_model_weights(responses)

        weighted_responses = []
        total_weight = 0

        for response, weight in zip(responses, weights):
            if 'error' not in response:
                weighted_responses.append({
                    'content': response['response'],
                    'weight': weight,
                    'confidence': response['confidence'],
                    'model': response['model']
                })
                total_weight += weight

        if not weighted_responses:
            return self._create_error_response("所有模型都发生错误")

        if total_weight == 0:
            weights = [1.0] * len(weighted_responses)
            total_weight = len(weighted_responses)
        else:
            weights = [wr['weight'] for wr in weighted_responses]

        final_response = self._combine_weighted_responses(weighted_responses, weights, total_weight)

        weighted_confidence = sum(wr['confidence'] * wr['weight'] for wr in weighted_responses) / total_weight

        return {
            'response': final_response,
            'confidence': weighted_confidence,
            'ensemble_size': len(responses),
            'successful_models': len(weighted_responses),
            'voting_method': 'weighted',
            'model_weights': {wr['model']: wr['weight'] for wr in weighted_responses}
        }

    async def _confidence_based_voting(self, responses: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        valid_responses = [r for r in responses if 'error' not in r]

        if not valid_responses:
            return self._create_error_response("所有模型都发生错误")

        confidence_threshold = 0.7
        high_confidence_responses = [r for r in valid_responses if r['confidence'] >= confidence_threshold]

        if high_confidence_responses:
            selected_responses = high_confidence_responses
        else:
            selected_responses = sorted(valid_responses, key=lambda r: r['confidence'], reverse=True)[:2]

        if len(selected_responses) == 1:
            best_response = selected_responses[0]
            return {
                'response': best_response['response'],
                'confidence': best_response['confidence'],
                'ensemble_size': len(responses),
                'voting_method': 'confidence_single',
                'selected_model': best_response['model']
            }

        return await self._weighted_voting(selected_responses, question)

    async def _quality_based_voting(self, responses: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        quality_scores = []

        for response in responses:
            if 'error' in response:
                quality_scores.append(0.0)
            else:
                quality_score = self._calculate_response_quality(response['response'], question)
                quality_scores.append(quality_score)

        quality_threshold = 0.6
        high_quality_indices = [i for i, score in enumerate(quality_scores) if score >= quality_threshold]

        if high_quality_indices:
            selected_responses = [responses[i] for i in high_quality_indices]
        else:
            best_index = max(range(len(quality_scores)), key=lambda i: quality_scores[i])
            selected_responses = [responses[best_index]]

        return await self._weighted_voting(selected_responses, question)

    async def _consensus_building(self, responses: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        valid_responses = [r for r in responses if 'error' not in r]

        if len(valid_responses) <= 1:
            return await self._weighted_voting(responses, question)

        consensus_analysis = self._analyze_consensus(valid_responses)

        if consensus_analysis['consensus_level'] >= 0.7:
            consensus_response = self._build_consensus_response(valid_responses, consensus_analysis)
            return {
                'response': consensus_response,
                'confidence': consensus_analysis['average_confidence'],
                'ensemble_size': len(responses),
                'consensus_level': consensus_analysis['consensus_level'],
                'voting_method': 'consensus',
                'agreement_points': consensus_analysis['common_points'],
                'disagreement_points': consensus_analysis['differences']
            }
        else:
            return await self._weighted_voting(valid_responses, question)

    def _calculate_model_weights(self, responses: List[Dict[str, Any]]) -> List[float]:
        weights = []

        for response in responses:
            if 'error' in response:
                weights.append(0.0)
                continue

            model_name = response['model']
            base_weight = 1.0

            if model_name in self.models_config.AVAILABLE_MODELS:
                model_config = self.models_config.AVAILABLE_MODELS[model_name]
                quality_weight = model_config['quality_score'] / 10.0
                base_weight = quality_weight

            confidence_weight = response['confidence']

            processing_time = response.get('processing_time', 5.0)
            speed_weight = max(0.1, 1.0 - processing_time / 30.0)

            final_weight = base_weight * 0.4 + confidence_weight * 0.4 + speed_weight * 0.2
            weights.append(final_weight)

        return weights

    def _combine_weighted_responses(self, weighted_responses: List[Dict[str, Any]], weights: List[float],
                                    total_weight: float) -> str:
        if len(weighted_responses) == 1:
            return weighted_responses[0]['content']

        primary_response = max(weighted_responses, key=lambda r: r['weight'])

        other_responses = [r for r in weighted_responses if r != primary_response]

        combined_response = primary_response['content']

        if other_responses:
            high_weight_others = [r for r in other_responses if r['weight'] / total_weight > 0.2]

            if high_weight_others:
                supplementary_info = []
                for response in high_weight_others:
                    if len(response['content']) > 50:
                        key_info = self._extract_key_information(response['content'])
                        if key_info and key_info not in combined_response:
                            supplementary_info.append(key_info)

                if supplementary_info:
                    combined_response += "\n\n补充信息：\n" + "\n".join(supplementary_info)

        return combined_response

    def _group_similar_responses(self, responses: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        groups = []

        for response in responses:
            if 'error' in response:
                continue

            placed = False
            for group in groups:
                if self._responses_similar(response, group[0]):
                    group.append(response)
                    placed = True
                    break

            if not placed:
                groups.append([response])

        return groups

    def _responses_similar(self, response1: Dict[str, Any], response2: Dict[str, Any]) -> bool:
        text1 = response1['response'].lower()
        text2 = response2['response'].lower()

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        similarity = intersection / union if union > 0 else 0

        return similarity > 0.6

    def _estimate_question_complexity(self, question: str) -> int:
        complexity_indicators = {
            'length': min(len(question.split()) / 15, 2),
            'technical_terms': self._count_technical_terms(question),
            'question_depth': self._analyze_question_depth(question)
        }

        total_score = sum(complexity_indicators.values())

        if total_score >= 4:
            return 4
        elif total_score >= 3:
            return 3
        elif total_score >= 2:
            return 2
        else:
            return 1

    def _count_technical_terms(self, question: str) -> int:
        technical_terms = [
            '算法', '架构', '系统', '框架', '优化', '分析', '设计', '实现',
            '模型', '数据', '处理', '计算', '网络', '协议', '接口', '服务'
        ]

        question_lower = question.lower()
        return sum(1 for term in technical_terms if term in question_lower)

    def _analyze_question_depth(self, question: str) -> float:
        depth_indicators = ['为什么', '如何实现', '原理', '机制', '深入分析', '详细说明']
        question_lower = question.lower()

        depth_count = sum(1 for indicator in depth_indicators if indicator in question_lower)
        return min(depth_count / 2, 2.0)

    def _calculate_response_quality(self, response: str, question: str) -> float:
        if not response or len(response.strip()) < 20:
            return 0.0

        quality_score = 0.0

        length_score = min(len(response) / 200, 1.0) * 0.2
        quality_score += length_score

        structure_score = self._analyze_response_structure(response) * 0.3
        quality_score += structure_score

        relevance_score = self._calculate_relevance(response, question) * 0.3
        quality_score += relevance_score

        informativeness_score = self._calculate_informativeness(response) * 0.2
        quality_score += informativeness_score

        return min(quality_score, 1.0)

    def _analyze_response_structure(self, response: str) -> float:
        structure_score = 0.0

        sentences = [s.strip() for s in response.split('。') if s.strip()]
        if len(sentences) >= 2:
            structure_score += 0.3

        if any(marker in response for marker in ['首先', '其次', '最后', '另外', '此外']):
            structure_score += 0.3

        if any(marker in response for marker in ['因为', '所以', '因此', '由于']):
            structure_score += 0.2

        if '\n' in response or '：' in response:
            structure_score += 0.2

        return min(structure_score, 1.0)

    def _calculate_relevance(self, response: str, question: str) -> float:
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())

        if not question_words or not response_words:
            return 0.0

        intersection = len(question_words.intersection(response_words))
        relevance = intersection / len(question_words)

        return min(relevance, 1.0)

    def _calculate_informativeness(self, response: str) -> float:
        info_indicators = [
            '数据', '研究', '分析', '报告', '统计', '比例', '百分比',
            '例如', '比如', '具体', '详细', '包括', '涉及', '方面'
        ]

        response_lower = response.lower()
        info_count = sum(1 for indicator in info_indicators if indicator in response_lower)

        return min(info_count / 5, 1.0)

    def _analyze_consensus(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(responses) <= 1:
            return {
                'consensus_level': 1.0,
                'average_confidence': responses[0]['confidence'] if responses else 0.0,
                'common_points': [],
                'differences': []
            }

        all_words = []
        for response in responses:
            words = set(response['response'].lower().split())
            all_words.append(words)

        common_words = set.intersection(*all_words) if all_words else set()
        all_unique_words = set.union(*all_words) if all_words else set()

        consensus_level = len(common_words) / len(all_unique_words) if all_unique_words else 0.0

        average_confidence = sum(r['confidence'] for r in responses) / len(responses)

        common_points = list(common_words)[:10]

        differences = []
        for i, response in enumerate(responses):
            unique_words = all_words[i] - common_words
            if unique_words:
                differences.append({
                    'model': response['model'],
                    'unique_aspects': list(unique_words)[:5]
                })

        return {
            'consensus_level': consensus_level,
            'average_confidence': average_confidence,
            'common_points': common_points,
            'differences': differences
        }

    def _build_consensus_response(self, responses: List[Dict[str, Any]], consensus_analysis: Dict[str, Any]) -> str:
        primary_response = max(responses, key=lambda r: r['confidence'])

        consensus_response = primary_response['response']

        common_points = consensus_analysis.get('common_points', [])
        if common_points and len(common_points) >= 3:
            key_points = "关键共识点：" + "、".join(common_points[:5])
            consensus_response += f"\n\n{key_points}"

        differences = consensus_analysis.get('differences', [])
        if differences and len(differences) <= 2:
            additional_perspectives = []
            for diff in differences:
                if diff['unique_aspects']:
                    perspective = f"{diff['model']}的独特观点：" + "、".join(diff['unique_aspects'][:3])
                    additional_perspectives.append(perspective)

            if additional_perspectives:
                consensus_response += "\n\n补充观点：\n" + "\n".join(additional_perspectives)

        return consensus_response

    def _extract_key_information(self, response: str) -> str:
        sentences = [s.strip() for s in response.split('。') if s.strip()]

        if len(sentences) <= 2:
            return response

        key_sentences = []
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['重要', '关键', '主要', '核心', '特别']):
                key_sentences.append(sentence)

        if key_sentences:
            return '。'.join(key_sentences[:2]) + '。'
        else:
            return sentences[0] + '。' if sentences else response

    async def _single_model_inference(self, model_name: str, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1.0)

        mock_responses = {
            'qwen-turbo': f"快速回答：关于{question}的基本信息和要点。",
            'qwen-plus': f"详细分析：{question}涉及多个方面，需要综合考虑相关因素和背景。",
            'qwen-max': f"深度解答：{question}是一个复杂主题，从理论基础到实际应用都有重要意义。"
        }

        response_text = mock_responses.get(model_name, f"关于{question}的回答")

        return {
            'response': response_text,
            'confidence': 0.8 + hash(model_name) % 20 / 100,
            'processing_time': 1.0 + hash(model_name) % 30 / 10,
            'quality_indicators': {
                'length': len(response_text),
                'structure_score': 0.7,
                'relevance_score': 0.8
            }
        }

    def _create_empty_response(self) -> Dict[str, Any]:
        return {
            'response': '抱歉，无法生成回答。',
            'confidence': 0.0,
            'ensemble_size': 0,
            'voting_method': 'none',
            'error': 'No responses available'
        }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        return {
            'response': f'处理过程中出现错误：{error_message}',
            'confidence': 0.0,
            'ensemble_size': 0,
            'voting_method': 'error',
            'error': error_message
        }

    def _format_single_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'response': response.get('response', ''),
            'confidence': response.get('confidence', 0.5),
            'ensemble_size': 1,
            'voting_method': 'single',
            'model': response.get('model', 'unknown'),
            'processing_time': response.get('processing_time', 0.0)
        }

    def _generate_coordination_metadata(self, responses: List[Dict[str, Any]], strategy: str) -> Dict[str, Any]:
        successful_responses = [r for r in responses if 'error' not in r]
        failed_responses = [r for r in responses if 'error' in r]

        if successful_responses:
            avg_confidence = sum(r['confidence'] for r in successful_responses) / len(successful_responses)
            avg_processing_time = sum(r.get('processing_time', 0) for r in successful_responses) / len(
                successful_responses)
        else:
            avg_confidence = 0.0
            avg_processing_time = 0.0

        return {
            'coordination_metadata': {
                'strategy_used': strategy,
                'total_models': len(responses),
                'successful_models': len(successful_responses),
                'failed_models': len(failed_responses),
                'average_confidence': avg_confidence,
                'average_processing_time': avg_processing_time,
                'model_list': [r['model'] for r in responses]
            }
        }