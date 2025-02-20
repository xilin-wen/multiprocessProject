import sys
from pprint import pprint

pprint(sys.meta_path)

import PANDAG_fileName as remote_module  # 将通过自定义机制从配置的URL加载

print(remote_module.test())