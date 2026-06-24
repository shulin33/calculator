"""
计算器测试脚本 v2 - 测试表达式引擎
"""

import sys
import unittest
from unittest.mock import MagicMock

sys.modules["tkinter"] = MagicMock()
sys.modules["tkinter.font"] = MagicMock()

import calculator


class TestExpressionEngine(unittest.TestCase):
    """测试表达式引擎"""

    def setUp(self):
        self.calc = calculator.CalculatorApp.__new__(calculator.CalculatorApp)
        self.calc.expr_buffer = ""
        self.calc.display_text = ""
        self.calc.just_calculated = False
        self.calc.open_parens = 0
        self.calc.expr_label = MagicMock()
        self.calc.display_var = MagicMock()
        self.calc.display_var.set = MagicMock()

    # --- 基本运算 ---
    def test_simple_addition(self):
        self.calc._input_digit("1")
        self.calc._input_digit("2")
        self.calc._input_operator("+")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "15")

    def test_chained_operations(self):
        """1 + 2 + 3 = 6"""
        self.calc._input_digit("1")
        self.calc._input_operator("+")
        self.calc._input_digit("2")
        self.calc._input_operator("+")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "6")

    def test_order_of_operations(self):
        """1 + 2 * 3 = 7 (优先级正确)"""
        self.calc._input_digit("1")
        self.calc._input_operator("+")
        self.calc._input_digit("2")
        self.calc._input_operator("*")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "7")

    def test_parentheses(self):
        """(1 + 2) * 3 = 9"""
        self.calc._input_left_paren()
        self.calc._input_digit("1")
        self.calc._input_operator("+")
        self.calc._input_digit("2")
        self.calc._input_right_paren()
        self.calc._input_operator("*")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "9")

    def test_nested_parentheses(self):
        """(1 + (2 * 3)) = 7"""
        self.calc._input_left_paren()
        self.calc._input_digit("1")
        self.calc._input_operator("+")
        self.calc._input_left_paren()
        self.calc._input_digit("2")
        self.calc._input_operator("*")
        self.calc._input_digit("3")
        self.calc._input_right_paren()
        self.calc._input_right_paren()
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "7")

    # --- 连续计算 ---
    def test_continue_after_equals(self):
        """5 + 3 = 8, 然后 + 2 = 10"""
        self.calc._input_digit("5")
        self.calc._input_operator("+")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "8")
        # 继续加
        self.calc._input_operator("+")
        self.calc._input_digit("2")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "10")

    def test_continue_multiply_after_equals(self):
        """4 * 3 = 12, 然后 - 5 = 7"""
        self.calc._input_digit("4")
        self.calc._input_operator("*")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "12")
        self.calc._input_operator("-")
        self.calc._input_digit("5")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "7")

    # --- 0 的显示 ---
    def test_zero_display(self):
        self.calc._input_digit("0")
        self.assertEqual(self.calc.display_var.set.call_args[0][0], "0")

    def test_zero_with_decimal(self):
        self.calc._input_digit("0")
        self.calc._input_decimal()
        self.calc._input_digit("5")
        self.assertEqual(self.calc.display_text, "0.5")

    def test_leading_zeros(self):
        """007 应该显示为 7"""
        self.calc._input_digit("0")
        self.calc._input_digit("0")
        self.calc._input_digit("7")
        self.calc._calculate()
        # 格式化后应为 "7"
        self.assertEqual(self.calc.display_text, "7")

    # --- 百分比 ---
    def test_percent_simple(self):
        """50% = 0.5"""
        self.calc._input_digit("5")
        self.calc._input_digit("0")
        self.calc._percent()
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "0.5")

    def test_percent_in_expression(self):
        """100 * 50% = 50"""
        self.calc._input_digit("1")
        self.calc._input_digit("0")
        self.calc._input_digit("0")
        self.calc._input_operator("*")
        self.calc._input_digit("5")
        self.calc._input_digit("0")
        self.calc._percent()
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "50")

    def test_percent_after_calculation(self):
        """5 + 3 = 8, 然后 % = 0.08"""
        self.calc._input_digit("5")
        self.calc._input_operator("+")
        self.calc._input_digit("3")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "8")
        self.calc._percent()
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "0.08")

    # --- 溢出处理 ---
    def test_overflow(self):
        """极大数应显示溢出提示"""
        self.calc.expr_buffer = "1e308 * 10"
        result = self.calc._evaluate(self.calc.expr_buffer)
        formatted = self.calc._format_number(result)
        # 溢出应显示 Infinity
        self.assertEqual(formatted, "Infinity")

    def test_division_by_zero(self):
        """10 ÷ 0 = Invalid"""
        self.calc._input_digit("1")
        self.calc._input_digit("0")
        self.calc._input_operator("÷")
        self.calc._input_digit("0")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "Invalid")

    # --- 特殊功能 ---
    def test_square(self):
        """5² = 25"""
        self.calc._input_digit("5")
        self.calc._square()
        self.assertEqual(self.calc.display_text, "25")

    def test_reciprocal(self):
        """1/4 = 0.25"""
        self.calc._input_digit("4")
        self.calc._reciprocal()
        self.assertEqual(self.calc.display_text, "0.25")

    def test_sqrt(self):
        """√16 = 4"""
        self.calc._input_digit("1")
        self.calc._input_digit("6")
        self.calc._sqrt()
        self.assertEqual(self.calc.display_text, "4")

    def test_negate(self):
        """-5"""
        self.calc._input_digit("5")
        self.calc._negate()
        self.assertEqual(self.calc.display_text, "-5")

    # --- 括号闭合 ---
    def test_auto_close_paren(self):
        """(1+2 按 = 应自动补右括号"""
        self.calc._input_left_paren()
        self.calc._input_digit("1")
        self.calc._input_operator("+")
        self.calc._input_digit("2")
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "3")

    # --- 隐式乘法 ---
    def test_implicit_multiplication(self):
        """2(3) = 6"""
        self.calc._input_digit("2")
        self.calc._input_left_paren()
        self.calc._input_digit("3")
        self.calc._input_right_paren()
        self.calc._calculate()
        self.assertEqual(self.calc.display_text, "6")

    # --- 清除 ---
    def test_clear_restores_zero(self):
        self.calc._input_digit("1")
        self.calc._input_digit("2")
        self.calc._clear_all()
        self.assertEqual(self.calc.expr_buffer, "")
        self.assertEqual(self.calc.display_text, "")

    def test_backspace(self):
        self.calc._input_digit("1")
        self.calc._input_digit("2")
        self.calc._input_digit("3")
        self.calc._backspace()
        self.assertEqual(self.calc.display_text, "12")

    def test_backspace_disabled_after_equals(self):
        self.calc._input_digit("1")
        self.calc._input_digit("2")
        self.calc._calculate()
        self.calc._backspace()
        # 按完后退格无效
        self.assertEqual(self.calc.display_text, "12")


class TestFormatNumber(unittest.TestCase):
    """测试数字格式化"""

    def test_normal_integer(self):
        self.assertEqual(calculator.CalculatorApp._format_number(42), "42")

    def test_large_integer(self):
        self.assertEqual(calculator.CalculatorApp._format_number(1234567), "1,234,567")

    def test_float_precision(self):
        # 0.1 + 0.2 浮点精度
        result = calculator.CalculatorApp._format_number(0.1 + 0.2)
        self.assertEqual(result, "0.3")

    def test_very_large(self):
        result = calculator.CalculatorApp._format_number(1e20)
        self.assertIn("e", result.lower())

    def test_very_small(self):
        result = calculator.CalculatorApp._format_number(1e-10)
        self.assertEqual(result, "1e-10")

    def test_zero(self):
        self.assertEqual(calculator.CalculatorApp._format_number(0), "0")

    def test_negative(self):
        self.assertEqual(calculator.CalculatorApp._format_number(-42), "-42")

    def test_invalid(self):
        self.assertEqual(calculator.CalculatorApp._format_number(float("nan")), "Invalid")

    def test_overflow_format(self):
        self.assertEqual(calculator.CalculatorApp._format_number(float("inf")), "Infinity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
