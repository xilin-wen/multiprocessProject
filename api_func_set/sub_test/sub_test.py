from decoratorFunc.getFuncDict import get_func_dict

data_hello = {"message": "Hello, world!"}
data_goodbye = {"message": "Goodbye, world!"}

# 定义多个路由处理函数
@get_func_dict('/hello', method='get', token_required=False,)
def handle_hello(ctx, data):
    print("ctx", ctx)
    print("data", data)
    body = {
        "ctx": ctx,
        "data": data
    }
    body.update(data_hello)
    return {
        "code": 200,
        "message": "this is a message",
        "body": body
    }

@get_func_dict('/goodbye', method='post')
def handle_goodbye(ctx, data):
    print("ctx", ctx)
    print("data", data)
    print("123456")
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