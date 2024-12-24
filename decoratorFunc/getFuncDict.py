"""
文件描述: api_func 函数的装饰器函数，用于在项目启动时获取、导入所有 api 函数的基本信息，并且创建一个 route_handlers 字典用于存放这些信息

创建者: 汐琳
创建时间: 2024-12-06 16:25:48
"""
import os
import inspect
from pathlib import Path
from symtable import Function
# from symtable import Function
from typing import Literal
# 存储所有路由的处理器
route_handlers = {}

def get_func_dict(
        path: str,
        method:Literal["get", "post", "put", "delete", "GET", "POST", "PUT", "DELETE"]='GET',
        token_required: bool=True,
        role_required: bool=False
):
    """
    路由装饰器，支持开启鉴权。

    :param path: 路由路径
    :param method: 请求方法，默认为 'GET'
    :param token_required: 是否需要 Token 鉴权，默认 True
    :param role_required: 是否需要角色鉴权，默认 False
    :return: 装饰后的函数
    """

    # 给装饰器函数自己添加一个属性 __is_decorator__，用于在引入所有 API 函数时，排除引入装饰器 --装饰器多是重复使用，但是本项目中要求函数名字不能重复
    get_func_dict.__is_decorator__ = True

    def decorator(func):
        # 获取被装饰函数的文件路径
        file_path = inspect.getfile(func)
        # 获取文件的绝对路径
        abs_file_path = os.path.abspath(file_path)

        # 查找基准目录 'api_func_set' 在路径中的位置
        base_dir_index = abs_file_path.find("api_func_set")

        relative_path = None
        # 如果找到了 'api_func_set'，则截取路径
        if base_dir_index != -1:
            # 保留 'api_func_set' 及其后的路径部分
            relative_path = abs_file_path[base_dir_index:]

        # 如果相对路径存在，去掉文件扩展名并构建模块路径
        if relative_path:
            file_without_extension = os.path.splitext(relative_path)[0]
            # 使用 pathlib 将路径分割为模块路径
            module_path = str(Path(file_without_extension).with_suffix('')).replace(os.sep, '.')
        else:
            # 如果路径无法匹配 api_func_set，给出错误提示或处理
            raise ValueError(f"'{func.__name__}' 函数不在 'api_func_set' 文件夹下。")

        # 初始化 route_handlers[path] 为字典（如果尚未初始化）
        if path not in route_handlers:
            route_handlers[path] = {}

        # 将当前路由的处理信息存储到 route_handlers 中
        route_handlers[path][method.upper()] = {
            "token_required": token_required,
            "role_required": role_required,
            "module_path": module_path,
            "func_name": func.__name__  # 新增函数名
        }

        # 返回原函数
        return func

    return decorator
