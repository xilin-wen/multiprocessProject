import json  # 导入 JSON 模块，用于数据格式化
from shared_data import SharedData  # 导入共享数据管理类

# 请求处理函数，根据请求路径返回不同的响应
def handle_request(request):
    # 解析 HTTP 请求（假设请求格式为 "METHOD /path HTTP/1.1"）
    method, path, _ = request.split(' ', 2)  # 拆分请求行，获取方法、路径和协议

    if path == '/increment':
        return handle_increment()  # 如果请求路径是 /increment，调用 handle_increment
    elif path == '/get_data':
        return handle_get_data()  # 如果请求路径是 /get_data，调用 handle_get_data
    else:
        return "HTTP/1.1 404 Not Found\r\n\r\nPage Not Found"  # 如果路径不匹配，返回 404 错误

# 处理递增共享变量的请求
def handle_increment():
    # 获取共享数据管理实例
    shared_data = SharedData()
    with shared_data.shared_variable.get_lock():  # 使用锁来保证线程安全
        shared_data.shared_variable.value += 1  # 递增共享变量的值
    # 返回包含当前值的 JSON 响应
    return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps({"value": shared_data.shared_variable.value})

# 处理获取共享数据的请求
def handle_get_data():
    # 获取共享数据管理实例
    shared_data = SharedData()
    # 组装数据字典
    data = {
        "queue_size": shared_data.queue.qsize(),  # 获取队列的大小
        "dict_data": dict(shared_data.shared_dict),  # 获取字典数据
        "list_data": list(shared_data.shared_list),  # 获取列表数据
        "variable_value": shared_data.shared_variable.value  # 获取共享变量的值
    }
    # 返回包含数据的 JSON 响应
    return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps(data)
