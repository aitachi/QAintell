import asyncio
import aiohttp
from typing import Dict, Any
from .tool_registry import BaseTool


class TranslatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="translator",
            description="文本翻译工具，支持多种语言互译",
            version="1.0"
        )
        self.capabilities = ["text_translation", "language_detection", "multi_language"]
        self.dependencies = []
        self.timeout = 8.0
        self.retry_count = 2

        self.supported_languages = {
            'zh': '中文',
            'en': '英文',
            'ja': '日文',
            'ko': '韩文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文',
            'ru': '俄文'
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get('text', '')
        target_language = params.get('target_language', 'en')
        source_language = params.get('source_language', 'auto')
        translation_service = params.get('service', 'mock')

        if translation_service == 'mock':
            return await self._mock_translation(text, source_language, target_language)
        else:
            return await self._real_translation(text, source_language, target_language, translation_service)

    def validate_params(self, params: Dict[str, Any]) -> bool:
        text = params.get('text', '')
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            return False

        if len(text) > 5000:
            return False

        target_language = params.get('target_language', 'en')
        if target_language not in self.supported_languages:
            return False

        return True

    async def _mock_translation(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        await asyncio.sleep(1.0)

        detected_source = self._detect_language(text) if source_lang == 'auto' else source_lang

        translation_map = {
            ('zh', 'en'): self._chinese_to_english,
            ('en', 'zh'): self._english_to_chinese,
            ('zh', 'ja'): self._chinese_to_japanese,
            ('en', 'ja'): self._english_to_japanese
        }

        translation_func = translation_map.get((detected_source, target_lang))

        if translation_func:
            translated_text = translation_func(text)
        else:
            translated_text = f"[{self.supported_languages.get(target_lang, target_lang)}] {text}"

        return {
            "translated_text": translated_text,
            "original_text": text,
            "source_language": detected_source,
            "target_language": target_lang,
            "confidence": 0.95,
            "translation_time": 1.0,
            "status": "success"
        }

    async def _real_translation(self, text: str, source_lang: str, target_lang: str, service: str) -> Dict[str, Any]:
        try:
            if service == 'google':
                return await self._google_translate(text, source_lang, target_lang)
            elif service == 'baidu':
                return await self._baidu_translate(text, source_lang, target_lang)
            else:
                return await self._mock_translation(text, source_lang, target_lang)
        except Exception as e:
            return {
                "translated_text": text,
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "error": str(e),
                "status": "error"
            }

    def _detect_language(self, text: str) -> str:
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
        japanese_chars = sum(1 for char in text if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff')

        total_chars = len([c for c in text if c.isalpha() or '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff'])

        if total_chars == 0:
            return 'en'

        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars
        japanese_ratio = japanese_chars / total_chars

        if chinese_ratio > 0.3:
            return 'zh'
        elif japanese_ratio > 0.1:
            return 'ja'
        elif english_ratio > 0.5:
            return 'en'
        else:
            return 'zh'

    def _chinese_to_english(self, text: str) -> str:
        simple_translations = {
            '你好': 'Hello',
            '谢谢': 'Thank you',
            '再见': 'Goodbye',
            '是': 'Yes',
            '不是': 'No',
            '什么': 'What',
            '如何': 'How',
            '为什么': 'Why',
            '哪里': 'Where',
            '什么时候': 'When',
            '计算': 'calculation',
            '搜索': 'search',
            '翻译': 'translation',
            '知识': 'knowledge',
            '问题': 'question',
            '回答': 'answer'
        }

        for chinese, english in simple_translations.items():
            text = text.replace(chinese, english)

        return f"[EN] {text}"

    def _english_to_chinese(self, text: str) -> str:
        simple_translations = {
            'Hello': '你好',
            'Thank you': '谢谢',
            'Goodbye': '再见',
            'Yes': '是',
            'No': '不是',
            'What': '什么',
            'How': '如何',
            'Why': '为什么',
            'Where': '哪里',
            'When': '什么时候',
            'calculation': '计算',
            'search': '搜索',
            'translation': '翻译',
            'knowledge': '知识',
            'question': '问题',
            'answer': '回答'
        }

        for english, chinese in simple_translations.items():
            text = text.replace(english, chinese)

        return f"[ZH] {text}"

    def _chinese_to_japanese(self, text: str) -> str:
        return f"[JA] {text}です"

    def _english_to_japanese(self, text: str) -> str:
        return f"[JA] {text}です"

    async def _google_translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        api_key = "YOUR_GOOGLE_TRANSLATE_API_KEY"
        url = "https://translation.googleapis.com/language/translate/v2"

        params = {
            'key': api_key,
            'q': text,
            'source': source_lang if source_lang != 'auto' else '',
            'target': target_lang,
            'format': 'text'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params) as response:
                if response.status == 200:
                    data = await response.json()
                    translation = data['data']['translations'][0]

                    return {
                        "translated_text": translation['translatedText'],
                        "original_text": text,
                        "source_language": translation.get('detectedSourceLanguage', source_lang),
                        "target_language": target_lang,
                        "confidence": 0.9,
                        "translation_time": 2.0,
                        "status": "success"
                    }
                else:
                    raise Exception(f"Google Translate API error: {response.status}")

    async def _baidu_translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        app_id = "YOUR_BAIDU_APP_ID"
        secret_key = "YOUR_BAIDU_SECRET_KEY"

        import hashlib
        import random
        import time

        salt = str(random.randint(32768, 65536))
        timestamp = str(int(time.time()))
        sign_str = app_id + text + salt + timestamp + secret_key
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

        params = {
            'q': text,
            'from': 'auto' if source_lang == 'auto' else source_lang,
            'to': target_lang,
            'appid': app_id,
            'salt': salt,
            'sign': sign
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params) as response:
                if response.status == 200:
                    data = await response.json()

                    if 'trans_result' in data:
                        translation = data['trans_result'][0]['dst']
                        detected_lang = data.get('from', source_lang)

                        return {
                            "translated_text": translation,
                            "original_text": text,
                            "source_language": detected_lang,
                            "target_language": target_lang,
                            "confidence": 0.85,
                            "translation_time": 1.5,
                            "status": "success"
                        }
                    else:
                        raise Exception(f"Baidu Translate error: {data}")
                else:
                    raise Exception(f"Baidu Translate API error: {response.status}")