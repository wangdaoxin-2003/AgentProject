from enum import Enum


class PathType(Enum):
    FAST = "fast"
    LLM = "llm"
    WORKFLOW = "workflow"
    RAG = "rag"


class PathSelector:
    def select(self, intent: str) -> PathType:
        if intent in ["weather", "calculator"]:
            return PathType.FAST
        if intent in ["chat"]:
            return PathType.LLM
        if intent in ["workflow", "double_calculation"]:
            return PathType.WORKFLOW
        if intent in "knowledge_query":
            return PathType.RAG
        return PathType.FAST
