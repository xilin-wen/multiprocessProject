import importlib
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FolderWatcher:
    def __init__(self, folder_name: str, ignore_backup: bool = True):
        """
        初始化文件夹监听器
        :param folder_name: 要监听的文件夹名称（相对于项目根目录）
        :param ignore_backup: 是否忽略备份文件（默认为 True，忽略以 '~' 结尾的文件）
        """
        # 获取项目根目录的上一级路径
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.folder_path = os.path.join(self.project_root, folder_name)  # 拼接要监听的文件夹路径
        self.ignore_backup = ignore_backup

        # 创建观察者
        self.observer = Observer()

    def is_valid_file(self, file_path: str):
        """
        文件名过滤规则：忽略以 '~' 结尾的备份文件
        :param file_path: 文件路径
        :return: 是否为有效文件
        """
        return not (self.ignore_backup and file_path.endswith('~'))

    def on_any_event(self, event):
        """
        事件处理器
        :param event: 文件系统事件
        """
        if event.is_directory or not self.is_valid_file(event.src_path):
            return
        print(f"文件 {event.src_path} 发生变化")
        self.reload_module(event.src_path)

    def reload_module(self, file_path: str):
        """
        动态重新加载模块
        """
        module_name = self.get_module_name(file_path)
        if module_name and module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
                print(f"模块 {module_name} 已重新加载")
            except Exception as e:
                print(f"重新加载模块 {module_name} 失败: {e}")

    def get_module_name(self, file_path: str) -> str | None:
        """
        根据文件路径获取模块名称
        """
        if not file_path.endswith(".py"):
            return None

        relative_path = os.path.relpath(file_path, self.project_root)
        module_name = relative_path.replace(os.sep, ".")[:-3]  # 去掉 `.py`
        return module_name

    def start_watch(self):
        """
        启动文件夹监听
        """
        event_handler = FileSystemEventHandler()  # 使用默认的事件处理器
        event_handler.on_any_event = self.on_any_event  # 替换事件处理方法

        # 设置并启动观察者
        self.observer.schedule(event_handler, self.folder_path, recursive=True)
        self.observer.start()

        print(f"开始监听文件夹: {self.folder_path}")

        try:
            while True:
                time.sleep(1)  # 每秒钟检查一次事件
        except KeyboardInterrupt:
            self.stop_watch()  # 捕获Ctrl+C时停止监听

    def stop_watch(self):
        """
        停止监听文件夹
        """
        self.observer.stop()  # 停止观察者
        self.observer.join()  # 等待所有线程结束