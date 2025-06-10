import time
import asyncio
import hashlib
import json
import pickle
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta


class CacheManager:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
        self.cache_levels = {
            'memory': MemoryCache(max_size // 2, default_ttl),
            'persistent': PersistentCache(max_size // 2, default_ttl * 24)
        }

    async def get(self, key: str, level: str = 'memory') -> Optional[Any]:
        cache_key = self._generate_cache_key(key)

        if level in self.cache_levels:
            result = await self.cache_levels[level].get(cache_key)
            if result is not None:
                self.hit_count += 1
                return result

        for cache_level in self.cache_levels.values():
            result = await cache_level.get(cache_key)
            if result is not None:
                self.hit_count += 1
                if level in self.cache_levels:
                    await self.cache_levels[level].set(cache_key, result)
                return result

        self.miss_count += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None, level: str = 'memory') -> bool:
        cache_key = self._generate_cache_key(key)

        if level in self.cache_levels:
            return await self.cache_levels[level].set(cache_key, value, ttl)

        return False

    async def delete(self, key: str, level: Optional[str] = None) -> bool:
        cache_key = self._generate_cache_key(key)
        deleted = False

        if level and level in self.cache_levels:
            deleted = await self.cache_levels[level].delete(cache_key)
        else:
            for cache_level in self.cache_levels.values():
                if await cache_level.delete(cache_key):
                    deleted = True

        return deleted

    async def clear(self, level: Optional[str] = None):
        if level and level in self.cache_levels:
            await self.cache_levels[level].clear()
        else:
            for cache_level in self.cache_levels.values():
                await cache_level.clear()

        self.hit_count = 0
        self.miss_count = 0

    async def get_stats(self) -> Dict[str, Any]:
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0

        level_stats = {}
        for level_name, cache_level in self.cache_levels.items():
            level_stats[level_name] = await cache_level.get_stats()

        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'level_stats': level_stats
        }

    async def preload_knowledge(self, domains: List[str]):
        for domain in domains:
            cache_key = f"domain_knowledge_{domain}"
            existing = await self.get(cache_key, 'persistent')
            if existing is None:
                knowledge_data = await self._fetch_domain_knowledge(domain)
                await self.set(cache_key, knowledge_data, ttl=86400, level='persistent')

    async def _fetch_domain_knowledge(self, domain: str) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            'domain': domain,
            'knowledge_base': f"预加载的{domain}领域知识",
            'last_updated': datetime.now().isoformat(),
            'confidence': 0.9
        }

    def _generate_cache_key(self, key: str) -> str:
        if isinstance(key, str):
            return hashlib.md5(key.encode('utf-8')).hexdigest()
        else:
            serialized = json.dumps(key, sort_keys=True)
            return hashlib.md5(serialized.encode('utf-8')).hexdigest()


class MemoryCache:
    def __init__(self, max_size: int, default_ttl: int):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.expiry_times = {}

    async def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None

        if self._is_expired(key):
            await self.delete(key)
            return None

        self.access_times[key] = time.time()
        return self.cache[key]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if len(self.cache) >= self.max_size and key not in self.cache:
            await self._evict_lru()

        ttl = ttl or self.default_ttl
        current_time = time.time()

        self.cache[key] = value
        self.access_times[key] = current_time
        self.expiry_times[key] = current_time + ttl

        return True

    async def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            self.access_times.pop(key, None)
            self.expiry_times.pop(key, None)
            return True
        return False

    async def clear(self):
        self.cache.clear()
        self.access_times.clear()
        self.expiry_times.clear()

    async def get_stats(self) -> Dict[str, Any]:
        current_time = time.time()
        expired_count = sum(1 for key in self.expiry_times
                            if self.expiry_times[key] < current_time)

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'expired_entries': expired_count,
            'utilization': len(self.cache) / self.max_size
        }

    def _is_expired(self, key: str) -> bool:
        if key not in self.expiry_times:
            return True
        return time.time() > self.expiry_times[key]

    async def _evict_lru(self):
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        await self.delete(lru_key)


class PersistentCache:
    def __init__(self, max_size: int, default_ttl: int):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.memory_cache = {}
        self.metadata = {}

    async def get(self, key: str) -> Optional[Any]:
        if key in self.memory_cache:
            if not self._is_expired(key):
                return self.memory_cache[key]
            else:
                await self.delete(key)

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if len(self.memory_cache) >= self.max_size and key not in self.memory_cache:
            await self._evict_oldest()

        ttl = ttl or self.default_ttl
        current_time = time.time()

        self.memory_cache[key] = value
        self.metadata[key] = {
            'created_at': current_time,
            'expires_at': current_time + ttl,
            'access_count': 0
        }

        return True

    async def delete(self, key: str) -> bool:
        if key in self.memory_cache:
            del self.memory_cache[key]
            self.metadata.pop(key, None)
            return True
        return False

    async def clear(self):
        self.memory_cache.clear()
        self.metadata.clear()

    async def get_stats(self) -> Dict[str, Any]:
        current_time = time.time()
        expired_count = sum(1 for meta in self.metadata.values()
                            if meta['expires_at'] < current_time)

        return {
            'size': len(self.memory_cache),
            'max_size': self.max_size,
            'expired_entries': expired_count,
            'utilization': len(self.memory_cache) / self.max_size
        }

    def _is_expired(self, key: str) -> bool:
        if key not in self.metadata:
            return True
        return time.time() > self.metadata[key]['expires_at']

    async def _evict_oldest(self):
        if not self.metadata:
            return

        oldest_key = min(self.metadata.keys(),
                         key=lambda k: self.metadata[k]['created_at'])
        await self.delete(oldest_key)