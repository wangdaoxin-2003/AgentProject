class IntentRecognizer:  # 意图识别器
    def recognize(self, message: str) -> str:
        if message.strip().startswith("知识库："):
            return "knowledge_query"
        if "天气" in message:
            return "weather"
        if "双计算" in message:
            return "double_calculation"
        if "工作" in message or "干活" in message:
            return "workflow"
        return "chat"  # 默认意图
