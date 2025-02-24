"""
文件总述: 引入远程模块

文件详解: 通过添加自定义查找器并调用对应的加载器实现远程模块的引入
        参考资料为 /learning_materials/import引入资料

创建者: 汐琳
创建时间: 2025/2/20 15:31
"""
import ast
import importlib.abc
import importlib.util
import json
import urllib.request
import urllib.parse


class RemoteMetaLoader(importlib.abc.SourceLoader):
    def __init__(self, module_name: str, code: str, path: str):
        self.module_name = module_name
        self.code = code
        self.path = path

    def get_data(self, path):
        return self.code
    def get_filename(self, module_name):
        return f"<remote-module:{module_name}>"

    def exec_module(self, module):
           # 自定义执行逻辑
           code = self.get_data(self.path)  # 通过你的get_data获取代码
           exec(code, module.__dict__)  # 实际执行代码

class RemoteMetaFinder(importlib.abc.MetaPathFinder):
    def __init__(self, base_url: str|None="http://localhost:3001/" ):
        self.base_url = base_url
        self.code = None
        self.module_name = None
        self.fullpath = None

    def find_spec(self, fullname, path, target=None):
        if fullname and type(fullname) == str and (fullname.startswith("PANDAG") or fullname.startswith("pandag")):
            try:
                name_str = fullname.split('_')
                self.module_name = name_str[1]
                self.code = self.get_code()
                tree = ast.parse(self.code)
                print("语法树的详细信息===>", ast.dump(tree, indent=4))
            except Exception as e:
                print(f"加载失败: {str(e)}")
                return None

            return importlib.util.spec_from_loader(
                name=self.module_name,
                loader=RemoteMetaLoader(self.module_name, self.code, self.fullpath),  # 将URL传递给加载器
                origin=self.base_url  # 记录模块来源
            )

    def get_code(self):
            headers = {
                'Authorization': 'Bearer this is a token'
            }

            self.fullpath = self.base_url + 'get_serve_module'
            params = {'module_name': self.module_name }
            url_with_params = self.fullpath + '?' + urllib.parse.urlencode(params)

            request = urllib.request.Request(url_with_params, headers=headers)

            # 发送请求并获取响应
            with urllib.request.urlopen(request) as response:
                raw_response = response.read()
                return json.loads(raw_response)["data"]