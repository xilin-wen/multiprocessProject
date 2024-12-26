from decoratorFunc.getFuncDict import get_func_dict

data_hello = {"message": "Hello, world!"}
data_goodbye = {"message": "Goodbye, world!"}

# 定义多个路由处理函数
@get_func_dict('/hello', method='get', token_required=False,)
def handle_hello_test(ctx, data):
    body = {
        "ctx": ctx,
        "data": data
    }
    body.update(data_hello)
    # 这里主动抛出异常
    # raise Exception("触发异常")
    return {
        "code": 200,
        "message": "this is a message",
        "body": body
    }

@get_func_dict('/goodbye', method='post')
def handle_goodbye_test(ctx, data):
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