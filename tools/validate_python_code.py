# import ast  # 导入用于解析 Python 代码抽象语法树的模块
# import black  # 导入用于格式化代码的黑色格式化工具
# import textwrap  # 导入用于清除代码多余缩进的模块
#
#
# def validate_python_code(code: str) -> bool:
#     """
#     校验输入的 Python 代码是否符合 Python 语法和格式规范。
#
#     :param code: 需要校验的 Python 代码字符串
#     :return: 如果代码符合规范返回 True，否则抛出异常
#     """
#
#     # 1. 移除代码多余的缩进，确保每行代码统一缩进
#     code = textwrap.dedent(code)
#
#     # 2. 使用 ast 模块解析代码，检查是否符合 Python 语法
#     try:
#         ast.parse(code)  # 尝试解析代码并检查语法
#         print("语法检查通过")
#     except SyntaxError as e:  # 如果解析失败，抛出语法错误
#         raise ValueError(f"代码包含语法错误: {e}")
#
#     # 3. 使用 black 格式化工具格式化代码，确保符合 PEP 8 规范
#     try:
#         formatted_code = black.format_str(code, mode=black.Mode())  # 格式化代码
#         print("代码格式化成功")
#         return True  # 如果格式化成功，返回 True
#     except Exception as e:  # 如果格式化失败，抛出异常
#         raise ValueError(f"代码格式化失败: {e}")
#
#
# # 示例用法：
# if __name__ == "__main__":
#     code = """
# def example(x, y):
#         result = x + y
#     print(result)
#     """
#     try:
#         if validate_python_code(code):
#             print("代码符合规范！")
#     except ValueError as e:
#         print(f"校验失败: {e}")

import ast


def check_indentation(code: str) -> bool:
    """
    检查代码中的缩进是否一致。
    :param code: 待校验的代码字符串
    :return: 如果缩进一致返回 True，否则返回 False
    """
    lines = code.splitlines()
    indentation = None

    for line in lines:
        # 忽略空行
        if line.strip() == "":
            continue
        # 获取当前行的缩进级别
        current_indentation = len(line) - len(line.lstrip())
        if indentation is None:
            indentation = current_indentation
        elif current_indentation % 4 != 0:  # 检查是否是 4 的倍数
            print(f"IndentationError: Indentation must be multiple of 4 spaces.")
            return False
        elif current_indentation != indentation:
            print(f"IndentationError: Inconsistent indentation on line: {line}")
            return False

        print("line======>", line)

    return True


def validate_python_code(code: str) -> bool:
    """
    校验给定的字符串是否符合 Python 代码格式。
    :param code: 待校验的字符串，实质是一个函数
    :return: 是否符合 Python 代码格式
    """
    if not check_indentation(code):
        return False

    try:
        # 使用 ast.parse 来检查代码是否符合 Python 的语法
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return False


# 测试用例
test_code_1 = """
def my_function(x, y):
    return x + y
"""

test_code_2 = """
def my_function(x, y
    return x + y
"""

test_code_3 = """
def my_function(x, y):
  return x + y
"""

print(validate_python_code(test_code_1))  # 输出: True
print(validate_python_code(test_code_2))  # 输出: False (SyntaxError)
print(validate_python_code(test_code_3))  # 输出: False (IndentationError)
