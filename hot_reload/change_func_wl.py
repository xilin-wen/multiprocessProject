import ast  # 导入 Python 的抽象语法树（AST）模块，用于解析和分析代码
import time  # 导入 time 模块，用于控制程序的时间延迟


# 装饰器例子
def handle(url):  # 定义装饰器函数，接受一个 URL 参数
    print(url)  # 装饰器运行时打印 URL，表示路由绑定的 URL

    def wrapper(func):  # wrapper 是内部的封装函数，接受被装饰的函数作为参数
        def run(*args, **kwargs):  # run 函数会调用原始函数
            return func(*args, **kwargs)  # 执行原始函数并返回结果

        return run  # 返回 run 函数

    return wrapper  # 返回包装函数


# handle_class管理类
class Manage:  # 定义一个管理类，用于管理路由和方法
    def __init__(self):
        self.handle_class = dict()  # 初始化一个字典，用于存储正式上线的类方法
        self.tmp_handle_class = dict()  # 初始化一个字典，用于存储临时的类方法（测试阶段）

    def add(self, obj_str):  # 添加一个新的类定义（字符串形式），并进行处理
        try:
            try:
                # str->语法分析树，将传入的类定义字符串解析为抽象语法树（AST）
                tree = ast.parse(obj_str)
                # print("obj_str======>", obj_str)
                # print("tree===>", ast.dump(tree, indent=4))
            except:
                # 如果解析失败，则抛出语法错误
                raise Exception("document error")

            class_name = ""  # 初始化一个空字符串，用于保存类名

            # 获得类名
            for node in ast.walk(tree):  # 遍历语法树中的所有节点
                if isinstance(node, ast.ClassDef):  # 如果节点是一个类定义节点
                    class_name = node.name  # 获取类名

            if class_name == "":  # 如果没有找到类名，则抛出异常
                raise Exception("have no class")

            # 实例化类并将其放进暂存列表
            # 动态执行传入的类定义字符串，并创建一个类实例 tmp
            # exec() 是 Python 中的一个内置函数，用于执行动态生成的 Python 代码
            test = f"{obj_str}\ntmp={class_name}()\nmanage.tmp_handle_class[tmp.func_name] = tmp"
            print(test)
            exec(f"{obj_str}\ntmp={class_name}()\nmanage.tmp_handle_class[tmp.func_name] = tmp")

            # 测试隔离：输出 tmp_handle_class 中 "add_person" 路由的方法实例，确认是否成功添加
            print(self.tmp_handle_class["add_person"])
        except Exception as e:
            print(e)  # 如果出现异常，打印错误信息

    def upgrade(self, func_name):  # 升级方法：将临时方法替换为正式方法
        # 如果测试通过，接收到正式上线方法的命令
        self.handle_class[func_name] = self.tmp_handle_class[func_name]  # 替换正式方法
        del self.tmp_handle_class[func_name]  # 从临时方法字典中删除该方法

    def delete(self, func_name):  # 删除方法：删除指定的路由和方法
        # 删除正式和临时方法
        del self.handle_class[func_name]
        del self.tmp_handle_class[func_name]

        # 删除装饰器中的映射关系
        # 注：此处并未完全删除装饰器的路由映射，实际情况可能需要进行额外的清理工作


if __name__ == "__main__":  # 如果是直接运行脚本，则执行以下代码
    # 示例：动态添加一个类定义（类字符串形式）
    manage = Manage()  # 创建一个 Manage 实例，用于管理路由和方法
    manage.add('''class func1:  # 定义一个类字符串
    def __init__(self):  # 构造函数
        # 这里传递一些需要的信心
        self.func_name = "add_person"  # 定义路由的功能名
        self.method = "POST"  # 定义 HTTP 请求方法（POST）
        self.need_token = True  # 是否需要 token 校验

    @handle(url="/a")  # 使用装饰器将 handle 绑定到 URL "/a"
    def handle(self):  # 定义处理请求的类方法
        print(self.value)  # 输出处理结果（此处的 self.value 未定义，需改进代码）
    ''')  # 结束类定义字符串

    # 模拟程序一直在运行，等待进一步操作
    while True:
        time.sleep(1)  # 每 1 秒钟暂停一次，模拟长时间运行的服务
