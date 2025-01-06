"""
文件描述: 本文件用于接收从客户端传入的数据，并匹配到对应的函数，最后将传入的函数覆盖服务器上代码，并热加载应用修改后的函数
            -- 要求：不能使用 importlib.reload 库

创建者: 汐琳
创建时间: 2025-12-30 18:39:58
"""
import ast
import hashlib
import inspect
import black
from types import FunctionType

class HotReloadMain:
    def __init__(self, class_code):
        # 路由和方法对应的函数名
        self.route_handlers = {
            "/api/test": {
                "get": "test_function"
            }
        }

        # 保存函数名和函数体
        self.import_api_func_dict = {
            "test_function": lambda: print("Original function")
        }

        self.code = class_code

    def format_code(self):

        print("self.code===>", self.code)
        try:
            ast.parse(self.code)
            print("语法检查通过")
        except SyntaxError as e:
            raise ValueError(f"代码包含语法错误：{e}")

        try:
            format_code = black.format_str(self.code, mode=black.Mode())
            print(f"代码格式化成功，{format_code}")
        except Exception as e:
            raise ValueError(f"代码格式化失败：{e}")

# 示例使用
if __name__ == "__main__":
    code = """
        def example():
            print("Hello World")
        """

    class_item = HotReloadMain(code)
    class_item.format_code()








