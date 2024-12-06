import multiprocessing  # 导入多进程模块
import os  # 导入操作系统模块，用于获取CPU核心数
import signal  # 导入信号模块，用于捕获进程信号

from script.traverse_folder import import_all_functions_in_folder
from server import HTTPServer  # 导入 HTTPServer 类，用于处理 HTTP 请求
from shared_data import SharedData  # 导入共享数据管理类

import_all_functions_in_folder("api_func_set")

# 子进程工作函数，接收端口号和队列作为参数
def worker_process(port, queue):
    server = HTTPServer(port, queue)  # 创建 HTTP 服务器实例
    server.serve_forever()  # 启动 HTTP 服务器，持续处理请求

# 启动服务器的函数
def start_server(port):
    # 创建跨进程共享队列
    queue = SharedData().queue

    # 获取 CPU 核心数，决定创建多少个进程
    num_workers = os.cpu_count()  # 获取操作系统中 CPU 核心数量
    processes = []  # 存储所有子进程对象

    # 如果 CPU 超过 4 个，则保留两个 CPU 用于启动独立的进程
    if num_workers > 4 * 2:  # 4 * 2： 4 个 CPU ，每个 CPU 有 2 个核心
        start_workers = num_workers - 2 * 2    # 保留 2 个 CPU 用来启动独立的进程
    else:
        start_workers = num_workers

    # 启动多个子进程
    for _ in range(start_workers):
        process = multiprocessing.Process(target=worker_process, args=(port, queue))  # 创建新进程
        processes.append(process)  # 将进程添加到进程列表中
        process.start()  # 启动进程

    # 等待所有进程结束
    for process in processes:
        process.join()  # 阻塞，直到每个进程结束

# 主程序入口
if __name__ == "__main__":
    # 捕获 SIGTERM 和 SIGINT 信号，保证进程优雅退出 --为什么是在服务器启动前结束？
    signal.signal(signal.SIGTERM, lambda signum, frame: exit(0))  # 捕获终止信号（如 kill 命令）
    signal.signal(signal.SIGINT, lambda signum, frame: exit(0))  # 捕获 Ctrl+C 信号(中断信号)

    start_server(8866)  # 启动服务器，监听 8866 端口
