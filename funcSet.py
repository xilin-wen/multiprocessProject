import multiprocessing
import json
from decoratorFunc.getFuncDict import get_func_dict
from http_frame.send_http_response import send_http_response

data_hello = {"message": "Hello, world!"}
data_goodbye = {"message": "Goodbye, world!"}

# 定义多个路由处理函数
@get_func_dict('/hello', method='get', token_required=False, role_required=True)
def handle_hello(self):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data_hello).encode())

@get_func_dict('/goodbye')
def handle_goodbye(self, client_socket):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data_goodbye).encode())
    body = {"错误": "路由错误，您当前访问的页面不存在"}
    headers = {
        "Content-Type": "application/json",
    }
    # send_http_response(client_socket, 404, "Not Found", headers, body)
    # send_http_response(client_socket, 401, "'错误':'令牌已过期或无效'", headers, response)

shared_var = multiprocessing.Value('i', 0)
lock = multiprocessing.Lock()
# 使用 Manager 创建共享的字典
def countFunc(shared_var, _):
    # 每次接收到请求时，增加全局变量
    lock.acquire()
    shared_var.value += 1
    lock.release()

@get_func_dict('/count', method='GET', token_required=False)
def handle_count(self):
    processes = []

    for i in range(6):
        count_process = multiprocessing.Process(target=countFunc, args=(shared_var, lock))
        processes.append(count_process)
        count_process.start()

    # 打印当前活跃的子进程
    print(f"当前活跃的子进程: {len(multiprocessing.active_children())}")

    # 等待所有进程完成
    for p in processes:
        p.join()

    response = {
        "message": "请求成功",
        "lock": shared_var.value
    }

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

