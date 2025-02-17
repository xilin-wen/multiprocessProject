import importlib.util
import sys
import requests


def import_remote_module(url, module_name):
    # 从远程URL获取模块内容
    headers = {
        'Authorization': f'Bearer this is a token'
    }
    response = requests.get(url, headers=headers, params={'module_name': 'test'})
    module_content = response.json()["data"]
    #
    # 创建一个模块规范
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)

    # 将模块内容执行到模块的命名空间中
    exec(module_content, module.__dict__)

    # 将模块添加到sys.modules中
    sys.modules[module_name] = module
    return module

if __name__ == "__main__":
    remote_module = import_remote_module("http://localhost:3001/get_serve_module", "remote_module")
    print(remote_module.test())