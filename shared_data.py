import multiprocessing  # 导入多进程模块

class SharedData:
    def __init__(self):
        # 初始化跨进程共享数据
        self.manager = multiprocessing.Manager()  # 创建一个进程管理器
        self.queue = self.manager.Queue()  # 创建共享队列
        self.shared_dict = self.manager.dict()  # 创建共享字典
        self.shared_list = self.manager.list()  # 创建共享列表
        self.shared_variable = self.manager.Value('i', 0)  # 创建共享整数变量，初始值为 0
        self.shared_float = self.manager.Value('d', 0.0)  # 创建共享浮动变量，初始值为 0.0
        self.shared_string = self.manager.Value('s', b'')  # 创建共享字符串（字节类型），初始为空
        self.shared_array = self.manager.Array('i', [0] * 10)  # 创建共享整型数组，初始长度为 10，值为0
        self.shared_event = self.manager.Event()  # 创建共享事件（用于同步）
        self.shared_lock = self.manager.Lock()  # 创建共享锁（用于进程间同步）
