import asyncio
import json
import struct
import hashlib
import base64

class WebSocketServer:
    """用于处理 ws 协议请求

    1. 接受客户端的 ws 升级请求
    2. 解析接收到的 WebSocket 数据帧
    3. 发送 WebSocket 数据帧

    Attributes(公共属性):
        writer: 用于写入数据的 StreamWriter
        reader: 用于读取数据的 StreamReader
        headers: 请求头
    """

    def __init__(self, writer: asyncio.StreamWriter, reader: asyncio.StreamReader, headers: dict):
        self.writer = writer
        self.headers = headers
        self.reader = reader

    async def send_websocket_response(self):
        """
        处理 WebSocket 握手并发送响应
        """
        ws_key = self.headers.get("Sec-WebSocket-Key")
        if not ws_key:
            return

        """
        计算 WebSocket 握手中服务器响应头 Sec-WebSocket-Accept 的值

        1. 将固定的 GUID（Globally Unique Identifier）与客户端提供的 Sec-WebSocket-Key 字符串拼接
                '258EAFA5-E914-47DA-95CA-C5AB0DC85B11' 是一个固定的 GUID字符串，是 WebSocket 握手协议规定的标准部分
        2. 使用 hashlib.sha1() 对拼接后的字符串进行 SHA-1 哈希运算
        3. 再通过 digest() 方法返回哈希值的二进制形式，
        4. 最后使用 decode() 将 Base64 编码后的字节对象转换为字符串格式
        """
        accept_key = base64.b64encode(
            hashlib.sha1((ws_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        ).decode()

        # 发送 WebSocket 握手响应
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_key}\r\n"
            "\r\n"
        )
        self.writer.write(response.encode())
        await self.writer.drain()

    async def read_websocket_frame(self):
        """服务器解析接收到的 WebSocket 数据帧
        Returns:
            None
        """

        try:
            # 读取前 2 个字节
            header = await self.reader.readexactly(2)
            byte1, byte2 = struct.unpack("!BB", header)

            fin = byte1 >> 7  # FIN 标志
            opcode = byte1 & 0x0F  # 操作码
            mask = byte2 >> 7  # 是否有掩码
            payload_len = byte2 & 0x7F  # 载荷长度

            if payload_len == 126:
                payload_len = struct.unpack("!H", await self.reader.readexactly(2))[0]
            elif payload_len == 127:
                payload_len = struct.unpack("!Q", await self.reader.readexactly(8))[0]

            if mask:
                masking_key = await self.reader.readexactly(4)  # 读取掩码
                payload = await self.reader.readexactly(payload_len)  # 读取数据
                payload = bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))  # 解除掩码
            else:
                payload = await self.reader.readexactly(payload_len)

            return payload.decode("utf-8")
        except Exception as e:
            print(f"读取websocket帧时出错: {e}")
            return None

    async def send_frame(self, payload: dict, opcode: int = 0x1):
        """发送 WebSocket 数据帧

        Args:
            payload: 要发送的字符串数据
            opcode: 操作码 (0x1: 文本, 0x2: 二进制, 0x8: 关闭连接)

        Returns:
            None
        """
        payload = json.dumps(payload, ensure_ascii=False)
        payload_bytes = payload.encode()
        payload_len = len(payload_bytes)

        # 构造 WebSocket 帧
        if payload_len <= 125:
            frame_header = struct.pack("!BB", 0x80 | opcode, payload_len)
        elif payload_len <= 65535:
            frame_header = struct.pack("!BBH", 0x80 | opcode, 126, payload_len)
        else:
            frame_header = struct.pack("!BBQ", 0x80 | opcode, 127, payload_len)

        self.writer.write(frame_header + payload_bytes)
        await self.writer.drain()
