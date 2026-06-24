"""
仿 Windows 计算器 - Kivy 版本
支持 Tkinter 桌面端和 Android APK 编译
"""

import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex


class CalculatorAppCore:
    """计算器核心逻辑（与 GUI 框架无关）"""

    def __init__(self):
        self.expr_buffer = ""
        self.display_text = ""
        self.just_calculated = False
        self.open_parens = 0
        self.expr_label_text = ""
        self.display_var = "0"

    def on_button(self, text):
        handlers = {
            "0": lambda: self._input_digit(text),
            "1": lambda: self._input_digit(text),
            "2": lambda: self._input_digit(text),
            "3": lambda: self._input_digit(text),
            "4": lambda: self._input_digit(text),
            "5": lambda: self._input_digit(text),
            "6": lambda: self._input_digit(text),
            "7": lambda: self._input_digit(text),
            "8": lambda: self._input_digit(text),
            "9": lambda: self._input_digit(text),
            ".": self._input_decimal,
            "(": self._input_left_paren,
            ")": self._input_right_paren,
            "+": lambda: self._input_operator(text),
            "−": lambda: self._input_operator(text),
            "×": lambda: self._input_operator(text),
            "÷": lambda: self._input_operator(text),
            "=": self._calculate,
            "C": self._clear_all,
            "⌫": self._backspace,
            "%": self._percent,
            "±": self._negate,
            "x²": self._square,
            "⅟x": self._reciprocal,
            "√x": self._sqrt,
        }
        handler = handlers.get(text)
        if handler:
            handler()

    # --- 数字和小数点输入 ---
    def _input_digit(self, digit):
        if self.just_calculated:
            self.expr_buffer = ""
            self.display_text = ""
            self.just_calculated = False
            self.open_parens = 0

        self.expr_buffer += digit
        self.display_text += digit
        self._strip_leading_zeros()
        self._update_display()

    def _strip_leading_zeros(self):
        i = len(self.expr_buffer)
        digits = []
        while i > 0 and self.expr_buffer[i - 1] in "0123456789":
            digits.append(self.expr_buffer[i - 1])
            i -= 1
        if digits:
            num_str = "".join(reversed(digits))
            cleaned = num_str.lstrip("0") or "0"
            self.expr_buffer = self.expr_buffer[:i] + cleaned
            j = len(self.display_text)
            digits_d = []
            while j > 0 and self.display_text[j - 1] in "0123456789":
                digits_d.append(self.display_text[j - 1])
                j -= 1
            if digits_d:
                num_str_d = "".join(reversed(digits_d))
                cleaned_d = num_str_d.lstrip("0") or "0"
                self.display_text = self.display_text[:j] + cleaned_d

    def _input_decimal(self):
        if self.just_calculated:
            self.expr_buffer = "0"
            self.display_text = "0."
            self.just_calculated = False
            self.open_parens = 0
            self._update_display()
            return

        current_num = self._last_number_in_buffer(self.expr_buffer)
        if "." in current_num:
            return
        self.expr_buffer += "."
        self.display_text += "."
        self._update_display()

    @staticmethod
    def _last_number_in_buffer(buf):
        parts = []
        for ch in reversed(buf):
            if ch in "0123456789.":
                parts.append(ch)
            else:
                break
        return "".join(reversed(parts))

    # --- 括号输入 ---
    def _input_left_paren(self):
        if self.just_calculated:
            self.expr_buffer = ""
            self.display_text = ""
            self.just_calculated = False

        if self.expr_buffer and self.expr_buffer[-1] in "0123456789)":
            self.expr_buffer += "*"
            self.display_text += "×"

        self.expr_buffer += "("
        self.display_text += "("
        self.open_parens += 1
        self._update_display()

    def _input_right_paren(self):
        if self.open_parens <= 0:
            return
        self.expr_buffer += ")"
        self.display_text += ")"
        self.open_parens -= 1
        self._update_display()

    # --- 运算符输入 ---
    def _input_operator(self, display_op):
        internal_op = self._display_to_internal(display_op)

        if self.just_calculated:
            try:
                result = self._evaluate(self.expr_buffer)
                result_str = self._format_number(result)
            except Exception:
                result_str = self.display_text
            self.expr_buffer = result_str
            self.display_text = result_str
            self.just_calculated = False

        if self.expr_buffer and self.expr_buffer[-1] in "+-*/":
            self.expr_buffer = self.expr_buffer[:-1]
            display_ops = "+−×÷"
            if self.display_text and self.display_text[-1] in display_ops:
                self.display_text = self.display_text[:-1]

        self.expr_buffer += internal_op
        self.display_text += display_op
        self._update_display()

    @staticmethod
    def _display_to_internal(op):
        mapping = {"+": "+", "−": "-", "×": "*", "÷": "/"}
        return mapping.get(op, op)

    # --- 计算 ---
    def _calculate(self):
        if not self.expr_buffer:
            return

        while self.open_parens > 0:
            self.expr_buffer += ")"
            self.display_text += ")"
            self.open_parens -= 1

        try:
            result = self._evaluate(self.expr_buffer)
        except ZeroDivisionError:
            self.display_text = "Invalid"
            self.expr_buffer = "Invalid"
            self.just_calculated = True
            self.display_var = "Invalid"
            self.expr_label_text = ""
            return
        except Exception:
            self.display_var = "Invalid"
            self.just_calculated = True
            return

        self.expr_label_text = self.display_text + " ="
        formatted = self._format_number(result)
        self.display_text = formatted
        self.expr_buffer = formatted
        self.just_calculated = True
        self.display_var = formatted

    def _evaluate(self, expr):
        allowed_chars = set("0123456789+-*/.() %eE")
        if not all(c in allowed_chars for c in expr):
            raise ValueError("非法字符")

        processed = self._process_percent(expr)
        result = eval(processed, {"__builtins__": {}}, {})

        if math.isnan(result):
            raise ValueError("NaN")
        if math.isinf(result):
            return result

        return result

    def _process_percent(self, expr):
        result = []
        for ch in expr:
            if ch == "%":
                result.append("/100")
            else:
                result.append(ch)
        return "".join(result)

    # --- 清除和退格 ---
    def _clear_all(self):
        self.expr_buffer = ""
        self.display_text = ""
        self.just_calculated = False
        self.open_parens = 0
        self.expr_label_text = ""
        self.display_var = "0"

    def _backspace(self):
        if self.just_calculated:
            return
        if not self.expr_buffer:
            return
        self.expr_buffer = self.expr_buffer[:-1]
        self.display_text = self.display_text[:-1]
        self._update_display()

    # --- 百分比 ---
    def _percent(self):
        if not self.expr_buffer:
            return
        self.expr_buffer += "%"
        self.display_text += "%"
        self._update_display()

    # --- 取反 ---
    def _negate(self):
        if not self.expr_buffer:
            return
        self._negate_last_number()
        self._update_display()

    def _negate_last_number(self):
        buf = self.expr_buffer
        disp = self.display_text

        num_start = len(buf)
        while num_start > 0 and buf[num_start - 1] in "0123456789.":
            num_start -= 1

        if num_start == len(buf):
            return

        num_str = buf[num_start:]
        try:
            val = float(num_str)
        except ValueError:
            return

        neg_val = -val
        new_num = self._format_number(neg_val)

        self.expr_buffer = buf[:num_start] + new_num

        num_start_d = len(disp)
        while num_start_d > 0 and disp[num_start_d - 1] in "0123456789.":
            num_start_d -= 1
        if num_start_d < len(disp):
            self.display_text = disp[:num_start_d] + new_num

    # --- 特殊功能 ---
    def _square(self):
        if not self.expr_buffer:
            return
        try:
            val = self._evaluate(self.expr_buffer)
        except Exception:
            return
        result = val * val
        self.expr_label_text = f"sqr({self.display_text}) ="
        self.display_text = self._format_number(result)
        self.expr_buffer = self.display_text
        self.just_calculated = True
        self.display_var = self.display_text

    def _reciprocal(self):
        if not self.expr_buffer:
            return
        try:
            val = self._evaluate(self.expr_buffer)
        except Exception:
            return
        if val == 0:
            self.display_var = "Invalid"
            self.just_calculated = True
            return
        result = 1 / val
        self.expr_label_text = f"1/({self.display_text}) ="
        self.display_text = self._format_number(result)
        self.expr_buffer = self.display_text
        self.just_calculated = True
        self.display_var = self.display_text

    def _sqrt(self):
        if not self.expr_buffer:
            return
        try:
            val = self._evaluate(self.expr_buffer)
        except Exception:
            return
        if val < 0:
            self.display_var = "Invalid"
            self.just_calculated = True
            return
        result = val ** 0.5
        self.expr_label_text = f"√({self.display_text}) ="
        self.display_text = self._format_number(result)
        self.expr_buffer = self.display_text
        self.just_calculated = True
        self.display_var = self.display_text

    def _update_display(self):
        self.display_var = self.display_text if self.display_text else "0"

    # --- 数字格式化 ---
    @staticmethod
    def _format_number(num):
        if isinstance(num, float) and math.isnan(num):
            return "Invalid"
        if math.isinf(num):
            return "Infinity"
        if num == 0:
            return "0"
        if abs(num) >= 1e16 or (abs(num) < 1e-10 and num != 0):
            return f"{num:.6e}"
        if num == int(num) and abs(num) < 1e16:
            return f"{int(num):,}"
        return f"{num:.10g}".replace(",", "")


# ============================================================
# Kivy GUI
# ============================================================

COLORS = {
    "bg": get_color_from_hex("#202020"),
    "display_fg": get_color_from_hex("#ffffff"),
    "btn_num": get_color_from_hex("#3b3b3b"),
    "btn_num_down": get_color_from_hex("#4a4a4a"),
    "btn_op": get_color_from_hex("#323232"),
    "btn_op_down": get_color_from_hex("#404040"),
    "btn_eq": get_color_from_hex("#4cc2f1"),
    "btn_eq_down": get_color_from_hex("#5dd0ff"),
    "btn_clear": get_color_from_hex("#3b3b3b"),
    "btn_clear_down": get_color_from_hex("#4a4a4a"),
    "text_fg": get_color_from_hex("#ffffff"),
    "text_sub": get_color_from_hex("#aaaaaa"),
}

BUTTONS = [
    ["(", ")", "%", "C"],
    ["±", "⅟x", "x²", "√x"],
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "−"],
    ["0", ".", "+", "="],
]


def _make_btn_style(btn_type):
    """返回按钮的 KV 样式字典"""
    if btn_type == "eq":
        return {
            "background_color": COLORS["btn_eq"],
            "color": get_color_from_hex("#1e1e1e"),
            "background_down": COLORS["btn_eq_down"],
        }
    elif btn_type == "op":
        return {
            "background_color": COLORS["btn_op"],
            "color": COLORS["text_fg"],
            "background_down": COLORS["btn_op_down"],
        }
    elif btn_type == "clear":
        return {
            "background_color": COLORS["btn_clear"],
            "color": COLORS["text_fg"],
            "background_down": COLORS["btn_clear_down"],
        }
    else:
        return {
            "background_color": COLORS["btn_num"],
            "color": COLORS["text_fg"],
            "background_down": COLORS["btn_num_down"],
        }


class CalcButton(Button):
    """自定义计算器按钮"""

    def __init__(self, text, btn_type="num", **kwargs):
        style = _make_btn_style(btn_type)
        kwargs.update(style)
        kwargs.setdefault("font_size", dp(22))
        kwargs.setdefault("bold", False)
        if btn_type == "op":
            kwargs["font_size"] = dp(26)
            kwargs["bold"] = True
        super().__init__(text=text, **kwargs)


class CalculatorScreen(BoxLayout):
    """计算器主界面"""

    def __init__(self, core: CalculatorAppCore, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(4)

        self.core = core

        # ---- 显示区域 ----
        display_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(100))
        display_layout.background_color = COLORS["bg"]

        self.expr_label = Label(
            text="",
            font_name="Roboto",
            font_size=dp(16),
            color=COLORS["text_sub"],
            halign="right",
            valign="bottom",
        )
        self.display_label = Label(
            text="0",
            font_name="Roboto",
            font_size=dp(30),
            color=COLORS["display_fg"],
            halign="right",
            valign="middle",
        )
        display_layout.add_widget(self.expr_label)
        display_layout.add_widget(self.display_label)
        self.add_widget(display_layout)

        # ---- 按钮区域 ----
        btn_layout = BoxLayout(orientation="vertical", size_hint_y=1)
        btn_layout.background_color = COLORS["bg"]

        for row_idx, row_buttons in enumerate(BUTTONS):
            row = BoxLayout(size_hint_y=1, spacing=dp(4))
            row.background_color = COLORS["bg"]
            for col_idx, text in enumerate(row_buttons):
                if text == "=":
                    btn_type = "eq"
                    font_name = "Roboto-Bold"
                elif text in ("÷", "×", "−", "+"):
                    btn_type = "op"
                    font_name = "Roboto-Bold"
                elif text == "C":
                    btn_type = "clear"
                    font_name = "Roboto"
                else:
                    btn_type = "num"
                    font_name = "Roboto"

                btn = CalcButton(
                    text=text,
                    btn_type=btn_type,
                    font_name=font_name,
                    on_press=self._on_press,
                )
                row.add_widget(btn)
            btn_layout.add_widget(row)

        self.add_widget(btn_layout)

    def _on_press(self, btn: CalcButton):
        self.core.on_button(btn.text)
        self.expr_label.text = self.core.expr_label_text
        self.display_label.text = self.core.display_var


class CalculatorKivyApp(App):
    def build(self):
        Window.clearcolor = COLORS["bg"]
        core = CalculatorAppCore()
        return CalculatorScreen(core)


if __name__ == "__main__":
    CalculatorKivyApp().run()
