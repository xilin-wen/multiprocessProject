import os
import inspect
from pathlib import Path

# 存储所有路由的处理器
route_handlers = {}


def get_func_dict(path, method='GET', token_required=True, role_required=False):
    """
    路由装饰器，支持开启鉴权。

    :param path: 路由路径
    :param method: 请求方法，默认为 'GET'
    :param token_required: 是否需要 Token 鉴权，默认 True
    :param role_required: 是否需要角色鉴权，默认 False
    :return: 装饰后的函数
    """

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
            raise ValueError(f"Function '{func.__name__}' is not located within the 'api_func_set' directory.")

        # 初始化 route_handlers[path] 为字典（如果尚未初始化）
        if path not in route_handlers:
            route_handlers[path] = {}

        # 将当前路由的处理信息存储到 route_handlers 中
        route_handlers[path][method] = {
            "token_required": token_required,
            "role_required": role_required,
            "module": module_path,
            "func": func,  # 将处理函数存储到对应的请求方法下
            "func_name": func.__name__  # 新增函数名
        }

        # 返回原函数
        return func

    return decorator
