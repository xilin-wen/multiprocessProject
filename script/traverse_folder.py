"""
文件描述: 在 main 函数中，执行该文件，动态引入 api_func_set 文件夹下的所有 api 函数

创建者: 汐琳
创建时间: 2024-12-06 16:23:22
"""
import os
import importlib
import types
from pathlib import Path


def import_all_functions_in_folder(folder_path):
    """
    动态导入指定文件夹及其子文件夹下的所有 Python 文件，排除 '__init__.py'。
    """
    folder = Path(folder_path)
    import_api_func_dict = {}  # 用于存储所有函数，按函数名称作为键

    for py_file in folder.rglob('*.py'):
        # 排除 __init__.py 文件
        if py_file.name != '__init__.py':
            # 获取模块路径（去除文件扩展名，替换文件分隔符为 .）
            # 这里保证模块路径以 api_func_set 为前缀
            module_path = py_file.relative_to(folder).with_suffix('')
            # 使用相对路径，转换为模块路径，前缀加上 api_func_set
            module_name = f"api_func_set.{module_path}".replace(os.sep, '.')

            try:
                # 动态导入模块
                module = importlib.import_module(module_name)

                # 遍历模块中的所有函数，并对其进行相应的处理
                for func_item_name in dir(module):
                    # 获取函数名称
                    func_item = getattr(module, func_item_name)

                    # 排除以__开头和结尾的函数，api 函数一般不会以__开头和结尾
                    if not (func_item_name.startswith('__') and func_item_name.endswith('__')) and type(func_item) == types.FunctionType:
                        # 判断函数是否为装饰器，如果是装饰器，不需要进行任何处理
                        func_is_decorator = getattr(func_item, "__is_decorator__", False)

                        if not func_is_decorator:
                            # 由于是在全局中引入所有 api 函数，因此 api 函数的名字不能重复
                            if func_item_name in import_api_func_dict:
                                raise ValueError(f"{module_name} 文件中的 '{func_item_name} 函数' 已经存在，请修改函数名称")
                            else:
                                import_api_func_dict[func_item_name] = func_item

                                # # 动态引入函数（如果未重复）
                                # try:
                                #     # 动态加载函数
                                #     getattr(module, func_item_name)
                                # except Exception as e:
                                #     raise ImportError(f"无法导入从'{module_path}'模块中导入函数 '{func_item_name}': {e}")

            except ModuleNotFoundError as e:
                print(f"Error importing {module_name}: {e}")

    return import_api_func_dict