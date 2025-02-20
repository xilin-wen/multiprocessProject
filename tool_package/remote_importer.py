"""
文件总述:

文件详解: 

创建者: 汐琳
创建时间: 2025/2/20 15:31
"""
import importlib.abc
import importlib.util
import json
import urllib.request
import urllib.parse


class RemoteMetaLoader(importlib.abc.SourceLoader):
    def __init__(self, module_name: str, code: str):
        self.module_name = module_name
        self.code = code

    def get_data(self, path):
        return self.code
    def get_filename(self, fullname):
        return f"<remote-module:{fullname}>"


class RemoteMetaFinder(importlib.abc.MetaPathFinder):
    def __init__(self, base_url: str|None="http://localhost:3001/" ):
        self.base_url = base_url
        self.code = None

    def find_spec(self, fullname, path, target=None):
        if fullname and type(fullname) == str and (fullname.startswith("PANDAG") or fullname.startswith("pandag")):
            try:
                self.code = self.get_code()
            except Exception as e:
                print(f"加载失败: {str(e)}")
                return None

            return importlib.util.spec_from_loader(
                name=fullname,
                loader=RemoteMetaLoader(fullname, self.code),  # 将URL传递给加载器
                origin=self.base_url  # 记录模块来源
            )

    def get_code(self):
            headers = {
                'Authorization': 'Bearer this is a token'
            }

            api_url = self.base_url + 'get_serve_module'
            params = {'module_name': 'test'}
            url_with_params = api_url + '?' + urllib.parse.urlencode(params)

            request = urllib.request.Request(url_with_params, headers=headers)

            # 发送请求并获取响应
            with urllib.request.urlopen(request) as response:
                raw_response = response.read()
                return json.loads(raw_response)["data"]

# sys.meta_path.insert(0, RemoteMetaFinder())
#
# if __name__ == "__main__":
#     # 尝试导入远程模块（假设服务器存在 remote_module.py）
#     try:
#         import PANDAG_fileName as remote_module  # 将通过自定义机制从配置的URL加载
#
#         print(remote_module.test())
#
#     except Exception as e:
#         print(f"加载失败: {str(e)}")