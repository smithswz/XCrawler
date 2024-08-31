# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from fake_useragent import UserAgent
import pymongo
from XCrawler import get_config
logger = logging.getLogger(__name__)


class XcrawlerPipeline:
    def __init__(self) -> None:
        self.g_ua = UserAgent()

    def process_item(self, item, spider):
        try:
            config_mogo = get_config.mogodbconfig()
            db_link = config_mogo['link']
            db_port = config_mogo['port']
            db_name = config_mogo['dbname']
            db_client = pymongo.MongoClient(host=db_link, port=db_port)
            db = db_client[db_name]
            collection = db["data"]
            collection.insert_one(dict(item))
            db_client.close()
        except Exception as e:
            logger.error(f"写入数据错误:{e}")
        return item
