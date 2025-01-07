from project_frame.multiprocess_server_main import ServerManager
from script.traverse_folder import import_all_functions_in_folder

if __name__ == "__main__":
    """
    这里文件的动态引入和 route_dict 字典的传递有三种用法：
        第一种：将下述两行代码放在文件最顶端，所有模块和路由处理程序都在主进程中加载，而主程序在启动子程序的时候会复制一份资源到子程序的内存中，这样子进程就无需重新加载，子进程可以直接使用主进程中加载的资源（例如，路由处理程序）来减少冗余开销
        第二种：将下述两行代码放在子进程启动函数内部，所有模块和路由处理程序都在子进程中加载，会消耗较多的资源，且耗时更久
        第三种：将下述两行代码放在文件main函数中执行，并且通过传参的方式传给子进程。这种方法只需要加载一次资源，并且不需要复制过多的资源给子进程，只需要传递一个字典，开销比较小

        本项目中，route_handlers 在应用运行期间不需要频繁更新且不需要跨进程共享和同步，第三种写法是最合适的。这种方式在进程数量较多的情况下，能有效减少系统的资源消耗
    """
    from decoratorFunc.getFuncDict import route_handlers # 在主进程中引入 route_handlers
    import_api_func_dict = import_all_functions_in_folder("api_func_set") # 动态引入所有 api 函数

    server_manager = ServerManager(8866, 8888, route_handlers, import_api_func_dict)  # 创建 ServerManager 实例
    server_manager.start_server()  # 启动服务器
