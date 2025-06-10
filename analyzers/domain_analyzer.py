import re
from typing import Dict, Any, List, Tuple


class DomainAnalyzer:
    def __init__(self):
        self.domain_keywords = {
            'technology': {
                'keywords': [
                    '编程', '代码', '软件', '算法', '数据结构', '框架',
                    '开发', '系统', '网络', '数据库', '服务器', '云计算',
                    'AI', '机器学习', '深度学习', '人工智能', '大数据',
                    'Python', 'Java', 'JavaScript', 'React', 'Vue',
                    '前端', '后端', '全栈', 'API', '微服务', '容器',
                    'Docker', 'Kubernetes', 'DevOps', '自动化'
                ],
                'weight': 1.0
            },
            'science': {
                'keywords': [
                    '物理', '化学', '生物', '数学', '统计', '概率',
                    '实验', '研究', '理论', '公式', '定律', '假设',
                    '分子', '原子', '基因', '蛋白质', 'DNA', 'RNA',
                    '进化', '生态', '环境', '气候', '地质', '天文',
                    '量子', '相对论', '热力学', '电磁学', '光学'
                ],
                'weight': 1.0
            },
            'medicine': {
                'keywords': [
                    '医学', '医疗', '健康', '疾病', '症状', '诊断',
                    '治疗', '药物', '手术', '康复', '预防', '免疫',
                    '病毒', '细菌', '感染', '炎症', '癌症', '肿瘤',
                    '心脏', '大脑', '肝脏', '肾脏', '肺部', '血液',
                    '神经', '内分泌', '消化', '呼吸', '循环', '免疫'
                ],
                'weight': 1.0
            },
            'business': {
                'keywords': [
                    '商业', '企业', '管理', '市场', '营销', '销售',
                    '财务', '会计', '投资', '金融', '银行', '股票',
                    '战略', '规划', '运营', '供应链', '物流', '采购',
                    '人力资源', '招聘', '培训', '绩效', '薪酬', '文化',
                    '品牌', '客户', '用户', '体验', '服务', '质量'
                ],
                'weight': 1.0
            },
            'education': {
                'keywords': [
                    '教育', '学习', '教学', '课程', '学校', '大学',
                    '教师', '学生', '考试', '评估', '成绩', '学位',
                    '培训', '技能', '知识', '能力', '素养', '发展',
                    '儿童', '青少年', '成人', '继续教育', '职业教育',
                    '在线教育', '远程教育', '教育技术', '学习平台'
                ],
                'weight': 1.0
            },
            'law': {
                'keywords': [
                    '法律', '法规', '条例', '法院', '法官', '律师',
                    '诉讼', '判决', '合同', '协议', '权利', '义务',
                    '民法', '刑法', '商法', '行政法', '国际法', '宪法',
                    '侵权', '违约', '犯罪', '证据', '程序', '执行',
                    '知识产权', '专利', '商标', '版权', '隐私', '数据保护'
                ],
                'weight': 1.0
            },
            'art': {
                'keywords': [
                    '艺术', '绘画', '音乐', '文学', '诗歌', '小说',
                    '电影', '戏剧', '舞蹈', '雕塑', '摄影', '设计',
                    '美术', '创作', '作品', '风格', '流派', '技法',
                    '审美', '文化', '传统', '现代', '当代', '经典',
                    '博物馆', '画廊', '展览', '收藏', '艺术家', '大师'
                ],
                'weight': 1.0
            },
            'sports': {
                'keywords': [
                    '体育', '运动', '比赛', '竞技', '训练', '健身',
                    '足球', '篮球', '网球', '游泳', '跑步', '自行车',
                    '奥运会', '世界杯', '锦标赛', '联赛', '季后赛',
                    '运动员', '教练', '裁判', '团队', '个人', '记录',
                    '体能', '技术', '战术', '策略', '装备', '场地'
                ],
                'weight': 1.0
            },
            'general': {
                'keywords': [
                    '日常', '生活', '常识', '基本', '普通', '一般',
                    '简单', '容易', '基础', '入门', '初级', '常见'
                ],
                'weight': 0.5
            }
        }

        self.interdisciplinary_indicators = [
            '跨领域', '交叉学科', '多学科', '综合', '融合',
            '应用于', '结合', '相关性', '联系', '关联'
        ]

    async def analyze(self, question: str) -> Dict[str, Any]:
        domain_scores = self._calculate_domain_scores(question)
        primary_domain = self._identify_primary_domain(domain_scores)
        is_interdisciplinary = self._check_interdisciplinary(question)
        confidence = self._calculate_confidence(domain_scores)

        return {
            'primary_domain': primary_domain,
            'domain_scores': domain_scores,
            'is_interdisciplinary': is_interdisciplinary,
            'confidence': confidence,
            'domain_type': self._classify_domain_type(primary_domain, is_interdisciplinary, confidence)
        }

    def _calculate_domain_scores(self, question: str) -> Dict[str, float]:
        question_lower = question.lower()
        domain_scores = {}

        for domain, config in self.domain_keywords.items():
            score = 0.0
            keywords = config['keywords']
            weight = config['weight']

            for keyword in keywords:
                if keyword.lower() in question_lower:
                    keyword_weight = self._calculate_keyword_weight(keyword, question)
                    score += keyword_weight * weight

            if score > 0:
                score = score / len(keywords) * 100

            domain_scores[domain] = score

        return domain_scores

    def _calculate_keyword_weight(self, keyword: str, question: str) -> float:
        base_weight = 1.0

        if len(keyword) >= 4:
            base_weight += 0.5

        keyword_count = question.lower().count(keyword.lower())
        if keyword_count > 1:
            base_weight += (keyword_count - 1) * 0.3

        question_length = len(question)
        if question_length < 20:
            base_weight += 0.3

        return base_weight

    def _identify_primary_domain(self, domain_scores: Dict[str, float]) -> str:
        if not domain_scores:
            return 'general'

        max_score = max(domain_scores.values())
        if max_score == 0:
            return 'general'

        primary_domains = [domain for domain, score in domain_scores.items() if score == max_score]

        if len(primary_domains) == 1:
            return primary_domains[0]

        priority_order = ['technology', 'science', 'medicine', 'business', 'law', 'education', 'art', 'sports',
                          'general']
        for domain in priority_order:
            if domain in primary_domains:
                return domain

        return primary_domains[0]

    def _check_interdisciplinary(self, question: str) -> bool:
        question_lower = question.lower()

        for indicator in self.interdisciplinary_indicators:
            if indicator in question_lower:
                return True

        domain_scores = self._calculate_domain_scores(question)
        significant_domains = [domain for domain, score in domain_scores.items() if score > 10 and domain != 'general']

        return len(significant_domains) >= 2

    def _calculate_confidence(self, domain_scores: Dict[str, float]) -> float:
        if not domain_scores:
            return 0.0

        max_score = max(domain_scores.values())
        if max_score == 0:
            return 0.0

        sorted_scores = sorted(domain_scores.values(), reverse=True)

        if len(sorted_scores) == 1:
            confidence = min(max_score / 50, 1.0)
        else:
            score_diff = sorted_scores[0] - sorted_scores[1]
            confidence = min((max_score + score_diff) / 100, 1.0)

        return confidence

    def _classify_domain_type(self, primary_domain: str, is_interdisciplinary: bool, confidence: float) -> str:
        if is_interdisciplinary:
            return 'interdisciplinary'
        elif primary_domain == 'general' or confidence < 0.3:
            return 'general'
        elif primary_domain in ['technology', 'science', 'medicine', 'law'] and confidence > 0.7:
            return 'professional'
        elif confidence > 0.5:
            return 'specialized'
        else:
            return 'general'