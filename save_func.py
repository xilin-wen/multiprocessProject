# def decorator(params):
#     def decorator_repeat(func):
#         def wrapper(*args, **kwargs):
#             print(args)
#             # for _ in range(num_times):
#             #     result = func(*args, **kwargs)
#             # return result
#
#         return wrapper
#     return decorator_repeat
#
# @decorator(123)
# def test(num: 321):
#     return "this is a test function"
#
# func_dict = {
#     "test": test
# }
#
# print_func = func_dict["test"]
# print(print_func())

def repeat(num_times):
    def decorator_repeat(func):
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator_repeat


@repeat(num_times=3)
def greet(name):
    print(f"Hello {name}")


greet("World")