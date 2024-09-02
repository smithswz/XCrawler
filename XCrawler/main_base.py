import os
import sys
from scrapy.cmdline import execute

# 获取当前脚本路径
dirpath = os.path.dirname(os.path.abspath(__file__))

# 运行文件绝对路径
print(os.path.abspath(__file__))

# 运行文件父路径
print(dirpath)

# 添加环境变量
sys.path.append(dirpath)

# 切换工作目录
os.chdir(dirpath)

# 启动爬虫, 第三个参数为爬虫name

execute(['scrapy', 'crawl', 'x'])
