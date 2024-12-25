import asyncio
import multiprocessing  # 导入多进程模块
import os  # 导入操作系统模块，用于获取CPU核心数
import signal  # 导入信号模块，用于捕获进程信号
import time

from http_frame.server import HTTPServer  # 导入 HTTPServer 类，用于处理 HTTP 请求
from script.traverse_folder import import_all_functions_in_folder


class ServerManager:
    def __init__(self, port, route_dict, api_func_dict):
        """
        初始化服务器管理器
        :param port: 监听的端口号
        :param route_dict: 路由和 API 函数之间关系的字典
        :param api_func_dict: API 函数字典
        """
        self.port = port
        self.route_dict = route_dict
        self.import_api_func_dict = api_func_dict
        self.processes = []  # 存储所有子进程对象

    async def start_server_worker(self):
        """
        启动单个异步 HTTP 服务器实例
        """
        server = HTTPServer(self.port, self.route_dict, self.import_api_func_dict)  # 使用自定义 HTTPServer 类
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

        # 启动多个子进程
        for _ in range(start_workers):
            process = multiprocessing.Process(target=self.worker_process)  # 创建新进程
            self.processes.append(process)  # 将进程添加到进程列表中
            process.start()  # 启动进程

        # 捕获终止信号并优雅退出
        signal.signal(signal.SIGTERM, self.graceful_exit)
        signal.signal(signal.SIGINT, self.graceful_exit)

        # 等待所有进程结束
        for process_item in self.processes:
            process_item.join()  # 等待子进程退出


# 主程序入口
if __name__ == "__main__":
    """
    这里文件的动态引入和 route_dict 字典的传递有三种用法：
        第一种：将下述两行代码放在文件最顶端，所有模块和路由处理程序都在主进程中加载，而主程序在启动子程序的时候会复制一份资源到子程序的内存中，这样子进程就无需重新加载，子进程可以直接使用主进程中加载的资源（例如，路由处理程序）来减少冗余开销
        第二种：将下述两行代码放在子进程启动函数内部，所有模块和路由处理程序都在子进程中加载，会消耗较多的资源，且耗时更久
        第三种：将下述两行代码放在文件main函数中执行，并且通过传参的方式传给子进程。这种方法只需要加载一次资源，并且不需要复制过多的资源给子进程，只需要传递一个字典，开销比较小

        本项目中，route_handlers 在应用运行期间不需要频繁更新且不需要跨进程共享和同步，第三种写法是最合适的。这种方式在进程数量较多的情况下，能有效减少系统的资源消耗
    """
    from decoratorFunc.getFuncDict import route_handlers

    import_api_func_dict = import_all_functions_in_folder("api_func_set")

    server_manager = ServerManager(8866, route_handlers, import_api_func_dict)  # 创建 ServerManager 实例
    server_manager.start_server()  # 启动服务器
