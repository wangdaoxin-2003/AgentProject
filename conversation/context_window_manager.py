from schemas import LLMMessage


class ContextWindowManager:

    def __init__(self, max_tokens: int = 1000):
        if max_tokens <= 0:
            raise ValueError("max_tokens 必须大于0")
        self.max_tokens = max_tokens

    def estimate_tokens(self, message: LLMMessage) -> int:
        content = message.content or ""
        char_count = len(content)
        tokens = max(1, (char_count + 1) // 2)

        # 1.取出消息的 content
        # 2.如果 content为None，按空字符串处理
        # 3.计算字符数

        return tokens

    def trim_history(self, history_messages: list[LLMMessage],max_tokens:int|None=None) -> list[LLMMessage]:
        selected = []
        used_tokens = 0
        budget = self.max_tokens if max_tokens is None else max_tokens
        if budget < 0:
            raise ValueError("max_tokens 不能为负数")
        for message in reversed(history_messages):
            token = self.estimate_tokens(message)

            if used_tokens + token > budget:
                break
            selected.append(message)
            used_tokens += token
        return list(reversed(selected))  # reversed(selected)得到的时一个迭代器需要转化成标准列表

    def calculate_history_budget(
            self,
            model_context_limit: int,
            system_tokens: int,
            user_tokens: int,
            reserved_tokens: int
    ) -> int:
        # 1.计算剩余预算
        # 2.如果结果小于0，则返回0
        # 3.返回最终的历史消息预算
        if model_context_limit <= 0:
            raise ValueError("model_context_limit 必须大于0")
        if system_tokens < 0:
            raise ValueError("system_tokens 必须大于等于0")
        if user_tokens<0:
            raise ValueError("user_tokens 必须大于等于0")
        if reserved_tokens < 0:
            raise ValueError("reserved_tokens 必须大于等于0")
        history_tokens = (model_context_limit - user_tokens - system_tokens - reserved_tokens)
        if history_tokens < 0:
            return 0
        return history_tokens
