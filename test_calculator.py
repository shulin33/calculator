"""
计算器测试脚本 - 非图形界面，通过单元测试验证计算器逻辑
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# 模拟 tkinter 以便在无 GUI 环境下导入
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()

# 导入待测模块
import calculator


class TestFormatNumber(unittest.TestCase):
    """测试 _format_number 静态方法"""

    def test_integer(self):
        self.assertEqual(calculator.CalculatorApp._format_number(42), "42")

    def test_large_integer(self):
        self.assertEqual(calculator.CalculatorApp._format_number(1234567), "1,234,567")

    def test_negative_integer(self):
        self.assertEqual(calculator.CalculatorApp._format_number(-42), "-42")

    def test_float(self):
        self.assertEqual(calculator.CalculatorApp._format_number(3.14), "3.14")

    def test_very_small_float(self):
        # 1e-10 级别，应显示为科学计数法
        result = calculator.CalculatorApp._format_number(0.0000000001)
        self.assertEqual(result, "1e-10")

    def test_very_large_float(self):
        # 大整数会加千分位分隔符
        result = calculator.CalculatorApp._format_number(1e15)
        self.assertEqual(result, "1,000,000,000,000,000")

    def test_infinity(self):
        self.assertEqual(calculator.CalculatorApp._format_number(float("inf")), "Invalid")

    def test_nan(self):
        self.assertEqual(calculator.CalculatorApp._format_number(float("nan")), "Invalid")

    def test_zero(self):
        self.assertEqual(calculator.CalculatorApp._format_number(0), "0")

    def test_negative_zero(self):
        # -0.0 == 0.0, 所以 int(-0.0) == 0
        result = calculator.CalculatorApp._format_number(-0.0)
        self.assertEqual(result, "0")


class TestBasicOperations(unittest.TestCase):
    """测试基本四则运算"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        # Mock expr_label
        self.calc.expr_label = MagicMock()

    def test_addition(self):
        self.calc.current_text = "3"
        self.calc.previous_text = "5"
        self.calc.operation = "+"
        self.calc.should_reset_display = False
        result = self.calc._apply_op(5, 3, "+")
        self.assertAlmostEqual(result, 8)

    def test_subtraction(self):
        result = self.calc._apply_op(10, 3, "−")
        self.assertAlmostEqual(result, 7)

    def test_multiplication(self):
        result = self.calc._apply_op(4, 3, "×")
        self.assertAlmostEqual(result, 12)

    def test_division(self):
        result = self.calc._apply_op(10, 4, "÷")
        self.assertAlmostEqual(result, 2.5)

    def test_division_by_zero(self):
        result = self.calc._apply_op(10, 0, "÷")
        self.assertTrue(result == float("inf"))

    def test_unknown_operator(self):
        result = self.calc._apply_op(5, 3, "?")
        self.assertAlmostEqual(result, 3)


class TestDigitInput(unittest.TestCase):
    """测试数字输入"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_input_single_digit(self):
        self.calc._input_digit("5")
        self.assertEqual(self.calc.current_text, "5")

    def test_input_multiple_digits(self):
        self.calc._input_digit("1")
        self.calc._input_digit("2")
        self.calc._input_digit("3")
        self.assertEqual(self.calc.current_text, "123")

    def test_input_resets_after_operation(self):
        self.calc.current_text = "123"
        self.calc.operation = "+"
        self.calc.previous_text = "123"
        self.calc.should_reset_display = True
        self.calc._input_digit("4")
        self.assertEqual(self.calc.current_text, "4")

    def test_input_max_digits(self):
        # 限制16位
        self.calc.current_text = "1" * 16
        self.calc._input_digit("5")
        self.assertEqual(len(self.calc.current_text), 16)

    def test_input_empty_string(self):
        self.calc.current_text = ""
        self.calc._input_digit("7")
        self.assertEqual(self.calc.current_text, "7")


class TestDecimalInput(unittest.TestCase):
    """测试小数点输入"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_input_decimal(self):
        self.calc.current_text = "123"
        self.calc._input_decimal()
        self.assertEqual(self.calc.current_text, "123.")

    def test_no_duplicate_decimal(self):
        self.calc.current_text = "123."
        self.calc._input_decimal()
        self.assertEqual(self.calc.current_text, "123.")

    def test_decimal_resets_after_operation(self):
        self.calc.should_reset_display = True
        self.calc._input_decimal()
        self.assertEqual(self.calc.current_text, "0.")


class TestOperationChaining(unittest.TestCase):
    """测试连续运算"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_chain_add_multiply(self):
        # 5 + 3 = 8
        self.calc.current_text = "5"
        self.calc._input_operation("+")
        self.calc.current_text = "3"
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "8")

        # 8 × 2 = 16
        self.calc._input_operation("×")
        self.calc.current_text = "2"
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "16")

    def test_chained_operations_intermediate(self):
        # 1 + 2 + 3 -> 应该先算 1+2=3，然后等待输入
        self.calc.current_text = "1"
        self.calc._input_operation("+")
        self.calc.current_text = "2"
        self.calc._input_operation("+")
        # 此时应该已经算完 1+2=3
        self.assertEqual(self.calc.current_text, "3")
        self.assertEqual(self.calc.previous_text, "3")
        self.assertEqual(self.calc.operation, "+")


class TestSpecialFunctions(unittest.TestCase):
    """测试特殊功能"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_percent(self):
        self.calc.current_text = "50"
        self.calc._percent()
        self.assertEqual(self.calc.current_text, "0.5")

    def test_percent_float(self):
        self.calc.current_text = "100.5"
        self.calc._percent()
        self.assertAlmostEqual(float(self.calc.current_text), 1.005)

    def test_negate_positive_to_negative(self):
        self.calc.current_text = "42"
        self.calc._negate()
        self.assertEqual(self.calc.current_text, "-42")

    def test_negate_negative_to_positive(self):
        self.calc.current_text = "-42"
        self.calc._negate()
        self.assertEqual(self.calc.current_text, "42")

    def test_negate_zero(self):
        self.calc.current_text = "0"
        self.calc._negate()
        self.assertEqual(self.calc.current_text, "0")  # 不应变化

    def test_negate_empty(self):
        self.calc.current_text = ""
        self.calc._negate()
        self.assertEqual(self.calc.current_text, "")  # 不应变化

    def test_square(self):
        self.calc.current_text = "5"
        self.calc._square()
        self.assertEqual(self.calc.current_text, "25")

    def test_square_negative(self):
        self.calc.current_text = "-3"
        self.calc._square()
        self.assertEqual(self.calc.current_text, "9")

    def test_reciprocal(self):
        self.calc.current_text = "4"
        self.calc._reciprocal()
        self.assertAlmostEqual(float(self.calc.current_text), 0.25)

    def test_reciprocal_zero(self):
        self.calc.current_text = "0"
        self.calc._reciprocal()
        self.assertEqual(self.calc.current_text, "Invalid")

    def test_sqrt_positive(self):
        self.calc.current_text = "16"
        self.calc._sqrt()
        self.assertEqual(self.calc.current_text, "4")

    def test_sqrt_negative(self):
        self.calc.current_text = "-4"
        self.calc._sqrt()
        self.assertEqual(self.calc.current_text, "Invalid")

    def test_sqrt_zero(self):
        self.calc.current_text = "0"
        self.calc._sqrt()
        self.assertEqual(self.calc.current_text, "0")


class TestBackspace(unittest.TestCase):
    """测试退格功能"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_backspace(self):
        self.calc.current_text = "123"
        self.calc._backspace()
        self.assertEqual(self.calc.current_text, "12")

    def test_backspace_empty(self):
        self.calc.current_text = ""
        self.calc._backspace()
        self.assertEqual(self.calc.current_text, "")  # 可能报错，需要检查

    def test_backspace_disabled_when_reset(self):
        self.calc.should_reset_display = True
        self.calc.current_text = "123"
        self.calc._backspace()
        self.assertEqual(self.calc.current_text, "123")  # 不应变化


class TestClear(unittest.TestCase):
    """测试清除功能"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = "123"
        self.calc.previous_text = "456"
        self.calc.operation = "+"
        self.calc.should_reset_display = True
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_clear_all(self):
        self.calc._clear_all()
        self.assertEqual(self.calc.current_text, "")
        self.assertEqual(self.calc.previous_text, "")
        self.assertIsNone(self.calc.operation)

    def test_clear_entry(self):
        self.calc._clear_entry()
        self.assertEqual(self.calc.current_text, "")
        # previous_text 和 operation 应保留
        self.assertEqual(self.calc.previous_text, "456")
        self.assertEqual(self.calc.operation, "+")


class TestDisplayUpdate(unittest.TestCase):
    """测试显示更新"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_update_display_empty(self):
        self.calc.current_text = ""
        self.calc._update_display()
        self.calc.display_var.set.assert_called_with("0")

    def test_update_display_value(self):
        self.calc.current_text = "123"
        self.calc._update_display()
        self.calc.display_var.set.assert_called_with("123")


class TestEdgeCases(unittest.TestCase):
    """测试边界情况和潜在bug"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_calculate_without_operation(self):
        self.calc.current_text = "42"
        self.calc._calculate()
        # 不应改变状态
        self.assertEqual(self.calc.current_text, "42")

    def test_backspace_on_empty_string(self):
        # BUG: 空字符串切片会返回空字符串，不会报错
        self.calc.current_text = ""
        self.calc._backspace()
        # 这不会崩溃，但也不做任何事 — 这是合理的

    def test_input_operation_with_current_empty(self):
        self.calc.current_text = ""
        self.calc.previous_text = "10"
        self.calc.operation = "+"
        self.calc._input_operation("−")
        # 应该切换操作符
        self.assertEqual(self.calc.operation, "−")

    def test_long_number_format(self):
        # 测试大数格式化
        result = calculator.CalculatorApp._format_number(123456789012345)
        self.assertEqual(result, "123,456,789,012,345")

    def test_scientific_notation_format(self):
        result = calculator.CalculatorApp._format_number(1e20)
        self.assertEqual(result, "1e+20")

    def test_very_precise_float(self):
        # 浮点精度问题
        result = calculator.CalculatorApp._format_number(0.1 + 0.2)
        # 0.1 + 0.2 = 0.30000000000000004
        # .10g 应该输出 "0.3"
        self.assertEqual(result, "0.3")

    def test_multiply_chains_precision(self):
        # 测试连续乘法精度
        self.calc.current_text = "0.1"
        self.calc._input_operation("×")
        self.calc.current_text = "0.2"
        self.calc._calculate()
        # 0.1 * 0.2 = 0.020000000000000004
        # 格式化后应该是 "0.02"
        self.assertEqual(self.calc.current_text, "0.02")


class TestFullScenarios(unittest.TestCase):
    """测试完整使用场景"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.current_text = ""
        self.calc.previous_text = ""
        self.calc.operation = None
        self.calc.should_reset_display = False
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()
        self.calc.expr_label = MagicMock()

    def test_simple_addition(self):
        """5 + 3 = 8"""
        self.calc._input_digit("5")
        self.calc._input_operation("+")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "8")

    def test_expression_display(self):
        """验证表达式显示是否正确"""
        self.calc._input_digit("5")
        self.calc._input_operation("+")
        # 表达式应该显示 "5 +"
        self.calc.expr_label.config.assert_called()
        call_args = self.calc.expr_label.config.call_args
        self.assertIn("text", str(call_args))

    def test_complex_calculation(self):
        """(2 + 3) × 4 = 20"""
        self.calc._input_digit("2")
        self.calc._input_operation("+")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "5")

        self.calc._input_operation("×")
        self.calc._input_digit("4")
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "20")

    def test_percentage_in_chain(self):
        """100 + 10% = 110"""
        self.calc._input_digit("1")
        self.calc._input_digit("0")
        self.calc._input_digit("0")
        self.calc._input_operation("+")
        self.calc._input_digit("1")
        self.calc._input_digit("0")
        self.calc._percent()
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "110")

    def test_division_by_zero_flow(self):
        """10 ÷ 0 = Invalid"""
        self.calc._input_digit("1")
        self.calc._input_digit("0")
        self.calc._input_operation("÷")
        self.calc._input_digit("0")
        self.calc._calculate()
        self.assertEqual(self.calc.current_text, "Invalid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
