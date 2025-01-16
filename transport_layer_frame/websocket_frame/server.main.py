import asyncio
import websockets
import json

from api_func_set.control_light_belt import LampBeltControl


# 定义 WebSocket 服务器处理函数
async def echo(websocket):
    print("新连接已建立...")
    try:
        # 持续接收并回传客户端消息
        async for message in websocket:
            print(f"收到消息: {message}")

            message_json = json.loads(message)  # 将字符串解析为字典
            scenario_type = message_json.get("scenario_type", None)
            color = message_json.get("color", None)
            config_data = message_json.get("data", {})

            strip = LampBeltControl()
            res = strip.handle_scenario(scenario_type, color=color, config_data=config_data)
            print(f"发送的消息: {res}")

            if res:
                if isinstance(res, str):
                    await websocket.send(res)
                else:
                    await websocket.send(json.dumps(res))

    except Exception as e:
        print(f"连接错误: {e}")
    finally:
        print("连接关闭")


# 启动 WebSocket 服务器
async def start_server():
    server = await websockets.serve(echo, "0.0.0.0", 8765)
    print("WebSocket 服务器已启动，监听端口 8765...")
    await server.wait_closed()


# 运行事件循环
if __name__ == "__main__":
    asyncio.run(start_server())