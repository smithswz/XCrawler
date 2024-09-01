from curl_cffi.requests import AsyncSession
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.exceptions import IgnoreRequest
import random
import logging
import psycopg2
from XCrawler import get_config

proxies = [
    {"https":"192.168.1.254:10811"}
]

class CurlCffiDownloaderMiddleware:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        self.logger.info('Spider opened: %s' % spider.name)

    async def process_request(self, request, spider):
        try:
            proxy = random.choice(proxies)
            header = request.meta['headers']
            cookie = request.meta['cookies']
            async with AsyncSession() as s:
                response = await s.get(request.url,impersonate="edge101",headers=header,proxies=proxy,cookies=cookie)
            if response.status_code == 429:
                self.update_account_status(request.meta['cookie_id'])
                self.logger.warning(f"返回429错误码，在数据库中进行标记")
                return
            return HtmlResponse(
                url=request.url,
                status=response.status_code,
                body=response.content,
                request=request,
            )
        except Exception as e:
            self.logger.error(f'Request failed: {e}')
            raise IgnoreRequest

    def process_response(self, request, response, spider):
        # Just return the response
        return response

    def process_exception(self, request, exception, spider):
        # Log exception and return None to continue processing
        self.logger.error(f'Exception occurred: {exception}')
        return None
    
    def update_account_status(self,id):
        '''
        标记数据库中状态码为429的账号
        '''
        sql = f' update "X_account" set status = 1 where id = {id} '
        sql_account = get_config.postgreconfig()
        db_data = psycopg2.connect(host=sql_account['link'],user=sql_account['user'],password = sql_account['passwd'],database = sql_account['dbname'],port=sql_account['port'])
        cursor = db_data.cursor()
        try:
            cursor.execute(sql)
            db_data.commit()
        except Exception as e:
            self.logger.error(f"更新数据库错误：{e}")
