import socket  # 导入套接字模块
import threading  # 导入线程模块，用于多线程处理请求
import json
import urllib.parse
import importlib

from decoratorFunc.getFuncDict import route_handlers
from send_http_response import send_http_response
from user.authority import Authority


class HTTPServer:
    def __init__(self, port, shared_queue):
        # 初始化 HTTP 服务器
        self.port = port  # 服务器监听的端口
        self.shared_queue = shared_queue  # 跨进程共享队列
        self.request = None # 前端传过来的数据
        self.api_func_info = None # 接口函数的相关信息
        self.path = None # 接口路由
        self.method = None # 接口方法
        self.header_dict = {} # 接口头部信息
        self.data = {} # 接口数据
        self.api_func = None # api 函数

    def test(self):
        self.other()

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

    def parsing_data(self, client_socket):
        self.request = client_socket.recv(1024).decode()  # 接收请求数据最大长度为1024
        if not self.request:
            return  # 如果没有请求数据，直接返回

        # 解析请求头，提取请求方法、路径、HTTP 版本、头部信息等
        # 状态行： HTTP/1.0 200 OK -- 200 是状态码
        request_line, *headers = self.request.split('\r\n')  # 按行分隔请求和头部 -- HTTP 标准中定义的换行符是“回车 + 换行”
        self.method, path, version = request_line.split()  # 提取方法、路径和 HTTP 版本

        # 解析 URL，去掉查询参数，只保留纯净的路由
        parsed_url = urllib.parse.urlparse(path) # 将 URL 拆解为各个组成部分，包括路径、查询参数、锚点等。我们只需要使用 path 部分，而 params 和 query 部分会被自动去掉
        self.path = parsed_url.path  # 只保留路径部分，不包括查询字符串

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
        for header in headers:
            if header:
                header_name, header_value = header.split(': ', 1)  # 解析键值对
                self.header_dict[header_name] = header_value

        # 判断 Content-Type
        content_type = self.header_dict.get('Content-Type', '').lower()

        # 解析请求数据
        if self.method == 'GET':
            # GET 请求通常通过查询参数传递数据
            parsed_url = urllib.parse.urlparse(path)
            self.data = urllib.parse.parse_qs(parsed_url.query)
        elif self.method == 'POST':
            header_end = self.request.find("\r\n\r\n")
            if header_end != -1:
                body = self.request[header_end + 4:] # str 类型数据

                # 处理不同的 Content-Type
                if 'application/x-www-form-urlencoded' in content_type:
                    # 处理 application/x-www-form-urlencoded 数据
                    post_params = urllib.parse.parse_qs(body)
                    for key, value in post_params.items():
                        self.data[key] = value

                elif 'application/json' in content_type:
                    # 处理 application/json 数据
                    try:
                        post_data = json.loads(body)
                        self.data.update(post_data)  # 更新字典
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")

    def import_func(self):
        self.api_func_info = route_handlers.get(self.path, {}).get(self.method, {})

        module_name = self.api_func_info.get("module")  # 获取模块名称（不需要 .py 后缀）
        module = importlib.import_module(module_name)  # 导入模块

        api_func_name = self.api_func_info.get("func_name")  # 获取函数名称
        self.api_func = getattr(module, api_func_name)  # 动态获取函数

    def create_header(self, content_type = "application/json", **other_info):
        header_info = {
            "Content-Type": content_type
        }

        # 如果传入了其他头部信息，合并到默认的 headers 中
        if other_info:
            header_info.update(other_info)

        return header_info

    def handle_client(self, client_socket):
        # 处理客户端请求
        try:
            # 解析接收到的信息
            self.parsing_data(client_socket)

            # 找到并导入对应的 api 函数
            self.import_func()

            # 创建 header 信息
            return_headers = self.create_header()

            # 判断 token 是否有效，并从中获取有用信息
            is_validate_token = self.api_func_info.get("token_required")
            is_validate_role = self.api_func_info.get("role_required")
            if is_validate_token:
                # 从请求头中获取 Authorization 头部并提取 token
                authorization = self.header_dict.get('Authorization', '')
                token = None
                if authorization.startswith('Bearer '):
                    token = authorization[len('Bearer '):]  # 获取 Bearer 后面的 token

                if token:
                    token_validate_result = Authority(token, verify_identity = is_validate_role, verify_token = is_validate_token)
                    decoded_token = token_validate_result.get_decoded_info()
                    if not token_validate_result:
                        send_http_response(client_socket, 401, "'错误':'令牌已过期或无效'", return_headers)
                    else:
                        response = self.api_func(ctx=decoded_token, data=self.data)
                        send_http_response(client_socket, response["code"], response["message"], return_headers, response["body"])
                else:
                    send_http_response(client_socket, 401, "'错误':'令牌已过期或无效'", return_headers)
            else:
                response = self.api_func({}, self.data)
                send_http_response(client_socket, response["code"], response["message"], return_headers, response["body"])

        finally:
            client_socket.close()  # 无论如何关闭客户端连接