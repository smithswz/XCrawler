# XCrawler
基于scrapy爬虫框架的分布式爬虫，用于爬取X（原twitter）的用户发布的公开帖子

# 数据库
需要redis,postgre和mongodb
```
├── main_base.py              // 启动scrapy爬虫
├── scrapy.cfg
├── XCrawler
│   ├── config.yaml           // 数据库配置
│   ├── distribute_tanks.py   // 任务推送到redis的程序，需要单独启动
│   ├── format_data.py        // 处理爬取到的数据
│   ├── get_config.py         // 获取数据库配置文件的信息
│   ├── __init__.py
│   ├── items.py              
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── request_async.py      // 用curl_cffi请求接口
│   ├── settings.py
│   └── spiders
│       ├── __init__.py
│       └── x.py
└── XCrawler.sql              // postgre数据库结构文件
```
