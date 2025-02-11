## 文件结构

```plaintext
【项目目录】
├── api_func_set   # 接口函数
│   ├── feco_api   # 小铁硬件相关的接口
│   │   └── control_light_belt.py   # 控制灯带
│   ├── server_api
│   │   └── handle_func_from_client.py
│   ├── sub_test2.py
│   └── sub_test_api
│       └── sub_test.py
├── config.py
├── database   # 数据库字段类型
│   ├── branch.py   # 商家端数据库
│   ├── consumer.py   # 客户端数据库
│   └── Internal.py   # 公司内部数据库
├── decoratorFunc
│   └── getFuncDict.py
├── doc # 各类文档
│   └── README.md   # 项目主文档
├── frame_project
│   └── main_multiprocess_server.py
├── frame_transport_layer
│   ├── http_frame
│   │   ├── IP_restrictions.py
│   │   ├── main_http_server.py
│   │   └── send_http_response.py
│   └── websocket_frame
│       ├── feco_control.py
│       ├── feco_control_serve.py
│       └── main_ws_server.py
├── hot_reload
│   ├── demo.py
│   ├── handle_route_api_set.py
│   └── main_edit_func.py
├── main.py
├── requirements.txt
├── script
│   ├── project_tree_print.py
│   ├── save_project_root_path.py
│   └── traverse_folder.py
├── tool_database
│   └── MySQLClient.py
└── user
    └── authority.py

```

