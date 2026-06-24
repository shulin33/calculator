"""
仿 Windows 计算器 - 使用 Python Tkinter 实现
支持括号、运算优先级、连续计算等功能
"""

import tkinter as tk
from tkinter import font
import math


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("计算器")
        self.root.resizable(False, False)
        self.root.geometry("340x520")

        # 颜色主题（仿 Win11 计算器）
        self.colors = {
            "bg": "#202020",
            "display_bg": "#202020",
            "display_fg": "#ffffff",
            "btn_num": "#3b3b3b",
            "btn_num_hover": "#4a4a4a",
            "btn_op": "#323232",
            "btn_op_hover": "#404040",
            "btn_eq": "#4cc2f1",
            "btn_eq_hover": "#5dd0ff",
            "btn_clear": "#3b3b3b",
            "btn_clear_hover": "#4a4a4a",
            "text_fg": "#ffffff",
            "text_sub": "#aaaaaa",
        }

        self.root.configure(bg=self.colors["bg"])

        # 表达式引擎：用字符串构建完整表达式，最后一次性求值
        self.expr_buffer = ""       # 内部表达式，运算符用 +,-,*,/, %
        self.display_text = ""      # 显示用表达式，运算符用 +,−,×,÷
        self.just_calculated = False  # 刚按完 = ，下一次数字输入开始新表达式
        self.open_parens = 0         # 未匹配的左括号数

        # 设置字体
        self.display_font = font.Font(family="Segoe UI", size=28, weight="normal")
        self.small_display_font = font.Font(family="Segoe UI", size=14, weight="normal")
        self.btn_font = font.Font(family="Segoe UI", size=14)
        self.op_font = font.Font(family="Segoe UI", size=16)

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # ---- 显示区域 ----
        display_frame = tk.Frame(self.root, bg=self.colors["display_bg"])
        display_frame.pack(fill="x", padx=12, pady=(12, 4))

        # 表达式行（小字）
        self.expr_label = tk.Label(
            display_frame,
            text="",
            font=self.small_display_font,
            fg=self.colors["text_sub"],
            bg=self.colors["display_bg"],
            anchor="e",
        )
        self.expr_label.pack(fill="x", pady=(0, 2))

        # 主数字行（大字）
        self.display_var = tk.StringVar(value="0")
        self.display_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=self.display_font,
            fg=self.colors["display_fg"],
            bg=self.colors["display_bg"],
            anchor="e",
        )
        self.display_label.pack(fill="x", pady=(2, 8))

        # ---- 按钮区域 ----
        btn_frame = tk.Frame(self.root, bg=self.colors["bg"])
        btn_frame.pack(fill="both", expand=True, padx=6, pady=4)

        # 按钮布局：每行 4 列
        # Row 0: (, ), %, C
        # Row 1: ±, ⅟x, x², √x
        # Row 2: 7, 8, 9, ÷
        # Row 3: 4, 5, 6, ×
        # Row 4: 1, 2, 3, −
        # Row 5: 0, ., +, =
        buttons = [
            ["(", ")", "%", "C"],
            ["±", "⅟x", "x²", "√x"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["0", ".", "+", "="],
        ]

        for row_idx, row_buttons in enumerate(buttons):
            for col_idx, text in enumerate(row_buttons):
                # 跳过空按钮
                if not text:
                    continue

                # 确定按钮样式
                if text == "=":
                    is_eq = True
                    is_num_btn = False
                    is_op = False
                    is_clear = False
                elif text in ("÷", "×", "−", "+"):
                    is_eq = False
                    is_num_btn = False
                    is_op = True
                    is_clear = False
                elif text in ("C",):
                    is_eq = False
                    is_num_btn = False
                    is_op = False
                    is_clear = True
                else:
                    is_eq = False
                    is_num_btn = True
                    is_op = False
                    is_clear = False

                # 确定列跨度（默认1列）
                col_span = 1

                # 创建按钮
                if is_eq:
                    btn = tk.Button(
                        btn_frame, text=text, font=self.op_font,
                        fg="#1e1e1e", bg=self.colors["btn_eq"],
                        activebackground=self.colors["btn_eq_hover"],
                        activeforeground="#1e1e1e",
                        relief="flat", bd=0, padx=0, pady=0,
                        command=lambda t=text: self.on_button(t),
                    )
                elif is_op:
                    btn = tk.Button(
                        btn_frame, text=text, font=self.op_font,
                        fg=self.colors["text_fg"], bg=self.colors["btn_op"],
                        activebackground=self.colors["btn_op_hover"],
                        activeforeground=self.colors["text_fg"],
                        relief="flat", bd=0, padx=0, pady=0,
                        command=lambda t=text: self.on_button(t),
                    )
                elif is_clear:
                    btn = tk.Button(
                        btn_frame, text=text, font=self.btn_font,
                        fg=self.colors["text_fg"], bg=self.colors["btn_clear"],
                        activebackground=self.colors["btn_clear_hover"],
                        activeforeground=self.colors["text_fg"],
                        relief="flat", bd=0, padx=0, pady=0,
                        command=lambda t=text: self.on_button(t),
                    )
                else:
                    btn = tk.Button(
                        btn_frame, text=text, font=self.btn_font,
                        fg=self.colors["text_fg"], bg=self.colors["btn_num"],
                        activebackground=self.colors["btn_num_hover"],
                        activeforeground=self.colors["text_fg"],
                        relief="flat", bd=0, padx=0, pady=0,
                        command=lambda t=text: self.on_button(t),
                    )
                btn.grid(row=row_idx, column=col_idx, columnspan=col_span, sticky="nsew")

                btn.bind("<Enter>", lambda e, b=btn: self._on_enter(b))
                btn.bind("<Leave>", lambda e, b=btn: self._on_leave(b))

            btn_frame.rowconfigure(row_idx, weight=1)

        for c in range(4):
            btn_frame.columnconfigure(c, weight=1)

    # --------------------------------------------------------------- hover
    def _on_enter(self, btn):
        bg = btn.cget("bg")
        hover_map = {
            self.colors["btn_num"]: self.colors["btn_num_hover"],
            self.colors["btn_op"]: self.colors["btn_op_hover"],
            self.colors["btn_eq"]: self.colors["btn_eq_hover"],
            self.colors["btn_clear"]: self.colors["btn_clear_hover"],
        }
        btn.configure(bg=hover_map.get(bg, bg))

    def _on_leave(self, btn):
        bg = btn.cget("bg")
        hover_map = {
            self.colors["btn_num_hover"]: self.colors["btn_num"],
            self.colors["btn_op_hover"]: self.colors["btn_op"],
            self.colors["btn_eq_hover"]: self.colors["btn_eq"],
            self.colors["btn_clear_hover"]: self.colors["btn_clear"],
        }
        btn.configure(bg=hover_map.get(bg, bg))

    # -------------------------------------------------------------- logic
    def on_button(self, text):
        if text in "0123456789":
            self._input_digit(text)
        elif text == ".":
            self._input_decimal()
        elif text == "(":
            self._input_left_paren()
        elif text == ")":
            self._input_right_paren()
        elif text in ("+", "−", "×", "÷"):
            self._input_operator(text)
        elif text == "=":
            self._calculate()
        elif text == "C":
            self._clear_all()
        elif text == "⌫":
            self._backspace()
        elif text == "%":
            self._percent()
        elif text == "±":
            self._negate()
        elif text == "x²":
            self._square()
        elif text == "⅟x":
            self._reciprocal()
        elif text == "√x":
            self._sqrt()

    def _update_display(self):
        if self.expr_buffer == "" and not self.just_calculated:
            self.display_var.set("0")
        else:
            self.display_var.set(self.display_text if self.display_text else "0")

    # --- 数字和小数点输入 ---
    def _input_digit(self, digit):
        if self.just_calculated:
            self.expr_buffer = ""
            self.display_text = ""
            self.just_calculated = False
            self.open_parens = 0

        self.expr_buffer += digit
        self.display_text += digit
        # 去掉前导零（但保留 "0" 本身）
        self._strip_leading_zeros()
        self._update_display()

    def _strip_leading_zeros(self):
        """去掉表达式中末尾数字串的前导零"""
        # 找到末尾连续数字
        i = len(self.expr_buffer)
        digits = []
        while i > 0 and self.expr_buffer[i-1] in "0123456789":
            digits.append(self.expr_buffer[i-1])
            i -= 1
        if digits:
            num_str = "".join(reversed(digits))
            # 去掉前导零，保留至少一位
            cleaned = num_str.lstrip("0") or "0"
            self.expr_buffer = self.expr_buffer[:i] + cleaned
            # 同步 display_text
            j = len(self.display_text)
            digits_d = []
            while j > 0 and self.display_text[j-1] in "0123456789":
                digits_d.append(self.display_text[j-1])
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

    @staticmethod
    def _auto_mul():
        """已废弃：隐式乘法由各输入方法内联处理"""
        pass

    # --- 括号输入 ---
    def _input_left_paren(self):
        if self.just_calculated:
            self.expr_buffer = ""
            self.display_text = ""
            self.just_calculated = False

        # 如果前一个token是数字或右括号，需要隐式乘法
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
            # 用上一次的结果作为新表达式的起点
            try:
                result = self._evaluate(self.expr_buffer)
                result_str = self._format_number(result)
            except Exception:
                result_str = self.display_text
            self.expr_buffer = result_str
            self.display_text = result_str
            self.just_calculated = False

        # 如果 buffer 末尾已经是运算符，替换它
        if self.expr_buffer and self.expr_buffer[-1] in "+-*/":
            self.expr_buffer = self.expr_buffer[:-1]
            # 同样替换 display_text 末尾的运算符
            display_ops = "+−×÷"
            if self.display_text and self.display_text[-1] in display_ops:
                self.display_text = self.display_text[:-1]
        else:
            # 否则追加运算符（前面可能有数字，不需要额外处理）
            pass

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

        # 自动闭合括号
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
            self._update_display()
            return
        except Exception:
            self.display_var.set("Invalid")
            self.just_calculated = True
            return

        # 显示表达式行
        self.expr_label.config(text=self.display_text + " =")

        formatted = self._format_number(result)
        self.display_text = formatted
        self.expr_buffer = formatted
        self.just_calculated = True
        self._update_display()

    def _evaluate(self, expr):
        """安全地评估内部格式的表达式字符串"""
        # expr 已经是内部格式（+,-,*,/, %），不需要再做符号转换
        allowed_chars = set("0123456789+-*/.() %eE")
        if not all(c in allowed_chars for c in expr):
            raise ValueError("非法字符")

        # 处理百分比：将 X% 替换为 (X/100)
        processed = self._process_percent(expr)

        result = eval(processed, {"__builtins__": {}}, {})

        if math.isnan(result):
            raise ValueError("NaN")
        if math.isinf(result):
            return result  # 让 _format_number 处理为 "Infinity"

        return result

    def _process_percent(self, expr):
        """将表达式中的 % 处理为 /100"""
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
        self.expr_label.config(text="")
        self._update_display()

    def _backspace(self):
        if self.just_calculated:
            return
        if not self.expr_buffer:
            return
        self.expr_buffer = self.expr_buffer[:-1]
        self.display_text = self.display_text[:-1]
        if self.expr_buffer.endswith("("):
            pass  # 正常
        self._update_display()

    # --- 百分比 ---
    def _percent(self):
        if not self.expr_buffer:
            return
        # 将末尾的数字加上 % 后缀
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

        # 提取末尾数字
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

        # 同步 display_text
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
        self.expr_label.config(text=f"sqr({self.display_text}) =")
        self.display_text = self._format_number(result)
        self.expr_buffer = self.display_text
        self.just_calculated = True
        self._update_display()

    def _reciprocal(self):
        if not self.expr_buffer:
            return
        try:
            val = self._evaluate(self.expr_buffer)
        except Exception:
            return
        if val == 0:
            self.display_var.set("Invalid")
            self.just_calculated = True
            return
        result = 1 / val
        self.expr_label.config(text=f"1/({self.display_text}) =")
        self.display_text = self._format_number(result)
        self.expr_buffer = self.display_text
        self.just_calculated = True
        self._update_display()

    def _sqrt(self):
        if not self.expr_buffer:
            return
        try:
            val = self._evaluate(self.expr_buffer)
        except Exception:
            return
        if val < 0:
            self.display_var.set("Invalid")
            self.just_calculated = True
            return
        result = val ** 0.5
        self.expr_label.config(text=f"√({self.display_text}) =")
        self.display_text = self._format_number(result)
        self.expr_buffer = self.display_text
        self.just_calculated = True
        self._update_display()

    # --- 数字格式化 ---
    @staticmethod
    def _format_number(num):
        """格式化数字显示"""
        if isinstance(num, float) and math.isnan(num):
            return "Invalid"
        if math.isinf(num):
            # 溢出 → 显示 Infinity
            return "Infinity"
        if num == 0:
            return "0"
        # 极大/极小值 → 科学计数法
        if abs(num) >= 1e16 or (abs(num) < 1e-10 and num != 0):
            return f"{num:.6e}"
        # 整数
        if num == int(num) and abs(num) < 1e16:
            return f"{int(num):,}"
        # 浮点数
        return f"{num:.10g}".replace(",", "")


def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
