"""
文件总述: 将项目的根目录持久化保存到 config.py 这个全局配置文件中
            目前仅支持 windows 系统

创建者: 汐琳
创建时间: 2025/2/8 10:41
"""
from pathlib import Path


def save_project_root_path(project_root: Path):
    """将项目的根目录持久化保存到 config.py 这个全局配置文件中

    Args:
        project_root: 项目根目录路径

    Returns:

    """
    project_root_str = str(project_root).replace("\\", "/") # 将 Path 对象转换为适合保存为变量的字符串

    file_path = Path(project_root) / 'config.py' # 拼凑 config.py 的路径

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines() # 读取 config.py 中的所有行

        # 查找 PROJECT_ROOT 所在的行并替换
        for i, line in enumerate(lines):
            if 'PROJECT_ROOT' in line:
                lines[i] = f"PROJECT_ROOT = '{project_root_str}'\n"  # 替换项目路径
                break  # 找到并替换后停止搜索

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)