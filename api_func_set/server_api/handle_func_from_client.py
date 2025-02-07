from decoratorFunc.getFuncDict import get_func_dict, route_handlers
from hot_reload.main_edit_func import HandleFuncFromClient
from dataclasses import dataclass, field
from typing import Optional, List

client_func_handler = HandleFuncFromClient()


@dataclass
class EditServerFuncDataType:
    func_id: str
    func_str: str
    func_name: str
    module: str
    is_active: bool
    description: Optional[str] = field(default=None)  # 可选字段，默认为 None
    tags: List[str] = field(default_factory=list)  # 避免共享可变对象,list, dict, set 这类可变类型，防止多个实例共享同一个默认值

@get_func_dict('/editServerFunc', method='post', token_required=False)
def edit_server_func(ctx: str, data: EditServerFuncDataType):
    """编辑 API 函数

    Args:
        ctx(str): 上下文，主要是用户身份信息
        data(EditServerFuncDataType):
            func_id (str): 函数 ID
            func_name (str): 函数名称
            module (str): 所属模块
            description (Optional[str]): 函数描述（可选）
            is_active (bool): 是否启用，默认 `True`

    Returns:

    """
    res = client_func_handler.edit_func(data["func_str"])
    if res:
        return {
            "code": 200,
            "message": "修改成功",
            "body": res
        }
    else:
        return {
            "code": 400,
            "message": "修改失败",
            "body": res
        }


@get_func_dict('/deleteServerFunc', method='post')
def delete_server_func(ctx, data):
    """删除 API 函数

    Args:
        ctx(str): 上下文，主要是用户身份信息
        data:

    Returns:

    """
    res = client_func_handler.delete(data["func_name"])

    if res:
        return {
            "code": 200,
            "message": "删除成功"
        }
    else:
        return {
            "code": 400,
            "message": "删除失败",
            "body": res,
        }

@get_func_dict('/selectApiList', method='get', token_required=False)
def select_api_list(ctx, data):
    """查询 API 函数列表，并获取接口文档

    Args:
        ctx: 上下文，主要是用户身份信息
        data(None):

    Returns:
        API 函数列表和接口文档
    """
    # 转换字典结构
    result = {}

    for path, methods in route_handlers.items():
        for method, details in methods.items():
            func_name = details['func_name']
            func_doc = details['func_doc']

            # 构建目标格式
            result[func_name] = {
                'method': method,
                'func_doc': func_doc,
                # 'api_path': api_path
            }

    return {
        "code": 200,
        "message": "API 函数列表获取成功",
        "body": result
    }
