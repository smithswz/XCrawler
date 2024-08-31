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
    user_avatar = Field()
    create_time = Field()
    tweet_full_text = Field()
    tweet_link = Field()
    photo_list = Field()
    video_list = Field()
    quote_result = Field()
    x_info_inner = Field()
    file_name = Field()
    publish_id = Field()
    is_download = Field()
