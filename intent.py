class IntentRecognizer:#意图识别器
    def recognize(self,message:str) ->str:
        if "天气" in message:
            return "weather"
        if "工作" in message or "干活" in message:
            return "workflow"
        return "chat"#默认意图