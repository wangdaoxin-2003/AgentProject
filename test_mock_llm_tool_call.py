from tools.calculator_tool import CalculatorTool


def test_string_input() -> None:
    calculator = CalculatorTool()

    result = calculator.execute("计算100+200")

    print("字符串输入结果：", result)

    assert result.success is True
    assert result.data is not None
    assert result.data["result"] == 300


def test_arguments_input() -> None:
    calculator = CalculatorTool()

    result = calculator.execute(
        {
            "expression": "100+200"
        }
    )

    print("字典输入结果：", result)

    assert result.success is True
    assert result.data is not None
    assert result.data["result"] == 300


def test_invalid_arguments() -> None:
    calculator = CalculatorTool()

    result = calculator.execute(
        {
            "wrong_key": "100+200"
        }
    )

    print("错误参数结果：", result)

    assert result.success is False
    assert result.error == "没有识别到有效的计算参数"


def main() -> None:
    test_string_input()
    test_arguments_input()
    test_invalid_arguments()

    print("CalculatorTool 输入兼容测试通过")


if __name__ == "__main__":
    main()