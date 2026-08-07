
from intent import IntentRecognizer# 识别用户意图
from schemas import AgentResponse# 返回执行结果
from path_handler_registry import PathHandlerRegistry#路径注册仓库
from path_selector import PathSelector# 选择执行路径


class AgentRuntime:  # Agent运行控制器

    def __init__(self,
                 intent_recognizer: IntentRecognizer,
                 path_selector: PathSelector,
                 path_handler_registry: PathHandlerRegistry
                 ):
        self.intent_recognizer = intent_recognizer
        self.path_selector = path_selector
        self.path_handler_registry = path_handler_registry

    def run(self, message: str, user_id: str) -> AgentResponse:
        intent = "unknown"
        execution_path = "unknown"
        try:
            intent = self.intent_recognizer.recognize(message)
            path = self.path_selector.select(intent)
            print(f"执行路径选择：{path}")
            handler = self.path_handler_registry.get_handler(path)
            if handler is None:
                return AgentResponse(
                    message="未找到对应的路径处理器",
                    user_id=user_id,
                    intent=intent,
                    execution_path=path.value,
                    status="failed",
                    result=None,
                    error="PATH_HANDLER_NOT_FOUND"
                )
            return handler.handle(message=message, user_id=user_id, intent=intent)
        except Exception as e:  # 负责捕获未预料到的系统异常
            return AgentResponse(
                message="Agent Runtime 执行失败",
                user_id=user_id,
                intent=intent,
                execution_path=execution_path,
                status="failed",
                result=None,
                error=str(e)
            )
