import socket  # 导入套接字模块
import json
import urllib.parse
import asyncio

from http_frame.send_http_response import send_http_response
from user.authority import Authority

class HTTPServer:
    def __init__(self, port, shared_route_handlers, import_api_func_dict):
        # 初始化 HTTP 服务器
        self.port = port  # 服务器监听的端口
        self.shared_route_handlers = shared_route_handlers
        self.import_api_func_dict = import_api_func_dict

    async def serve_forever(self):
        # 启动 HTTP 服务，监听客户端请求
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许端口复用 -- 虽然说 asyncio 是自主支持端口复用，但是如果不添加这句代码会报错，不允许复用端口
        server_socket.bind(('0.0.0.0', self.port))  # 绑定 IP 和端口
        server_socket.listen(5) # 开始监听，最多允许 5 个连接排队

        server = await asyncio.start_server(self.handle_client, sock=server_socket)  # 异步创建 TCP 服务器
        print(f"Server listening on port {self.port}...")  # 打印启动信息

        # 运行服务器直到手动停止
        async with server:
            await server.serve_forever()  # 异步地一直运行，直到手动停止

    async def parsing_data(self, reader):
        # request 前端传过来的数据
        request = (await reader.read(1024)).decode()  # 异步读取请求数据（最大 1024 字节），并使用decode()方法将字节流解码为字符串  asyncio.start_server 提供的 reader 和 writer 是对原始套接字的封装
        if not request:
            return  # 如果没有请求数据，直接返回

        # 解析请求头，提取请求方法、路径、HTTP 版本、头部信息等
        # 状态行： HTTP/1.0 200 OK -- 200 是状态码
        request_line, *headers = request.split('\r\n')  # 按行分隔请求和头部 -- HTTP 标准中定义的换行符是“回车 + 换行”
        method, path, version = request_line.split()  # 提取方法、路径和 HTTP 版本

        # 解析 URL，去掉查询参数，只保留纯净的路由
        parsed_url = urllib.parse.urlparse(path) # 将 URL 拆解为各个组成部分，包括路径、查询参数、锚点等。我们只需要使用 path 部分，而 params 和 query 部分会被自动去掉
        path = parsed_url.path  # 只保留路径部分，不包括查询字符串

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
        header_dict = {}  # 接口头部信息
        for header in headers:
            if header:
                header_name, header_value = header.split(': ', 1)  # 解析键值对
                header_dict[header_name] = header_value

        # 判断 Content-Type
        content_type = header_dict.get('Content-Type', '').lower()

        # 解析请求数据
        data = {}  # 接口数据
        if method == 'GET':
            # GET 请求通常通过查询参数传递数据
            data = urllib.parse.parse_qs(parsed_url.query)
        elif method == 'POST':
            header_end = request.find("\r\n\r\n")
            if header_end != -1:
                body = request[header_end + 4:] # str 类型数据

                # 处理不同的 Content-Type
                if 'application/x-www-form-urlencoded' in content_type:
                    # 处理 application/x-www-form-urlencoded 数据
                    post_params = urllib.parse.parse_qs(body)
                    for key, value in post_params.items():
                        data[key] = value

                elif 'application/json' in content_type:
                    # 处理 application/json 数据
                    try:
                        post_data = json.loads(body)
                        data.update(post_data)  # 更新字典
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")

        return {
            "request": request,
            "path": path,
            "method": method,
            "header_dict": header_dict,
            "data": data,
        }

    def import_func(self, path, method):
        api_func_info = self.shared_route_handlers.get(path, {}).get(method, {})
        api_func_name = api_func_info.get("func_name")  # 获取函数名称

        return {
            "api_func_info": api_func_info,
            "api_func_name": api_func_name
        }

    @staticmethod
    def create_header(content_type ="application/json", **other_info):
        header_info = {
            "Content-Type": content_type
        }

        # 如果传入了其他头部信息，合并到默认的 headers 中
        if other_info:
            header_info.update(other_info)

        return header_info

    async def handle_client(self, reader, writer):
        # 处理客户端请求
        try:
            # 解析接收到的信息
            parsing_data = await self.parsing_data(reader)
            if parsing_data is None:
                return  # 如果没有请求数据，直接返回

            request, path, method, header_dict, data = parsing_data.values()

            # 找到并导入对应的 api 函数
            api_func_dict = self.import_func(path, method)
            api_func_info = api_func_dict["api_func_info"]
            func_name = api_func_info["func_name"]
            api_func = self.import_api_func_dict[func_name]

            # 创建 header 信息
            return_headers = self.create_header()

            # 判断 token 是否有效，并从中获取有用信息
            is_validate_token = api_func_info.get("token_required")
            is_validate_role = api_func_info.get("role_required")
            if is_validate_token:
                # 从请求头中获取 Authorization 头部并提取 token
                authorization = header_dict.get('Authorization', '')
                token = None
                if authorization.startswith('Bearer '):
                    token = authorization[len('Bearer '):]  # 获取 Bearer 后面的 token

                if token:
                    token_validate_result = Authority(token, verify_identity = is_validate_role, verify_token = is_validate_token)
                    decoded_token = token_validate_result.get_decoded_info()
                    if not token_validate_result:
                        await send_http_response(writer, 401, "'错误':'令牌已过期或无效'", return_headers)
                    else:
                        response = api_func(ctx=decoded_token, data=data)
                        await send_http_response(writer, response["code"], response["message"], return_headers, response["body"])
                else:
                    await send_http_response(writer, 401, "'错误':'令牌已过期或无效'", return_headers)
            else:
                response = api_func({}, data)
                await send_http_response(writer, response["code"], response["message"], return_headers, response["body"])

        finally:
            writer.close()  # 无论如何关闭客户端连接

    async def start(self):
        await self.serve_forever()  # 调用 serve_forever 协程