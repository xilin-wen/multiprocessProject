"""
文件描述: 在 main 函数中，执行该文件，动态引入 api_func_set 文件夹下的所有 api 函数

创建者: 汐琳
创建时间: 2024-12-06 16:23:22
"""
import os
import importlib
from pathlib import Path

def import_all_functions_in_folder(folder_path):
    """
    动态导入指定文件夹及其子文件夹下的所有 Python 文件，排除 '__init__.py'。
    """
    folder = Path(folder_path)
    for py_file in folder.rglob('*.py'):
        # 排除 __init__.py 文件
        if py_file.name != '__init__.py':
            # 获取模块路径（去除文件扩展名，替换文件分隔符为 .）
            # 这里保证模块路径以 api_func_set 为前缀
            module_path = py_file.relative_to(folder).with_suffix('')
            # 使用相对路径，转换为模块路径，前缀加上 api_func_set
            module_name = f"api_func_set.{module_path}".replace(os.sep, '.')
            # print("module_name", module_name)

            try:
                # 动态导入模块
                importlib.import_module(module_name)
            except ModuleNotFoundError as e:
                print(f"Error importing {module_name}: {e}")