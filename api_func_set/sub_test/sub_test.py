import json
from decoratorFunc.getFuncDict import get_func_dict

data_hello = {"message": "Hello, world!"}
data_goodbye = {"message": "Goodbye, world!"}

# 定义多个路由处理函数
@get_func_dict('/hello', method='GET', token_required=False, role_required=True)
def handle_hello(self):
    print("123456")
    # self.send_response(200)
    # self.send_header('Content-type', 'application/json')
    # self.end_headers()
    # self.wfile.write(json.dumps(data_hello).encode())

# @get_func_dict('/goodbye')
# def handle_goodbye(self):
#     self.send_response(200)
#     self.send_header('Content-type', 'application/json')
#     self.end_headers()
#     self.wfile.write(json.dumps(data_goodbye).encode())
