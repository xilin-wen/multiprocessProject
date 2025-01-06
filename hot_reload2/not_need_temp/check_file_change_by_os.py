import asyncio
import win32file
import win32con

async def check_windows_file_change(path: str):
    """
    监听文件变化，基于Windows API实现
    """
    # 打开目录
    hDir = win32file.CreateFile(
        path,  # 要监控的目录路径
        win32con.GENERIC_READ,  # 只需要读取权限
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,  # 允许其他进程对文件的读取、写入和删除
        None,  # 安全属性
        win32con.OPEN_EXISTING,  # 如果文件不存在，则无法打开
        win32con.FILE_FLAG_BACKUP_SEMANTICS,  # 用于操作文件夹
        None
    )

    # 定义需要监听的事件
    while True:
        # 调用 ReadDirectoryChangesW 来监听目录变化
        results = win32file.ReadDirectoryChangesW(
            hDir,  # 目录句柄
            1024,  # 缓冲区大小
            True,  # 是否递归监听子目录
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,  # 要监听的文件变化类型
            None,  # 不返回事件代码
            None,  # 不返回时间戳
        )

        # 处理文件变化事件
        for action, filename in results:
            print(f"检测到文件变化: {filename}, 动作: {action}")
            if action == win32con.FILE_ACTION_ADDED:
                print(f"文件 {filename} 被创建")
            elif action == win32con.FILE_ACTION_REMOVED:
                print(f"文件 {filename} 被删除")
            elif action == win32con.FILE_ACTION_MODIFIED:
                print(f"文件 {filename} 被修改")
            elif action == win32con.FILE_ACTION_RENAMED_OLD_NAME:
                print(f"文件 {filename} 被重命名为旧文件名")
            elif action == win32con.FILE_ACTION_RENAMED_NEW_NAME:
                print(f"文件 {filename} 被重命名为新文件名")

            # 假设文件变化后的操作，这里可以通过 `await asyncio.sleep` 来模拟一个异步操作
            await asyncio.sleep(1)

async def main():
    await listen_file_change("C:/path_to_your_folder")

if __name__ == "__main__":
    asyncio.run(main())
