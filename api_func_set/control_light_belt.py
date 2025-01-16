import colorsys
import re
from typing import Union, List



class LampBeltControl:
    def __init__(self, num_lamp=19, total_weight=100):
        """初始化灯带，默认有19个灯泡"""
        self.num_lamp = num_lamp
        self.return_lamp_array = []
        self.total_weight = total_weight

    #     parts = self.count_num_lamp_belt_sub_part()
    #     self.num_first_part = parts["num_first_part"]
    #     self.num_second_part = parts["num_first_part"]
    #     self.num_third_part = parts["third_part"]
    #
    # def count_num_lamp_belt_sub_part(self):
    #     num_first_part = self.num_lamp // 3
    #     third_part = self.num_lamp - 2 * num_first_part
    #     return {
    #         "num_first_part": num_first_part,
    #         "third_part": third_part
    #     }

    def write_single_config(self, *, interval:Union[str, int]=0, colors: Union[str, List[str]] =None, number_control_lamp=0, delay=0, duration=0, lamp_index=0):
        """
        配置灯带的通用控制方法

        :param lamp_index: 当前灯泡在数组中的下标 --仅在跑马灯中使用
        :param duration:灯泡在一个周期内亮起的时间
        :param interval: 灯泡在一个周期内熄灭的时间
        :param colors: 灯泡的颜色（默认使用RGB颜色）。
        :param number_control_lamp: 控制灯泡的数量，仅在需要设置常亮灯泡时使用。
        :param delay: 灯泡亮起间隔时间
        """
        if not number_control_lamp:
            number_control_lamp = self.num_lamp

        for operated_lamp in range(number_control_lamp):
            config_operated_lamp = {
                "color": colors or "rgb(0, 0 0)",
                "interval": interval or 0,  # 默认灯泡两次亮起间的间隔时间为 0 --一个周期内熄灭的时间
                "delay": delay * lamp_index  or 0,  # 默认第一个灯泡亮起时间的延迟为 0
                "duration": duration or 0 # 默认灯泡亮起保持时间为 0 --一个周期内亮起的时候
            }
            self.return_lamp_array.append(config_operated_lamp)

    def handle_scenario(self, scenario_type, *, config_data, color):
        """
        根据场景类型执行相应的灯带模式。
        多值颜色对应规则：
            将 1-100 粗暴分为三段，分别是 [0, 33], (33,66] ,(66,100]
            将 19 个灯泡简单分为 3 段，每段分别有 7、7、5个灯泡，每段分别和上述的三段之一对应
                -- 如果想要更具体，则每个灯泡代表5.2左右

        :param color:
        :param config_data:
        :param scenario_type: 场景类型 A、B、C、D 等
        # :param power: 机器运转功率
        # :param battery: 机器剩余电量
        # :param delay: 机器亮起延长时间

        """
        valid_types = ['charging', 'in_operation', 'fault', 'in_running', 'disconnect_remote']
        if scenario_type not in valid_types:
            raise ValueError(f"{scenario_type}场景错误")

        print("config_data", config_data)
        battery = config_data.get("battery", 0)
        power = config_data.get("power", 0)
        delay = config_data.get("delay", 0)
        interval = config_data.get("interval", 0)
        duration = config_data.get("duration", 0)

        lamp_color = "rgb(255, 255, 255)" # 默认无色
        lamp_color_low = "rgb(0, 255, 0)" # 低程度默认值
        lamp_color_middle = "rgb(255, 255, 0)" # 中程度默认值
        lamp_color_high = "rgb((128, 0, 128)" # 高程度默认值
        if color:
            if isinstance(color, str):
                lamp_color = color
            elif isinstance(color, dict):
                lamp_color_low = color.get("low", "rgb(0, 255, 0)")
                lamp_color_middle = color.get("middle", "rgb(255, 255, 0)")
                lamp_color_high = color.get("high", "rgb((128, 0, 128)")
        else:
            return "缺少必要参数：颜色"

        if scenario_type == 'charging':
            # 充电中：设置常亮灯泡并且最后一个闪烁
            if battery:
                num_lamp_work_charging = int(self.find_bulb_for_value(battery))
                print("num_lamp_work_charging", num_lamp_work_charging)

                for index in range(num_lamp_work_charging - 1):
                    self.write_single_config(colors=lamp_color, number_control_lamp=1, interval="False",
                                             duration=duration, delay=delay)

                self.write_single_config(colors=lamp_color, number_control_lamp=1, interval=interval, duration=duration)
            else:
                # raise ValueError("缺少必要参数剩余电量 battery")
                return "缺少必要参数剩余电量：battery"
        elif scenario_type == 'in_operation':
            # 运行中：所有灯泡常亮，整个灯带呈渐变色，并且灯泡的数量代表功率的强弱
            if power:
                color_set = self.generate_gradient_between_three_colors(lamp_color_low, lamp_color_middle, lamp_color_high)

                num_lamp_work = int(self.find_bulb_for_value(power))

                for index in range(num_lamp_work):
                    self.write_single_config(colors=color_set[index], number_control_lamp=1, interval=interval, duration=duration, delay=delay)
            else:
                return "缺少必要参数：机器功率"
        elif scenario_type == 'fault':
            r = 0
            g = 0
            b = 0
            match = re.match(r"rgb\(([^,]+),([^\),]+),([^\)]+)\)", lamp_color)
            if match:
                # 提取 r, g, b 的值
                r = float(match.group(1))
                g = float(match.group(2))
                b = float(match.group(3))

            color_str = self.generate_breathing_colors_from_rgb(r, g, b)

            # 故障中：红色中等速度的呼吸灯
            self.write_single_config(colors=color_str, number_control_lamp=self.num_lamp, interval=interval, duration=duration, delay=delay)
        elif scenario_type == 'in_running':
            # 遥控器连接成功：跑马灯模式 --> 常亮，并且亮灯数量和颜色反应电量状态
            if battery:
                num_lamp_work_in_running = int(self.find_bulb_for_value(battery))

                color_set = self.generate_gradient_between_three_colors(lamp_color_low, lamp_color_middle,
                                                                        lamp_color_high)

                for index in range(num_lamp_work_in_running):
                    self.write_single_config(colors=color_set[index], number_control_lamp=1, interval=interval,
                                             duration=duration, delay=delay, lamp_index=index)
            else:
                raise ValueError("缺少必要参数：剩余电量")
        elif scenario_type == 'disconnect_remote':
            # 遥控器连接失败：绿色中等速度闪烁
            self.write_single_config(colors=lamp_color, number_control_lamp=self.num_lamp, interval=interval, duration=duration)

        if len(self.return_lamp_array) < 19:
            num_cycles = self.num_lamp - len(self.return_lamp_array) or 1
            for _ in range(num_cycles):
                self.return_lamp_array.append({
                    "color": "rgb(0, 0, 0)",
                    "interval": "False",
                    "delay":  0,
                    "duration": 0
                })


        return_lamp =dict({})
        for index, value in enumerate(self.return_lamp_array):
            return_lamp[index] = value

        return return_lamp

    @staticmethod
    def generate_breathing_colors_from_rgb(r, g, b, steps=10):
        """
        根据给定的 RGB 颜色生成适合呼吸灯效果的颜色序列，主要通过调整亮度。

        :param r: 红色分量 (0-255)
        :param g: 绿色分量 (0-255)
        :param b: 蓝色分量 (0-255)
        :param steps: 呼吸灯渐变的步数
        :return: 颜色序列 (列表)
        """
        # 将 RGB 转换为 HLS（Hue, Lightness, Saturation）模式
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

        # 生成渐变色：亮度从低到高，再从高到低
        colors = []

        # 从亮度低到高
        for i in range(steps + 1):
            # 计算当前亮度值
            lightness = l * (i / steps)
            # 将 HLS 转回 RGB
            r_new, g_new, b_new = colorsys.hls_to_rgb(h, lightness, s)
            colors.append(f"rgb{(int(r_new * 255), int(g_new * 255), int(b_new * 255))}")

        # 从亮度高到低
        for i in range(steps - 1, -1, -1):
            lightness = l * (i / steps)

            # 确保亮度不为 0
            if lightness < 0.1:
                break

            r_new, g_new, b_new = colorsys.hls_to_rgb(h, lightness, s)
            colors.append(f"rgb{(int(r_new * 255), int(g_new * 255), int(b_new * 255))}")

        return colors

    @staticmethod
    def rgb_to_tuple(rgb_str):
        # 将rgb字符串转换为元组 (r, g, b)
        rgb_str = rgb_str.strip("rgb()")  # 去除 'rgb(' 和 ')'
        rgb_values = rgb_str.split(",")  # 分割为 r, g, b
        return tuple(int(float(value.strip())) for value in rgb_values)  # 先转换为 float，再转为整数

    def generate_gradient_between_three_colors(self, color_first, color_second, color_third):
        """
            生成一个基于三个颜色的渐变列表。

            该函数根据输入的三个颜色，生成从第一个颜色到第二个颜色、再从第二个颜色到第三个颜色之间的渐变颜色。
            渐变的步数通过首尾渐变占比与中间渐变占比来控制，使得首尾部分的渐变幅度更大，中间部分的渐变幅度较小。

            参数:
            - color_first (str): 起始颜色，RGB 格式字符串（例如：'rgb(255, 0, 0)'）。
            - color_second (str): 中间颜色，RGB 格式字符串。
            - color_third (str): 结束颜色，RGB 格式字符串。

            返回:
            - List[str]: 包含渐变颜色的 RGB 字符串列表，按渐变顺序排列。

            说明：
            - 渐变的步数会根据总步数 `num_lamp` 的比例来调整：首尾部分分别占 40%，中间部分占剩余的 20%。
            - 如果 `num_lamp` 设置得较小，可能不会有中间渐变，渐变会更集中在首尾部分。
            """

        # 内部函数：计算两个颜色之间的渐变
        def interpolate_color(color, sub_color, steps):
            # 提取两个颜色的 RGB 值
            r1, g1, b1 = color
            r2, g2, b2 = sub_color

            # 计算每个颜色通道的步进值
            step_r = (r2 - r1) / (steps - 1)  # 计算红色通道的步进值
            step_g = (g2 - g1) / (steps - 1)  # 计算绿色通道的步进值
            step_b = (b2 - b1) / (steps - 1)  # 计算蓝色通道的步进值

            # 初始化渐变颜色列表
            gradient = []
            for i in range(steps):
                # 根据步进值计算每一阶的颜色，并四舍五入至整数
                r = round(r1 + step_r * i)
                g = round(g1 + step_g * i)
                b = round(b1 + step_b * i)

                # 将计算得到的颜色转为字符串并添加到渐变列表中
                gradient.append(f"rgb({r}, {g}, {b})")

            return gradient

        # 将输入的 rgb 字符串转换为元组形式，方便后续处理
        color_first = self.rgb_to_tuple(color_first)
        color_second = self.rgb_to_tuple(color_second)
        color_third = self.rgb_to_tuple(color_third)

        # 假设 num_lamp 为总步数，调整比例：首尾渐变各占 40%，中间部分占 20%
        first_to_second_steps = int(self.num_lamp * 0.4) + 1  # 第一个渐变的步数
        second_to_third_steps = int(self.num_lamp * 0.4) + 1  # 第二个渐变的步数
        middle_steps = self.num_lamp - first_to_second_steps - second_to_third_steps  # 中间渐变的步数

        # 计算从 color1 到 color2 的渐变
        gradient1 = interpolate_color(color_first, color_second, first_to_second_steps)

        # 计算从 color2 到 color3 的渐变
        gradient2 = interpolate_color(color_second, color_third, second_to_third_steps)

        # 如果有中间渐变（即 middle_steps 大于 0），生成中间渐变的颜色
        if middle_steps > 0:
            # 计算从 color2 到 color3 的过渡渐变
            middle_gradient = interpolate_color(color_second, color_third, middle_steps)
            # 合并渐变时加上中间渐变部分
            gradient_all = gradient1[:-1] + middle_gradient[1:-1] + gradient2
        else:
            # 没有中间渐变时，直接合并
            gradient_all = gradient1[:-1] + gradient2

        return gradient_all

    def find_bulb_for_value(self, value):
        """
        用于计算传入值对应第几枚灯泡
        :param value:
        :return:
        """
        # 灯泡权重设定
        num_bulbs = self.num_lamp
        # 从第二枚开始到结尾的灯泡对应的权重
        subsequent_bulb_weight = (100 / self.num_lamp * 10) // 1 / 10
        # 第一枚开灯泡对应的权重
        first_bulb_weight = round(100 - subsequent_bulb_weight * (self.num_lamp - 1), 1)

        # 计算所有灯泡的总权重

        # 计算给定值所处的总权重区间
        normalized_value = (value / 100) * self.total_weight

        # 根据权重查找对应的灯泡
        if normalized_value <= first_bulb_weight:
            return 1  # 第一个灯泡
        else:
            # 从第二个灯泡开始，减去第一个灯泡的权重
            remaining_value = normalized_value - first_bulb_weight
            bulb_index = 2 + (remaining_value // subsequent_bulb_weight)
            return min(bulb_index, num_bulbs)  # 确保返回的灯泡索引不超过 19