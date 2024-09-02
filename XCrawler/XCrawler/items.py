# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field
import scrapy


class XcrawlerItem(scrapy.Item):
    user_id_str = Field()
    name = Field()
    user_name = Field()
    header_link = Field()
    create_time = Field()
    X_full_text = Field()
    X_link = Field()
    photo_list = Field()
    video_list = Field()
    quote_result = Field()
    x_info_inner = Field()
    is_download = Field()
