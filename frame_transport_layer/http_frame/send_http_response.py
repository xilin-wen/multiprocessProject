"""
文件描述: 用于将处理后的数据返回给客户端（异步版本）

创建者: 汐琳
创建时间: 2024-12-06 17:24:05
"""
import json  # 导入 JSON 模块

from dicts.http_status import http_status_codes


async def send_http_response(writer, status_code=200, status_message="请求成功", headers=None, body=None):
    """
    构造并发送一个完整的 HTTP 响应（异步版本）。

    :param writer: asyncio.StreamWriter 对象，用于向客户端发送数据
    :param status_code: HTTP 状态码 (例如: 404, 200)
    :param status_message: HTTP 状态消息 (例如: "Not Found", "OK")
    :param headers: 响应头字典，例如 {"Content-Type": "application/json"}
    :param body: 响应体内容，通常是 JSON 格式的字典
    """
    # 初始化响应头部
    if headers is None:
        headers = {"Content-Type": "application/json; charset=utf-8"}

    # 构造响应体
    if body:
        try:
            return_body = {
                "code": status_code,
                "message": status_message,
                "data": body
            }
            body_bytes = json.dumps(return_body, ensure_ascii=False).encode()  # 将 JSON 数据转换为字节流
            headers["Content-Length"] = str(len(body_bytes))  # 自动计算并设置 Content-Length
        except (TypeError, ValueError) as e:
            # 如果 body 无法转换为 JSON，设置错误响应
            status_code = 500
            status_message = "Internal Server Error"
            body = {"error": str(e)}
            body_bytes = json.dumps(body, ensure_ascii=False).encode()
            headers["Content-Length"] = str(len(body_bytes))
    else:
        body_bytes = b""
        headers["Content-Length"] = "0"

    # 构造状态行
    # status_line = f"HTTP/1.1 200 OK\r\n"
    http_status_code = http_status_codes[status_code]
    status_line = f"HTTP/1.1 {status_code} {http_status_code}\r\n"

    # 构造头部
    header_lines = "".join([f"{k}: {v}\r\n" for k, v in headers.items()])

    # 完整的响应：状态行 + 头部 + 空行
    response = status_line + header_lines + "\r\n"

    # 使用 writer 异步发送响应数据
    writer.write(response.encode())  # 发送状态行和头部
    if body_bytes:
        print(body_bytes)
        writer.write(body_bytes)  # 如果有响应体，发送响应体
    await writer.drain()  # 确保数据完全发送
