import ast
import time


# 装饰器例子
def handle(url):
    print(url)

    def wrapper(func):
        def run(*args, **kwargs):
            return func(*args, **kwargs)

        return run

    return wrapper


# handle_class管理类
class Manage:
    def __init__(self):
        self.handle_class = dict()
        self.tmp_handle_class = dict()

    def add(self, obj_str):
        try:
            try:
                # str->语法分析树
                tree = ast.parse(obj_str)
            except SyntaxError as e:
                return e
            class_name = ""
            # 获得类名
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
            if class_name == "":
                # 未获得类名
                raise Exception("have no class")
            # 实例化类并奖他放进暂存列表, 这里会自动调用装饰器
            exec(f"{obj_str}\ntmp={class_name}()\nmanage.tmp_handle_class[tmp.func_name] = tmp")
            # 这里做测试隔离，分配一个临时id列表，这个id列表id的token进来的消息都会由老方法+新替换方法执行，其他的请求则是老方法
            print(self.tmp_handle_class["add_person"])
        except Exception as e:
            print(e)

    def upgrade(self, func_name):
        # 如果测试通过，接收到了正式上线方法的命令
        self.handle_class[func_name] = self.tmp_handle_class[func_name]
        del self.tmp_handle_class[func_name]

    def delete(self, func_name):
        # 如果要删除某个方法
        del self.handle_class[func_name]
        del self.tmp_handle_class[func_name]
        # 装饰器里的映射关系别忘了删


if __name__ == "__main__":
    # 如果不用类的话，你就post请求带上一些函数的信息进行配置
    # 如果用类的话，就可以直接类参数里面带
    # 只要能映射url->func就行了，所以核心在于替换func指针
    # 传入字符串正确性用ast和动态执行去确认，只要崩溃不影响其他函数就行，也就是try exp最外层要有
    # 函数带了装饰器的进来会自动触发装饰器，以此去绑定路由
    # 把部分id划分为测试id，相同路由进行函数的区分，没问题则上线
    # 你现在只需要完成具体逻辑了，demo都在这了还不会
    # 自己找个茅坑吃撑
    manage = Manage()
    manage.add('''class func1:
    def __init__(self):
        # 这里传递一些需要的信心
    self.func_name = "add_person"
        self.method = "POST"
        self.need_token = True

    @handle(url="/a")
    def handle(self):
        print(self.value)
    ''')

    while True:
        time.sleep(1)
