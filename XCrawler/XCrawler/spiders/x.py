import scrapy


class XSpider(scrapy.Spider):
    name = "x"
    allowed_domains = ["x.com"]
    start_urls = ["https://x.com"]

    def parse(self, response):
        pass
