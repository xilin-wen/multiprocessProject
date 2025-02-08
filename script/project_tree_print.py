"""
文件总述: 用于生成整个项目文件目录

文件详解: 

创建者: 汐琳
创建时间: 2025/2/7 18:39
"""
from pathlib import Path

import config


def print_tree(folder, content="", depth=0):
    """打印文件夹的树形结构

    Args:
        folder:
        content:
        depth:

    Returns:

    """
    # 输出文件夹名称

    ignore_dirs = ['.git', '.idea', '__pycache__', '.venv', '__init__.py']  # ignore_dirs(arr): 需要忽略的目录

    # 遍历当前目录下的所有文件和文件夹
    for child in folder.iterdir():
        if child.name not in ignore_dirs:
            if child.is_dir():
                    # 如果是目录，递归调用
                    content += "| " * depth + "+--" + child.name + "/\n"  # 添加目录
                    content = print_tree(child, content, depth+1)
            else:
                # 如果是文件，直接输出文件名
                content += "| " * depth + "+--" + child.name + "\n"  # 添加文件

    return content

if __name__ == '__main__':

    folder_path = Path(config.PROJECT_ROOT)
    content_str = print_tree(folder_path)
    print(content_str)

    output_file = folder_path /'doc/project_tree.txt'  # 输出文件路径
    # 将树形结构内容写入文件
    with open(output_file, 'w') as f:
        f.write(content_str)

    print(f"目录树已保存到 {output_file}")
