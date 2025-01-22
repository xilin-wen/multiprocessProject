import asyncio
import websockets
import json


class ChangeData:
    def __init__(self, input):
        self. input = input
        self.feco_real_time = dict({
                                "battery": {
                                    "percentage": 85,  # 电量百分比，范围0-100
                                    "charging": False  # 是否正在充电，False 表示未充电，True 表示正在充电
                                },
                                "power": {
                                    "blade1": 100,  # 1号刀盘功率，单位W
                                    "blade2": 120,  # 2号刀盘功率，单位W
                                    "blade3": 110,  # 3号刀盘功率，单位W
                                    "motor1": 150,  # 1号行走电机功率，单位W
                                    "motor2": 160   # 2号行走电机功率，单位W
                                },
                                "bladeSpeed": {
                                    "blade1": 1200,  # 1号刀盘转速，单位RPM
                                    "blade2": 1300,  # 2号刀盘转速，单位RPM
                                    "blade3": 1250   # 3号刀盘转速，单位RPM
                                },
                                "motorSpeed": {
                                    "motor1": 3.5,  # 1号行走电机速度，单位km/h
                                    "motor2": 3.8   # 2号行走电机速度，单位km/h
                                },
                                "xyz": {
                                    "x": 15.2,  # X轴角度，单位°
                                    "y": 30.0,  # Y轴角度，单位°
                                    "z": 45.0   # Z轴角度，单位°
                                },
                                "remote": True  # 遥控器连接状态，True 表示已连接，False 表示未连接
                            })

    def check_range_of_input(self, data = None, template = None, path=""):
        """
        验证数据是否符合预定义结构（递归检查键）。
        参数：
        - data: 待验证的输入数据（字典类型）
        - template: 预定义的模板结构（字典类型）
        - path: 用于记录当前字段的路径（字符串）
        返回值：
        - 如果验证成功，返回 (True, None)；
        - 如果验证失败，返回 (False, 错误字段的路径)。
        """
        if not data: data = self.input
        if not template: template = self.feco_real_time
        if not isinstance(data, dict) or not isinstance(template, dict):  # 如果 data 或 template 不是字典
            return False, path or "根节点不是字典"  # 返回失败及路径提示

        for key in data:  # 遍历待验证数据中的每个键
            current_path = f"{path}.{key}" if path else key  # 构建当前字段的完整路径
            if key not in template:  # 如果当前键不在模板的键中
                print(f"错误: 无效的字段 '{current_path}' 不在预定义结构中")  # 打印错误信息，指明无效键的路径
                return False, current_path  # 返回失败及无效键的路径

            if isinstance(data[key], dict):  # 如果当前键对应的值是一个字典
                result, error_path = self.check_range_of_input(data[key], template[key], current_path)
                if not result:  # 如果嵌套验证失败
                    return False, error_path  # 返回失败及错误字段的路径

        return True, None  # 如果所有键都通过验证，返回成功

    def update_second_level(self):
        """
        只更新目标字典中已有的二级键值。
        """
        for key, value in self.input.items():
            if key in self.feco_real_time and isinstance(self.feco_real_time[key], dict) and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key in self.feco_real_time[key]:  # 只更新已存在的二级键
                        print(f"更新 '{key}' 的二级字段 '{sub_key}' 为值 '{sub_value}'")
                        self.feco_real_time[key][sub_key] = sub_value

    def start(self):
        res, error = self.check_range_of_input()
        if res:
            self.update_second_level()
            return True
        else:
            return error

# 定义 WebSocket 服务器处理函数
async def feco_date(websocket):
    print("新连接已建立...")
    try:
        # 持续接收并回传客户端消息
        async for message in websocket:
            message_json = json.loads(message)  # 将字符串解析为字典

            print(f"收到消息: {message_json}")

            change_data = ChangeData(message_json)
            res = change_data.start()
            send_res = {
                "status": 200 if res else 400,
                "message": "修改成功" if res else res
            }
            print("发送的消息:",  send_res)

            await websocket.send(json.dumps(send_res))

    except Exception as e:
        print(f"连接错误: {e}")
    finally:
        print("连接关闭")

# 每 5 秒向客户端发送当前时间
async def send_data(websocket):
    while True:
        data = {
            # "timestamp": datetime.datetime.now().isoformat(),
            "message": "Hello, this is your periodic data!"
        }
        await websocket.send(str(data))
        print(f"Sent: {data}")
        await asyncio.sleep(5)


# 启动 WebSocket 服务器
async def start_server():
    server_show = await websockets.serve(send_data, "0.0.0.0", 8855)
    server_update = await websockets.serve(feco_date, "0.0.0.0", 8877)
    print("WebSocket 服务器已启动，监听端口 8855...")
    print("WebSocket 服务器已启动，监听端口 8877...")
    # await server_show.wait_closed()
    # await server_update.wait_closed()
    await asyncio.gather(server_show.wait_closed(), server_update.wait_closed())


# 运行事件循环
if __name__ == "__main__":
    asyncio.run(start_server())
