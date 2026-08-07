from enum import Enum


class PathType(Enum):
    FAST = "fast"
    LLM = "llm"
    WORKFLOW = "workflow"


class PathSelector:
    def select(self, intent: str) ->PathType:
        if intent in ["weather", "calculator"]:
            return PathType.FAST
        if intent in ["chat"]:
            return PathType.LLM
        if intent in ["workflow"]:
            return PathType.WORKFLOW
        return PathType.FAST
