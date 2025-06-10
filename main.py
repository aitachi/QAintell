import asyncio
import sys
import json
from typing import Dict, Any
from core.scheduler import UnifiedScheduler
from config.settings import Settings
from utils.logging_utils import setup_logging


class IntelligentQASystem:
    def __init__(self):
        self.settings = Settings()
        self.logger = setup_logging()
        self.scheduler = UnifiedScheduler()

    async def initialize(self):
        await self.scheduler.initialize()
        self.logger.info("Intelligent QA System initialized successfully")

    async def process_question(self, question: str, user_context: Dict[str, Any] = None,
                               conversation_history: list = None):
        if user_context is None:
            user_context = {}
        if conversation_history is None:
            conversation_history = []

        try:
            result = await self.scheduler.process_question(question, user_context, conversation_history)
            return result
        except Exception as e:
            self.logger.error(f"Error processing question: {e}")
            return {"error": str(e), "response": "抱歉，处理您的问题时出现了错误。"}


async def main():
    system = IntelligentQASystem()
    await system.initialize()

    while True:
        try:
            question = input("\n请输入您的问题 (输入 'quit' 退出): ")
            if question.lower() in ['quit', 'exit', '退出']:
                break

            result = await system.process_question(question)
            print(f"\n回答: {result.get('response', '无法生成回答')}")
            print(f"置信度: {result.get('confidence', 0):.2f}")
            print(f"处理时间: {result.get('processing_time', 0):.2f}秒")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"错误: {e}")

    print("感谢使用智能问答系统！")


if __name__ == "__main__":
    asyncio.run(main())