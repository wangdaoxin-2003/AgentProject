from typing import Any
from intent import IntentRecognizer# 识别用户意图
from schemas import AgentResponse# 返回执行结果
from path_handler_registry import PathHandlerRegistry#路径注册仓库
from path_selector import PathSelector, PathType  # 选择执行路径
import logging


logger = logging.getLogger(__name__)

class AgentRuntime:  # Agent运行控制器

    def __init__(self,
                 intent_recognizer: IntentRecognizer,
                 path_selector: PathSelector,
                 path_handler_registry: PathHandlerRegistry
                 ):
        self.intent_recognizer = intent_recognizer
        self.path_selector = path_selector
        self.path_handler_registry = path_handler_registry

    def run(self, message: str, user_id: str,workflow_inputs:dict[str,Any]| None=None) -> AgentResponse:
        intent = "unknown"
        execution_path = "unknown"
        try:
            intent = self.intent_recognizer.recognize(message)
            path = self.path_selector.select(intent)
            # print(f"执行路径选择：{path}")
            logger.info("execution path selected: user_id=%s intent=%s path=%s",user_id,intent,path.value)

            handler = self.path_handler_registry.get_handler(path)
            if handler is None:
                logger.warning(
                    "path handler not found: user_id=%s intent=%s path=%s",
                    user_id,
                    intent,
                    path.value
                )

                return AgentResponse(
                    message="未找到对应的路径处理器",
                    user_id=user_id,
                    intent=intent,
                    execution_path=path.value,
                    status="failed",
                    result=None,
                    error="PATH_HANDLER_NOT_FOUND"
                )
            if path == PathType.WORKFLOW:
                return handler.handle(
                    message=message,
                    user_id=user_id,
                    intent=intent,
                    workflow_inputs=workflow_inputs)
            return handler.handle(
                message=message,
                user_id=user_id,
                intent=intent
            )
        except Exception as e:  # 负责捕获未预料到的系统异常

            logger.exception(
                "agent runtime execution failed: user_id=%s",
                user_id
            )
            return AgentResponse(
                message="Agent Runtime 执行失败",
                user_id=user_id,
                intent=intent,
                execution_path=execution_path,
                status="failed",
                result=None,
                error=str(e)
            )
