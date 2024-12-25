"""
文件描述: 本文件用于多进程、协程启动服务

创建者: 汐琳
创建时间: 2024-12-25 15:53:24
"""
import asyncio
import multiprocessing  # 导入多进程模块
import os  # 导入操作系统模块，用于获取CPU核心数
import signal  # 导入信号模块，用于捕获进程信号
import time
import platform  # 用于判断操作系统类型

from http_frame.server import HTTPServer  # 导入 HTTPServer 类，用于处理 HTTP 请求


class ServerManager:
    def __init__(self, port, route_dict, api_func_dict):
        """
        初始化服务器管理器
        :param port: 监听的端口号
        :param route_dict: 路由和 API 函数之间关系的字典
        :param api_func_dict: 动态引入生成的 API 函数字典
        """
        self.port = port
        self.route_dict = route_dict
        self.api_func_dict = api_func_dict
        self.processes = []  # 存储所有子进程对象
        self.cpu_cores_number = self.get_cpu_cores_count()  # 根据操作系统获取 CPU 核心数量

    @staticmethod
    def get_cpu_cores_count():
        """
        根据操作系统类型获取 CPU 核心数量，并防止 os.cpu_count() 返回 None
        """
        os_type = platform.system()  # 获取操作系统类型
        if os_type == "Windows":
            return os.cpu_count() or 1
        elif os_type == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    return sum(1 for line in f if line.startswith("processor")) or 1
            except FileNotFoundError:
                return os.cpu_count() or 1
        elif os_type == "Darwin":  # macOS
            return os.cpu_count() or 1
        else:
            print(f"未知操作系统: {os_type}，默认使用单核。")
            return 1

    async def start_server_worker(self):
        """
        启动单个异步 HTTP 服务器实例
        """
        server = HTTPServer(self.port, self.route_dict, self.api_func_dict)  # 使用自定义 HTTPServer 类
        await server.start()  # 启动 HTTPServer（异步操作）
        await asyncio.Future()  # 防止退出（保持运行状态）

    def worker_process(self):
        """
        单个进程的工作函数，运行 asyncio 事件循环，且处理进程中的异常，确保进程崩溃时会重启
        """
        loop = None  # 确保 loop 变量在 try 块外部就已经声明
        while True:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)  # 将新的事件循环设置为当前线程的默认事件循环
                # 在事件循环中启动异步 HTTP 服务器
                loop.run_until_complete(self.start_server_worker())
            except Exception as e:
                print(f"Worker process crashed: {e}. Restarting...")
                time.sleep(3)  # 等待 3 秒后重启进程，避免立即重启
            finally:
                if loop:
                    loop.close()  # 确保事件循环存在时关闭它

    def graceful_exit(self, signum, frame):
        """
        捕获退出信号并优雅退出
        """
        print("正在终止服务...")
        for process_item in self.processes:
            process_item.terminate()  # 终止子进程
        for process_item in self.processes:
            process_item.join()  # 等待子进程退出
        exit(0)

    def start_server(self):
        """
        启动服务器并管理子进程
        """
        num_workers = os.cpu_count() or 1  # 获取操作系统中 CPU 核心数量 防止 os.cpu_count() 返回 None

        # 如果 CPU 超过 4 个，则保留两个 CPU 用于启动独立的进程
        if num_workers > 4 * 2:
            start_workers = num_workers - 2 * 2  # 保留 2 个 CPU 用来启动独立的进程
        else:
            start_workers = num_workers

        processes = [] # 用于存放所有子进程
        # 启动多个子进程
        for _ in range(start_workers):
            process = multiprocessing.Process(target=self.worker_process)  # 创建新进程
            print("process", process)
            processes.append(process)  # 将进程添加到进程列表中
            process.start()  # 启动进程

        self.processes = processes

        # 捕获终止信号并优雅退出
        signal.signal(signal.SIGTERM, self.graceful_exit)
        signal.signal(signal.SIGINT, self.graceful_exit)

        # 等待所有进程结束
        for process_item in self.processes:
            process_item.join()  # 等待子进程退出