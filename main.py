import asyncio
import multiprocessing  # 导入多进程模块
import os  # 导入操作系统模块，用于获取CPU核心数
import signal  # 导入信号模块，用于捕获进程信号
import time

from http_frame.server import HTTPServer # 导入 HTTPServer 类，用于处理 HTTP 请求
from script.traverse_folder import import_all_functions_in_folder
from shared_data import SharedData  # 导入共享数据管理类
from decoratorFunc.getFuncDict import route_handlers

async def start_server_worker(port, queue, shared_route_handlers):
    """
    启动单个异步 HTTP 服务器实例
    """
    server = HTTPServer(port, queue, shared_route_handlers)  # 使用自定义 HTTPServer 类
    await server.start()  # 启动 HTTPServer（异步操作）
    await asyncio.Future()  # 防止退出（保持运行状态）

# # 子进程工作函数，接收端口号和队列作为参数
# def worker_process(port, queue, shared_route_handlers):
#     """
#     子进程工作函数，负责启动 HTTPServer 并处理请求。
#     :param port: 监听的端口号
#     :param queue: 跨进程共享队列
#     :param shared_route_handlers: 跨进程共享的路由处理程序字典
#     """
#     server = HTTPServer(port, queue, shared_route_handlers)  # 创建 HTTP 服务器实例
#     server.serve_forever()  # 启动 HTTP 服务器，持续处理请求

def worker_process(port, queue, shared_route_handlers):
    """
    单个进程的工作函数，运行 asyncio 事件循环，且处理进程中的异常，确保进程崩溃时会重启
        --后续需要加入日志和错误跟踪，用于记录每个进程的状态、异常和重启

    :param port: 监听的端口号
    :param queue: 跨进程共享队列
    :param shared_route_handlers: 跨进程共享的路由处理程序字典
    """
    loop = None  # 确保 loop 变量在 try 块外部就已经声明
    while True:
        try:
            # loop = asyncio.get_event_loop()
            # 每次进程崩溃后重新创建一个新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)  # 将新的事件循环设置为当前线程的默认事件循环
            # 在事件循环中启动异步 HTTP 服务器
            loop.run_until_complete(start_server_worker(port, queue, shared_route_handlers))
        except Exception as e:
            print(f"Worker process crashed: {e}. Restarting...")
            time.sleep(3)  # 等待 3 秒后重启进程，避免立即重启
        finally:
            if loop:
                loop.close()  # 确保事件循环存在时关闭它

# def restart_process(port, queue, shared_route_handlers):
#     """
#        进程重启逻辑
#        """
#     print("服务器进程重启中...")
#     time.sleep(3)  # 等待 3 秒后重启进程，避免立即重启
#     # 重新启动新的进程
#     new_process = multiprocessing.Process(target=worker_process, args=(port, queue, shared_route_handlers))
#     new_process.start()

# 启动服务器的函数
def start_server(port):
    # 创建跨进程共享队列
    queue = SharedData().queue

    # 获取 CPU 核心数，决定创建多少个进程
    num_workers = os.cpu_count() or 1  # 获取操作系统中 CPU 核心数量 防止 os.cpu_count() 返回 None
    processes = []  # 存储所有子进程对象

    # 使用 Manager 创建共享字典
    with multiprocessing.Manager() as manager:
        shared_route_handlers = manager.dict(route_handlers)  # 创建共享字典

        # 如果 CPU 超过 4 个，则保留两个 CPU 用于启动独立的进程
        if num_workers > 4 * 2:  # 4 * 2： 4 个 CPU ，每个 CPU 有 2 个核心
            start_workers = num_workers - 2 * 2    # 保留 2 个 CPU 用来启动独立的进程
        else:
            start_workers = num_workers

        # 启动多个子进程
        for _ in range(start_workers):
            process = multiprocessing.Process(target=worker_process, args=(port, queue, shared_route_handlers)) # 创建新进程
            processes.append(process)  # 将进程添加到进程列表中
            process.start()  # 启动进程

        # 捕获终止信号并优雅退出
        def graceful_exit(signum, frame):
            print("终止服务...")
            for process_item in processes:
                process_item.terminate()  # 终止子进程
            for process_item in processes:
                process_item.join()  # 等待子进程退出
            exit(0)

        signal.signal(signal.SIGTERM, graceful_exit)
        signal.signal(signal.SIGINT, graceful_exit)

        # 等待所有进程结束，并监控是否有进程崩溃
        while True:
            for i, processing_item in enumerate(processes):
                print(processing_item)
                if not processing_item.is_alive():  # 如果某个进程没有存活
                    print("工作进程异常，正在重新启动，请稍后......")
                    # 重新启动崩溃的进程
                    new_process = multiprocessing.Process(target=worker_process, args=(port, queue, shared_route_handlers))
                    processes[i] = new_process  # 替换已停止的进程
                    new_process.start()

            time.sleep(1)  # 每秒钟检查一次进程状态

# 主程序入口
if __name__ == "__main__":
    # 捕获 SIGTERM 和 SIGINT 信号，保证进程优雅退出 --为什么是在服务器启动前结束？ -- 改到进程内部实现
    # signal.signal(signal.SIGTERM, lambda signum, frame: exit(0))  # 捕获终止信号（如 kill 命令）
    # signal.signal(signal.SIGINT, lambda signum, frame: exit(0))  # 捕获 Ctrl+C 信号(中断信号)

    # 只在主进程中导入 API 函数，否则每个子进程均会执行一次
    import_all_functions_in_folder("api_func_set")

    start_server(8866)  # 启动服务器，监听 8866 端口
