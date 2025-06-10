import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from .tool_registry import BaseTool


class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="搜索网络信息，获取最新的资讯和数据",
            version="1.0"
        )
        self.capabilities = ["search", "real_time_info", "news", "general_info"]
        self.dependencies = []
        self.timeout = 15.0
        self.retry_count = 2
        self.search_engines = {
            "bing": "https://api.bing.microsoft.com/v7.0/search",
            "google": "https://www.googleapis.com/customsearch/v1",
            "baidu": "https://www.baidu.com/s"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get('query', '')
        max_results = params.get('max_results', 5)
        language = params.get('language', 'zh-CN')
        search_engine = params.get('search_engine', 'mock')

        if search_engine == 'mock':
            return await self._mock_search(query, max_results, language)
        else:
            return await self._real_search(query, max_results, language, search_engine)

    def validate_params(self, params: Dict[str, Any]) -> bool:
        required_params = ['query']
        for param in required_params:
            if param not in params:
                return False

        query = params.get('query', '')
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False

        max_results = params.get('max_results', 5)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return False

        return True

    async def _mock_search(self, query: str, max_results: int, language: str) -> Dict[str, Any]:
        await asyncio.sleep(1)

        mock_results = [
            {
                "title": f"关于 '{query}' 的搜索结果 1",
                "url": f"https://example.com/result1?q={query}",
                "snippet": f"这是关于 {query} 的详细信息。包含了相关的背景知识和最新动态。",
                "published_date": "2024-12-01",
                "source": "示例网站1",
                "relevance_score": 0.95
            },
            {
                "title": f"'{query}' 最新发展和趋势分析",
                "url": f"https://news.example.com/analysis?topic={query}",
                "snippet": f"最新报告显示，{query} 领域出现了重要进展，专家分析认为这将带来重大影响。",
                "published_date": "2024-11-30",
                "source": "新闻网站",
                "relevance_score": 0.88
            },
            {
                "title": f"{query} 完整指南和教程",
                "url": f"https://tutorial.example.com/guide/{query}",
                "snippet": f"全面的 {query} 学习资源，包括基础概念、实践案例和高级技巧。",
                "published_date": "2024-11-28",
                "source": "教程网站",
                "relevance_score": 0.82
            },
            {
                "title": f"{query} 常见问题解答",
                "url": f"https://faq.example.com/{query}",
                "snippet": f"收集了关于 {query} 的常见问题和专业回答，帮助用户快速理解核心概念。",
                "published_date": "2024-11-25",
                "source": "FAQ网站",
                "relevance_score": 0.75
            },
            {
                "title": f"{query} 社区讨论和经验分享",
                "url": f"https://forum.example.com/topic/{query}",
                "snippet": f"用户在社区中分享的 {query} 相关经验，包含实用技巧和解决方案。",
                "published_date": "2024-11-20",
                "source": "技术论坛",
                "relevance_score": 0.68
            }
        ]

        selected_results = mock_results[:max_results]

        return {
            "results": selected_results,
            "total_results": len(selected_results),
            "search_query": query,
            "language": language,
            "search_time": 1.0,
            "status": "success"
        }

    async def _real_search(self, query: str, max_results: int, language: str, search_engine: str) -> Dict[str, Any]:
        try:
            if search_engine == "bing":
                return await self._bing_search(query, max_results, language)
            elif search_engine == "google":
                return await self._google_search(query, max_results, language)
            else:
                return await self._mock_search(query, max_results, language)
        except Exception as e:
            return {
                "results": [],
                "total_results": 0,
                "search_query": query,
                "language": language,
                "error": str(e),
                "status": "error"
            }

    async def _bing_search(self, query: str, max_results: int, language: str) -> Dict[str, Any]:
        headers = {
            "Ocp-Apim-Subscription-Key": "YOUR_BING_API_KEY"
        }

        params = {
            "q": query,
            "count": max_results,
            "mkt": language,
            "responseFilter": "webPages"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_engines["bing"], headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_bing_results(data, query, language)
                else:
                    raise Exception(f"Bing API error: {response.status}")

    async def _google_search(self, query: str, max_results: int, language: str) -> Dict[str, Any]:
        params = {
            "key": "YOUR_GOOGLE_API_KEY",
            "cx": "YOUR_SEARCH_ENGINE_ID",
            "q": query,
            "num": max_results,
            "lr": f"lang_{language[:2]}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_engines["google"], params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_google_results(data, query, language)
                else:
                    raise Exception(f"Google API error: {response.status}")

    def _parse_bing_results(self, data: Dict[str, Any], query: str, language: str) -> Dict[str, Any]:
        results = []

        web_pages = data.get("webPages", {}).get("value", [])

        for item in web_pages:
            results.append({
                "title": item.get("name", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
                "published_date": item.get("dateLastCrawled", ""),
                "source": self._extract_domain(item.get("url", "")),
                "relevance_score": 0.8
            })

        return {
            "results": results,
            "total_results": len(results),
            "search_query": query,
            "language": language,
            "search_time": 2.0,
            "status": "success"
        }

    def _parse_google_results(self, data: Dict[str, Any], query: str, language: str) -> Dict[str, Any]:
        results = []

        items = data.get("items", [])

        for item in items:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "published_date": "",
                "source": self._extract_domain(item.get("link", "")),
                "relevance_score": 0.8
            })

        return {
            "results": results,
            "total_results": len(results),
            "search_query": query,
            "language": language,
            "search_time": 2.0,
            "status": "success"
        }

    def _extract_domain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"