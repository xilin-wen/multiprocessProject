# from decoratorFunc.getFuncDict import get_func_dict
# from hot_reload.try_by_self import HandleFuncFromClient
#
#
# client_func_handler = HandleFuncFromClient()
#
# @get_func_dict('/editServerFunc', method='post', token_required=False)
# def edit_server_func(ctx, data):
#     print(666)
#     print("data", data)
#     res = client_func_handler.edit_func(data.func_str)
#     if res:
#         return {
#             "code": 200,
#             "message": "修改成功"
#         }
#     else:
#         return {
#             "code": 400,
#             "message": res
#         }
#
#
# @get_func_dict('/deleteServerFunc', method='post')
# def delete_server_func(ctx, data):
#     res = client_func_handler.delete(data.func_name)
#
#     if res:
#         return {
#             "code": 200,
#             "message": "删除成功"
#         }
#     else:
#         return {
#             "code": 400,
#             "message": res
#         }
