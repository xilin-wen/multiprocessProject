## 项目简介

[本项目](https://github.com/xilin-wen/multiprocessProject.git ) 是基于 [Python](https://docs.python.org/zh-cn/3/index.html) + [MySQL](https://www.mysqlzh.com/) 等技术栈构建的小铁割草机小程序后端项目

## 项目文档

### 项目结构

```plaintext
【项目目录】
├── api_func_set   # 接口函数
│   ├── feco_api   # 小铁硬件相关的接口
│   │   └── control_light_belt.py   # 控制灯带
│   ├── server_api   # 和服务器相关的 API 函数
│   │   └── handle_func_from_client.py   # 前端修改 API 函数
│   ├── sub_test2.py
│   └── sub_test_api
│       └── sub_test.py
├── config.py   # 项目的全局配置文件，存放全局数据
├── database   # 数据库字段类型
│   ├── branch.py   # 商家端数据库
│   ├── consumer.py   # 客户端数据库
│   └── Internal.py   # 公司内部数据库
├── decoratorFunc   # 装饰器函数
│   └── getFuncDict.py   # 在项目启动时获取所有 API 函数，并生成 API 和路由的映射关系
├── doc   # 各类文档
│   └── README.md   # 项目主文档
├── frame_project   # 项目框架
│   └── main_multiprocess_server.py   # 多进程、协程启动项目
├── frame_transport_layer   # 传输层框架
│   ├── http_frame   # http 框架
│   │   ├── IP_restrictions.py   # 获取本地设备的局域网 IP
│   │   ├── main_http_server.py   # 封装的 http 框架
│   │   └── send_http_response.py   # 将处理后的数据返回给客户端（异步版本）
│   └── websocket_frame   # websocket 框架
│       ├── feco_control.py
│       ├── feco_control_serve.py
│       └── main_ws_server.py
├── hot_reload   # 实现热更新
│   ├── demo.py
│   ├── handle_route_api_set.py
│   └── main_edit_func.py
├── main.py   # 项目主函数
├── requirements.txt
├── script   # 脚本文件，实现一些自动化功能
│   ├── project_tree_print.py   # 输出树形项目目录
│   ├── save_project_root_path.py   # 获取并保存项目的根目录
│   └── traverse_folder.py   # 动态引入 api_func_set 文件夹下的所有 api 函数
├── tool_database   # 数据库
│   └── MySQLClient.py   # MySQL 增删改查的使用
└── user
    └── authority.py
```

### 项目结构更新

对文件或文件夹进行增删改之后，在终端执行 `python script/project_tree_print.py`，`README.md`中【项目目录】将自动更新，原有注释不会被删除

```bash
python script/project_tree_print.py
```

## git提交规范

在提交`git`时，需要标注提交类型

注: 提交类型后需要跟上英文冒号和空格键

```bash
git commit -m "提交类型: 提交内容"
```

【提交类型】：

- `feat`：新功能
- `fix`：修复 bug
- `doc`：文档变更
- `style`：代码风格变动
- `refactor`：代码重构
- `perf`：性能优化
- `test`：添加或修改测试
- `chore`：杂项（构建过程或辅助工具的变化）
- `build`：构建系统或外部依赖项的变更
- `ci`：持续集成配置的变更
- `revert`：回滚
