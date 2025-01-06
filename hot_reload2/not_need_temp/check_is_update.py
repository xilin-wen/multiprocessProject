import os
import time


def check_for_update(module_file, last_modified_time):
    if not os.path.exists(module_file):
        print(f"{module_file} does not exist!")
        return last_modified_time

    # 获取文件的最后修改时间
    current_modified_time = os.path.getmtime(module_file)

    # 如果文件的最后修改时间与上次记录的不同，说明文件已更新
    if current_modified_time != last_modified_time:
        print(f"{module_file} has been updated!")
        return current_modified_time  # 更新修改时间
    return last_modified_time


# 示例：使用该函数来检测模块更新
last_modified_time = 0  # 初始没有修改时间
module_file = '../module.py'

while True:
    last_modified_time = check_for_update(module_file, last_modified_time)
    time.sleep(2)  # 每 2 秒检查一次
