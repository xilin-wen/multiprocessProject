import ast
from decoratorFunc.getFuncDict import route_handlers


class HandleFuncFromClient:
    def __init__(self):
        self.handle_class = dict()  # 初始化一个字典，用于存储正式上线的类方法
        self.tmp_handle_class = dict()  # 初始化一个字典，用于存储临时的类方法（测试阶段）

    def edit_func(self, obj_str):  # 添加一个新的类定义（字符串形式），并进行处理
        try:
            try:
                # 使用 ast.parse() 将传入的类定义字符串解析为抽象语法树（AST）
                tree = ast.parse(obj_str)
                # print("语法树的详细信息===>", ast.dump(tree, indent=4))
            except SyntaxError as e:
                # 如果解析失败，则返回语法错误
                print(f"函数定义错误：{e}")
                return e

            class_name = ""  # 初始化一个空字符串，用于保存类名

            # 获得类名
            for node in ast.walk(tree):  # 遍历语法树中的所有节点
                if isinstance(node, ast.ClassDef):  # 判断节点是否为一个类定义节点
                    class_name = node.name  # 获取类名

            if class_name == "":  # 未获取到类名，则抛出异常
                raise Exception("have no class")

            # 实例化类并将其放进暂存列表
            """
            exec() 是 Python 中的一个内置函数，用于执行动态生成的 Python 代码，这里动态执行传入的类定义字符串，并创建一个类实例 tmp
                —— exec 存在安全性问题，因此需要谨慎修改：
                    1. 通过正则匹配拒绝一些系统文件性的修改
                    2. 使用 ip 限制访问
                    3. 将端口和对客户端开启的端口分开，以进行隔离 -- 需要解决问题：函数是共享的
            """
            # print(f"{obj_str}\ntmp={class_name}()\nmanage.tmp_handle_class[tmp.func_name] = tmp")
            exec(f"{obj_str}\ntmp={class_name}()\nmanage.tmp_handle_class[tmp.func_name] = tmp")

            # 测试隔离：输出 tmp_handle_class 中 "add_person" 路由的方法实例，确认是否成功添加
            # 这里做测试隔离，分配一个临时id列表，这个id列表id的token进来的消息都会由老方法+新替换方法执行，其他的请求则是老方法
            print(self.tmp_handle_class["add_person"])
        except Exception as e:
            print(e)  # 如果出现异常，打印错误信息

    def upgrade(self, func_name):
        # 升级方法：如果测试通过，接收到正式上线方法的命令
        self.handle_class[func_name] = self.tmp_handle_class[func_name]  # 替换正式方法
        del self.tmp_handle_class[func_name]  # 从临时方法字典中删除该方法

    def delete(self, func_name):  # 删除方法：删除指定的路由和方法
        try:
            if self.handle_class[func_name] and self.tmp_handle_class[func_name]:
                # 删除方法：删除正式和临时方法
                del self.handle_class[func_name]
                del self.tmp_handle_class[func_name]
            else:
                print(f"{func_name} 函数不存在")
                return False
            # 删除装饰器中的映射关系
            return self.remove_handler_by_func_name(func_name)
        except:
            raise Exception(f"{func_name} 函数删除失败")

    @staticmethod
    def remove_handler_by_func_name(func_name):
        # 遍历所有路径和方法
        for path, methods in route_handlers.items():
            for method, handler in methods.items():
                # 如果 func_name 匹配，则删除该 handler
                if handler.get("func_name") == func_name:
                    try:
                        del methods[method]  # 删除当前 method 下的 handler
                        return
                    except:
                        raise Exception(f"{route_handlers} 中的 {func_name} 函数删除失败")
                else:
                    print(f"{route_handlers} 中不存在 {func_name} 函数")
                    return False