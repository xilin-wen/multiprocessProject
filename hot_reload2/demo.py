import time
import importlib
import os

# 用于控制热更新是否启用的全局变量
hot_reload_enabled = False


# 创建或检查模块是否存在
def create_module():
    if not os.path.exists("module.py"):
        with open("module.py", "w") as f:
            f.write("""
                def greet():
                    return "Hello, World!"
            """)


# 加载模块并检测更新
def load_module():
    try:
        module = importlib.import_module("module")
        importlib.reload(module)  # 强制重新加载模块
    except ModuleNotFoundError:
        print("Module not found, creating a new one.")
        create_module()
        module = importlib.import_module("module")
    return module


# 检查模块是否更新
def check_for_update(last_modified_time):
    if not os.path.exists("module.py"):
        print("module.py does not exist!")
        return last_modified_time
    current_modified_time = os.path.getmtime("module.py")
    if current_modified_time != last_modified_time:
        print("Module updated!")  # 输出更新提示
        return current_modified_time
    return last_modified_time


# 控制热更新的启用或禁用
def toggle_hot_reload(enable: bool):
    global hot_reload_enabled
    hot_reload_enabled = enable
    if hot_reload_enabled:
        print("Hot reload is ENABLED.")
    else:
        print("Hot reload is DISABLED.")


# 主程序
def main():
    last_modified_time = 0  # 初始时没有修改时间

    while True:
        user_input = input("Enter command: ('r' to check for updates, 'q' to quit, 't' to toggle hot reload): ")

        if user_input.lower() == 'q':
            break  # 用户选择退出
        elif user_input.lower() == 'r':
            if hot_reload_enabled:
                last_modified_time = check_for_update(last_modified_time)  # 手动触发更新检查
                module = load_module()  # 加载最新的模块
                print(module.greet())  # 调用模块中的 greet 函数
            else:
                print("Hot reload is disabled. Please enable it using 't' command.")

        elif user_input.lower() == 't':
            toggle_hot_reload(not hot_reload_enabled)  # 切换热更新状态
        else:
            print("Invalid command. Please try again.")

        time.sleep(1)  # 每 1 秒休眠一次，避免过度占用 CPU


if __name__ == "__main__":
    create_module()  # 确保模块存在
    main()  # 运行主程序
