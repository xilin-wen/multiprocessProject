"""
文件描述: 本文件用于多进程、协程启动项目

创建者: 汐琳
创建时间: 2024-12-25 15:53:24
"""
import asyncio
import multiprocessing  # 导入多进程模块
import os  # 导入操作系统模块，用于获取CPU核心数
import signal  # 导入信号模块，用于捕获进程信号
import time
import platform  # 用于判断操作系统类型
from typing import Literal
import psutil

from hot_reload2.check_file_change import FolderWatcher
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
        self.os_type = platform.system()  # 获取操作系统类型
        self.cpu_cores_number = self.get_cpu_cores_count()  # 根据操作系统获取 CPU 核心数量


    def get_cpu_cores_count(self):
        """
        根据操作系统类型获取 CPU 核心数量，并防止 os.cpu_count() 返回 None
        """
        if self.os_type == "Windows":
            return os.cpu_count() or 1
        elif self.os_type == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    return sum(1 for line in f if line.startswith("processor")) or 1
            except FileNotFoundError:
                return os.cpu_count() or 1
        elif self.os_type == "Darwin":  # macOS
            return os.cpu_count() or 1
        else:
            print(f"未知操作系统: {self.os_type}，默认使用单核。")
            return 1

    async def start_server_worker(self):
        """
        启动单个异步 HTTP 服务器实例
        """
        server = HTTPServer(self.port, self.route_dict, self.api_func_dict)  # 使用自定义 HTTPServer 类
        await server.start()  # 启动 HTTPServer（异步操作）
        await asyncio.Future()  # 防止退出（保持运行状态）

    async def listen_file_change(self):
        """
        监听文件变化的协程，包含多个特定任务
        """
        # 特定任务 1：每隔一分钟打印一次当前时间
        async def print_time_periodically(os_type):
            while True:
                await asyncio.sleep(60)  # 每隔60秒执行一次
                print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

        # 这里可以增加其他任务来处理文件变化等
        async def other_task():
            while True:
                pass

        # 启动并行执行多个任务
        await asyncio.gather(print_time_periodically(self.os_type), other_task())

    def worker_process(self, task_type: Literal['http_server', 'listen_file_change']):
        """
        单个进程的工作函数，运行 asyncio 事件循环，且处理进程中的异常，确保进程崩溃时会重启
        """
        loop = None  # 确保 loop 变量在 try 块外部就已经声明
        while True:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)  # 将新的事件循环设置为当前线程的默认事件循环
                # 根据 task_type 选择对应的函数并调用，返回协程对象
                if task_type == 'http_server':
                    task = self.start_server_worker
                elif task_type == 'listen_file_change':
                    print(123)
                    watcher = FolderWatcher(folder_name="api_func_set")  # 创建监听器实例
                    task = watcher.start_watch  # 选择文件变化监听任务
                else:
                    raise ValueError(f"未知的任务类型: {task_type}")
                # 在事件循环中启动异步 HTTP 服务器
                loop.run_until_complete(task())
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
        启动服务器并管理子进程，并将每个进程绑定到特定核心
        """
        num_workers = os.cpu_count() or 1  # 获取操作系统中 CPU 核心数量 防止 os.cpu_count() 返回 None
        special_project_tasks_cpu = 1 * 2 # 用于处理项目特殊任务的进程
        other_task_cpu = 1 * 2

        # 如果 CPU 超过 4 个，则保留两个 CPU 用于启动独立的进程
        if num_workers > 4 * 2:
            start_workers = num_workers - other_task_cpu  # 保留 2 个 CPU 用来启动独立的进程
        else:
            start_workers = num_workers

        http_server_cpu = start_workers - special_project_tasks_cpu or 1 # 用于处理 http 请求的 cpu = 启动进程的 cpu - 执行特殊任务的 cpu

        processes = [] # 用于存放所有子进程

        # 启动多个子进程，并绑定进程到指定核心
        for i in range(start_workers):
            if i <= http_server_cpu:
                process = multiprocessing.Process(target=self.worker_process, args=('http_server',))  # 创建新进程，并传递核心索引
            else:
                process = multiprocessing.Process(target=self.worker_process, args=('listen_file_change',))  # 创建新进程，并传递核心索引
            processes.append(process)  # 将进程添加到进程列表中
            process.start()  # 启动进程

            # 获取当前进程的进程 ID (PID)
            pid = process.pid

            # 使用 psutil 绑定进程到指定核心
            cpu_core = i % num_workers  # 将进程分配到不同的核心
            p = psutil.Process(pid)
            p.cpu_affinity([cpu_core])  # 绑定到指定核心

        self.processes = processes

        # 捕获终止信号并优雅退出
        signal.signal(signal.SIGTERM, self.graceful_exit)
        signal.signal(signal.SIGINT, self.graceful_exit)

        # 等待所有进程结束
        for process_item in self.processes:
            process_item.join()  # 等待子进程退出