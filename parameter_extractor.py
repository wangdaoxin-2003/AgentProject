import re#python自带的正则表达式模块
class ParameterExtractor:
    def extract_calculator_params(self,message:str):
        numbers = re.findall(r"\d+",message)#匹配数字 \d表示一个数字 +表示匹配一个或多个
        if len(numbers) < 2:
            return None
        operator =self.extract_operator(message)
        return {
            "number1":int(numbers[0]),
            "number2":int(numbers[1]),
            "operator":operator
        }

    def extract_operator(self,message:str):
       if "加" in message or "+" in message:
           return "add"
       if "减" in message or "-" in message:
           return "subtract"
       if "乘" in message or "*" in message:
           return "multiply"
       if "除" in message or "/" in message:
           return "divide"
       return None