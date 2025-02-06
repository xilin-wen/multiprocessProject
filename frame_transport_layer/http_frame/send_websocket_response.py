import json
from websockets.legacy.server import WebSocketServerProtocol


async def send_ws_message(websocket: WebSocketServerProtocol, message: dict):
    """
    发送 JSON 格式的 WebSocket 消息。

    :param websocket: WebSocket 连接对象
    :param message: 需要发送的消息（字典格式）
    """
    message_json = json.dumps(message, ensure_ascii=False)
    await websocket.send(message_json)