"""
文件描述: 用于将处理后的数据返回给客户端

创建者: 汐琳
创建时间: 2024-12-06 17:24:05
"""
import json  # 导入 JSON 模块

def send_http_response(client_socket, status_code = 200, status_message = "请求成功", headers=None, body=None):
    """
    构造并发送一个完整的 HTTP 响应。

    :param client_socket: 客户端的 socket 连接
    :param status_code: HTTP 状态码 (例如: 404, 200)
    :param status_message: HTTP 状态消息 (例如: "Not Found", "OK")
    :param headers: 响应头字典，例如 {"Content-Type": "application/json"}
    :param body: 响应体内容，通常是 JSON 格式的字典
    """
    # 构造状态行
    status_line = f"HTTP/1.1 {status_code} {status_message}\r\n"

    # 构造头部
    header_lines = ""
    if headers:
        for header_name, header_value in headers.items():
            header_lines += f"{header_name}: {header_value}\r\n"

    # 构造响应体
    if body:
        body = json.dumps(body, ensure_ascii=False).encode()
    else:
        body = b""

    # 如果没有响应体，确保 Content-Length 头部正确
    if body:
        headers["Content-Length"] = str(len(body))
    else:
        headers["Content-Length"] = "0"

    # 完整的响应：状态行 + 头部 + 空行 + 响应体
    response = status_line + header_lines + "\r\n"

    # 发送响应
    client_socket.sendall(response.encode())  # 发送响应的状态行和头部
    if body:
        client_socket.sendall(body)  # 发送响应体