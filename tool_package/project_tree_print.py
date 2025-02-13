"""
文件总述: 用于生成整个项目文件目录

文件详解: 

创建者: 汐琳
创建时间: 2025/2/7 18:39
"""
import re
import importlib
from pathlib import Path
import sys
sys.path.append(Path(__file__).resolve().parent.parent.__str__())
config = importlib.import_module("config")


# mod = importlib.import_moudle_http("http://")
def parse_md_file():
    with open(Path(config.PROJECT_ROOT) / 'doc/README.md', 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r"```plaintext\s*【项目目录】([\s\S]*?)```"
    match = re.search(pattern, content)
    match.group(1).strip() if match else None

class PrintProjectTree:
    def __init__(self):
        self.folder = Path(config.PROJECT_ROOT)
        self.md_tree = ""
        self.new_tree = ""
        self.content_md = ""
        self.pattern = r"```plaintext\s*【项目目录】([\s\S]*?)```"
        self.match = None

    def get_new_project_tree(self, folder: Path = Path(config.PROJECT_ROOT), prefix: str = ""):
        """生成符合 `tree` 命令风格的文件夹结构

        Args:
            folder (Path): 当前文件夹路径
            prefix (str): 当前层级的前缀符号

        Returns:
            str: 生成的树形结构内容
        """
        # 忽略的目录和文件
        ignore_items = {'.git', '.idea', '__pycache__', '.venv', '__init__.py'}

        # 获取当前目录下的所有子项，并按名称排序（忽略大小写）
        # children = sorted(
        #     [child for child in folder.iterdir() if child.name not in ignore_items],
        #     key=lambda x: x.name.lower()
        # )
        children = [child for child in folder.iterdir() if child.name not in ignore_items]

        for index, child in enumerate(children):
            is_last = (index == len(children) - 1)  # 判断是否为当前层级的最后一项
            connector = "└── " if is_last else "├── "
            new_prefix = prefix + ("    " if is_last else "│   ")

            # 添加当前文件/目录
            self.new_tree += f"{prefix}{connector}{child.name}\n"

            # 如果是目录，递归处理
            if child.is_dir():
                self.get_new_project_tree(child, new_prefix)

    def parse_md_file(self) -> None:
        """
        解析 README.md 文件，并获取项目目录部分内容
        """
        with open(Path(config.PROJECT_ROOT) / 'doc/README.md', 'r', encoding='utf-8') as file:
            self.content_md = file.read()

        self.match = re.search(self.pattern, self.content_md)
        tree_content = self.match.group(1).strip() if self.match else None
        self.md_tree = tree_content

    def save_file_project_tree(self):
        # 将树形结构内容写入文件
        with open(Path(config.PROJECT_ROOT) / 'doc/delete.txt', 'w', encoding='utf-8') as file:
            file.write(self.md_tree)

    def save_md_new_tree(self):
        """
        将替换后的目录存入 README.md 文件中
        """
        if self.match:
            # 使用 re.sub 替换匹配到的部分
            update_content_md = re.sub(self.pattern, f"```plaintext\n【项目目录】\n{self.md_tree}\n```", self.content_md)
            with open(Path(config.PROJECT_ROOT) / 'doc/README.md', 'w', encoding='utf-8') as file:
                file.write(update_content_md)
        else:
            print("未找到匹配的部分")
            return self.content_md


    def start(self):
        self.get_new_project_tree()
        self.parse_md_file()

        new_tree_lines = self.new_tree.splitlines() or []
        md_tree_lines = self.md_tree.splitlines() or []

        md_title_annotation = dict()
        for md_tree_file_line in md_tree_lines:
            md_tree_file_name_set = re.search(r"([A-Za-z]\S*)\s*(#.*)?", md_tree_file_line)
            md_folder_title = md_tree_file_name_set.group(1)  # 提取文件或文件夹的名称
            md_annotation = md_tree_file_name_set.group(2).strip() if md_tree_file_name_set.group(2) else ""  # 提取注释部分，若没有注释则为空字符串
            md_title_annotation[md_folder_title] = md_annotation

        new_md_tree_content = ""
        for index, new_tree_line in enumerate(new_tree_lines):
            new_tree_file_name_set = re.search(r"([A-Za-z]\S*)", new_tree_line)
            new_tree_file_name = new_tree_file_name_set.group()
            md_annotation_copy = md_title_annotation.get(new_tree_file_name, "")
            if md_annotation_copy:
                new_md_tree_content = new_md_tree_content + new_tree_line + '   ' + md_annotation_copy + '\n'
            else:
                new_md_tree_content += new_tree_line+ '\n'

        self.md_tree = new_md_tree_content

        # 新增文件、删除文件、修改名称，都好要命啊
        # self.save_file_project_tree() # 将树形结构内容写入一个专门的文件，路径为 doc/delete.txt
        self.save_md_new_tree()

if __name__ == '__main__':
    handle_print_project_tree = PrintProjectTree()
    handle_print_project_tree.start()
