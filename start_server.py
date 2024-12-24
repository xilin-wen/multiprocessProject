import asyncio
import multiprocessing  # 导入多进程模块
import os  # 导入操作系统模块，用于获取CPU核心数
import signal  # 导入信号模块，用于捕获进程信号
import time
import platform  # 用于判断操作系统类型

from decoratorFunc.getFuncDict import route_handlers
from script.traverse_folder import import_all_functions_in_folder
from shared_data import SharedData  # 导入共享数据管理类
from http_frame.server import HTTPServer # 导入 HTTPServer 类，用于处理 HTTP 请求


class StartMultiprocessServer:
    def __init__(self, port):
        """
        :param port: 监听的端口号
        """
        self.port = port
        self.queue = SharedData().shared_queue  # 创建跨进程共享队列
        self.processes = [] # 存储所有子进程对象
        # self.loop = None  # 确保 loop 变量在 try 块外部就已经声明
        self.manager = multiprocessing.Manager()
        # 获取 CPU 核心数，决定创建多少个进程
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
        server = HTTPServer(self.port, self.queue)  # 使用自定义 HTTPServer 类
        await server.start()  # 启动 HTTPServer（异步操作）
        await asyncio.Future()  # 防止退出（保持运行状态）

    def start_multiprocess(self):
        """
        单个进程的工作函数，运行 asyncio 事件循环，且处理进程中的异常，确保进程崩溃时会重启
            --后续需要加入日志和错误跟踪，用于记录每个进程的状态、异常和重启
        """
        loop = None
        while True:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.start_server_worker())
            except Exception as e:
                print(f"Worker process crashed: {e}. Restarting...")
                time.sleep(3)
            finally:
                if loop:
                    loop.close()

    # 捕获终止信号并优雅退出
    def setup_signal_handlers(self):
        """
        设置信号处理程序以优雅退出
        """
        def graceful_exit(signum, frame):
            print("终止服务...")
            for process in self.processes:
                process.terminate()
            for process in self.processes:
                process.join()
            exit(0)

        signal.signal(signal.SIGTERM, graceful_exit)
        signal.signal(signal.SIGINT, graceful_exit)

    def monitor_processes(self):
        """
        监控子进程的状态并在崩溃时重启
        """
        while True:
            for i, process in enumerate(self.processes):
                if not process.is_alive():
                    print("工作进程异常，正在重新启动，请稍后......")
                    new_process = multiprocessing.Process(target=self.start_multiprocess)
                    self.processes[i] = new_process
                    new_process.start()
            time.sleep(1)

    # 启动服务器的函数
    def start_server(self):
        """
        启动多个子进程以运行 HTTP 服务器
        """
        # 创建跨进程共享队列
        # 如果 CPU 超过 4 个，则保留两个 CPU 用于启动独立的进程
        if self.cpu_cores_number > 4 * 2:  # 4 * 2： 4 个 CPU ，每个 CPU 有 2 个核心
            start_workers = self.cpu_cores_number - 2 * 2  # 保留 2 个 CPU 用来启动独立的进程
        else:
            start_workers = self.cpu_cores_number

        # 启动多个子进程
        for _ in range(start_workers):
            process = multiprocessing.Process(target=self.start_multiprocess)  # 创建新进程
            self.processes.append(process)  # 将进程添加到进程列表中
            process.start()  # 启动进程

        self.setup_signal_handlers()
        self.monitor_processes()

    def start(self):
        """
        启动服务器管理器
        """
        import_all_functions_in_folder("api_func_set")
        self.start_server()

# 主程序入口
if __name__ == "__main__":
    server_manager = StartMultiprocessServer(port=8866)
    server_manager.start()
