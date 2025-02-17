"""
文件总述: 

文件详解: 

创建者: 汐琳
创建时间: 2025/2/14 15:31
"""
import os
from pathlib import Path
from decoratorFunc.getFuncDict import get_func_dict
from script.project_tree_print import config


@get_func_dict('/get_serve_module', method='get', token_required=False)
def get_serve_module(ctx, data):
    real_path = (Path(config.PROJECT_ROOT) / 'tool_package/test.py')
    content = ""
    if os.path.exists(real_path) and os.path.isfile(real_path):
        with open(real_path, 'r', encoding='utf-8') as f:
            content = f.read()

    return {
        "code": 200,
        "message": "this is a message",
        "body": content
    }