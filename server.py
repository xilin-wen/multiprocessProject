import socket  # 导入套接字模块
import threading  # 导入线程模块，用于多线程处理请求

from decoratorFunc.getFuncDict import route_handlers
from send_http_response import send_http_response
import importlib

from user.authority import Authority


class HTTPServer:
    def __init__(self, port, shared_queue):
        # 初始化 HTTP 服务器
        self.port = port  # 服务器监听的端口
        self.shared_queue = shared_queue  # 跨进程共享队列

    def serve_forever(self):
        # 启动 HTTP 服务，监听客户端请求
        # 使用 with 语法来确保 socket 连接会自动关闭
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # 创建 TCP 套接字，IPv4 地址，流式协议
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许端口复用

            server_socket.bind(('0.0.0.0', self.port))  # 绑定 IP 和端口
            server_socket.listen(5)  # 开始监听，最多允许 5 个连接排队
            print(f"Server listening on port {self.port}...")  # 打印启动信息

            while True:
                # 持续接受客户端连接
                # client_socket 和 server_socket是两个不同的套接字
                #       server_socket 主要用于监听，
                #       client_socket 主要用于与连接的客户端进行通信
                client_socket, client_address = server_socket.accept()  # 等待客户端连接
                print(f"Connection from {client_address}")  # 打印客户端信息
                # 为每个连接启动新线程处理请求
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            # 处理客户端请求
            request = client_socket.recv(1024).decode()  # 接收请求数据最大长度为1024
            if not request:
                return  # 如果没有请求数据，直接返回

            # 解析请求头，提取请求方法、路径、HTTP 版本、头部信息等
            # 状态行： HTTP/1.0 200 OK -- 200 是状态码
            request_line, *headers = request.split('\r\n')  # 按行分隔请求和头部 -- HTTP 标准中定义的换行符是“回车 + 换行”
            method, path, version = request_line.split()  # 提取方法、路径和 HTTP 版本

            api_func_info = route_handlers.get(path, {}).get(method, {})

            module_name = api_func_info.get("module")    # 获取模块名称（不需要 .py 后缀）
            module = importlib.import_module(module_name)   # 导入模块

            api_func_name = api_func_info.get("func_name")    # 获取函数名称
            api_func = getattr(module, api_func_name)   # 动态获取函数

            # api_func = route_handlers.get(path, {}).get("func")
            is_validate_token = api_func_info.get("token_required")
            is_validate_role = api_func_info.get("role_required")

            """
            创建一个字典存储请求头
            常见的HTTP请求头字段：
                Host: 请求的目标主机（服务器）地址。例如：Host: www.example.com
                User-Agent: 浏览器或客户端软件的标识信息。例如：User-Agent: Mozilla/5.0
                Authorization: 用于身份验证的认证信息。例如：Authorization: Bearer <token>
                Content-Type: 请求体的类型，表示请求体中的数据格式。例如：Content-Type: application/json
                Content-Length: 请求体的大小，字节数。
                Accept: 客户端可处理的响应类型。例如：Accept: text/html,application/xhtml+xml
                Accept-Encoding: 客户端支持的编码方式，例如 gzip、deflate。
                Connection: 连接的管理方式，例如：Connection: keep-alive 或 Connection: close
                Cookie: 客户端发送的 cookie 信息。例如：Cookie: user=alice; session=xyz123
                X-Forwarded-For: 用于标识请求经过的代理服务器的原始客户端 IP 地址（常见于代理和负载均衡场景）。
                Referer: 上一个请求的 URL 地址，浏览器发送该头用于引用页面。
                Origin: 请求的原始域，通常用于跨域请求时识别来源。
            """
            header_dict = {}
            for header in headers:
                if header:
                    header_name, header_value = header.split(': ', 1)  # 解析键值对
                    header_dict[header_name] = header_value

            # 判断 token 是否优先，并从中获取有用信息
            if is_validate_token:
                # 从请求头中获取 Authorization 头部并提取 token
                authorization = header_dict.get('Authorization', '')
                token = None
                if authorization.startswith('Bearer '):
                    token = authorization[len('Bearer '):]  # 获取 Bearer 后面的 token

                if token:
                    token_validate_result = Authority(token, verify_identity = is_validate_role, verify_token = is_validate_token)
                    if not token_validate_result:
                        # body = {"错误": "路由错误，您当前访问的页面不存在"}
                        # headers = {
                        #     "Content-Type": "application/json",
                        # }
                        # send_http_response(client_socket, 404, "Not Found", headers, body)
                        send_http_response(client_socket, 401, "'错误':'令牌已过期或无效'", headers)
                    else:
                        api_func(token_validate_result)
                else:
                    send_http_response(client_socket, 401, "'错误':'令牌已过期或无效'", headers)
            else:
                api_func()

        finally:
            client_socket.close()  # 无论如何关闭客户端连接