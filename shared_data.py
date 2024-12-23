import multiprocessing  # 导入多进程模块

class SharedData:
    def __init__(self):
        # 初始化跨进程共享数据
        self.manager = multiprocessing.Manager()  # 创建一个进程管理器
        self.shared_queue  = self.manager.Queue()  # 创建共享队列
        self.shared_dict = self.manager.dict()  # 创建共享字典
        self.shared_list = self.manager.list()  # 创建共享列表
        self.shared_variable = self.manager.Value('i', 0)  # 创建共享整数变量，初始值为 0
        self.shared_float = self.manager.Value('d', 0.0)  # 创建共享浮动变量，初始值为 0.0
        self.shared_string = self.manager.Value('s', b'')  # 创建共享字符串（字节类型），初始为空
        self.shared_array = self.manager.Array('i', [0] * 10)  # 创建共享整型数组，初始长度为 10，值为0
        self.shared_event = self.manager.Event()  # 创建共享事件（用于同步）
        self.shared_lock = self.manager.Lock()  # 创建共享锁（用于进程间同步）

        # 共享字典操作

    def set_dict(self, key, value):
        with self.shared_lock:  # 锁定操作，确保线程安全
            self.shared_dict[key] = value

    def get_dict(self, key):
        with self.shared_lock:
            return self.shared_dict.get(key, None)

    def del_dict(self, key):
        with self.shared_lock:
            if key in self.shared_dict:
                del self.shared_dict[key]

        # 共享列表操作

    def append_list(self, value):
        with self.shared_lock:
            self.shared_list.append(value)

    def get_list(self):
        with self.shared_lock:
            return list(self.shared_list)  # 返回一个拷贝避免直接修改

    def remove_list(self, value):
        with self.shared_lock:
            if value in self.shared_list:
                self.shared_list.remove(value)

        # 共享队列操作

    def put_queue(self, value):
        with self.shared_lock:
            self.shared_queue.put(value)

    def get_queue(self):
        with self.shared_lock:
            if not self.shared_queue.empty():
                return self.shared_queue.get()
            else:
                return None

        # 共享单变量操作

    def set_value(self, value):
        with self.shared_lock:
            self.shared_value.value = value

    def get_value(self):
        with self.shared_lock:
            return self.shared_value.value

        # 共享浮动变量操作

    def set_float(self, value):
        with self.shared_lock:
            self.shared_float.value = value

    def get_float(self):
        with self.shared_lock:
            return self.shared_float.value

        # 共享字符串操作

    def set_string(self, value):
        with self.shared_lock:
            self.shared_string.value = value.encode()  # 字符串需要编码为字节

    def get_string(self):
        with self.shared_lock:
            return self.shared_string.value.decode()  # 解码为字符串

        # 共享数组操作

    def set_array(self, index, value):
        with self.shared_lock:
            self.shared_array[index] = value

    def get_array(self):
        with self.shared_lock:
            return list(self.shared_array)  # 返回数组拷贝

        # 事件操作，用于进程间同步

    def set_event(self):
        with self.shared_lock:
            self.shared_event.set()  # 设置事件

    def clear_event(self):
        with self.shared_lock:
            self.shared_event.clear()  # 清除事件

    def wait_event(self):
        with self.shared_lock:
            self.shared_event.wait()  # 阻塞直到事件被设置

        # 显示当前所有共享数据

    def display_data(self):
        print("Shared Dictionary:", self.shared_dict)
        print("Shared List:", self.shared_list)
        print("Shared Queue:", list(self.shared_queue.queue))  # Convert Queue to list for display
        print("Shared Integer:", self.shared_value.value)
        print("Shared Float:", self.shared_float.value)
        print("Shared String:", self.shared_string.value.decode())
        print("Shared Array:", list(self.shared_array))