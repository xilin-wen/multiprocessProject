from decoratorFunc.getFuncDict import get_func_dict
from hot_reload.try_by_self import HandleFuncFromClient

data_hello = {"message": "Hello, world!"}
data_goodbye = {"message": "Goodbye, world!"}

client_func_handler = HandleFuncFromClient()

# 定义多个路由处理函数
@get_func_dict('/hello', method='get', token_required=False,)
def handle_hello(ctx, data):
    body = {
        "ctx": ctx,
        "data": data
    }
    print(321)
    res = client_func_handler.edit_func(data.func_str)
    print(res)
    body.update(data_hello)
    # 这里主动抛出异常
    # raise Exception("触发异常")
    return {
        "code": 200,
        "message": "this is a message",
        "body": body
    }

@get_func_dict('/goodbye', method='post')
def handle_goodbye(ctx, data):
    body = {
        "ctx": ctx,
        "data": data
    }
    body.update(data_goodbye)
    return {
        "code": 200,
        "message": "this is a message",
        "body": body
    }


@get_func_dict('/editServerFunc', method='post', token_required=False)
def edit_server_func(ctx, data):
    print("data", data)
    res = client_func_handler.edit_func(data.func_str)
    if res:
        return {
            "code": 200,
            "message": "修改成功"
        }
    else:
        return {
            "code": 400,
            "message": res
        }