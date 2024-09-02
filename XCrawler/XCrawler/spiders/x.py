import json
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
import logging
import traceback
import time
from XCrawler.items import XcrawlerItem
import psycopg2
from XCrawler.format_data import get_article
from XCrawler import get_config
logger = logging.getLogger(__name__)


class XSpider(RedisSpider):
    name = "x"
    allowed_domains = ["x.com"]
    redis_key = "start_urls"

    def parse(self, response, **kwargs):
        api_data = response.json()
        # 上次采集到最新帖子的时间
        stop_time = response.meta['stop_time']
        # X用户的个人id
        user_id = response.meta['user_id']
        # 在数据库的id
        _id = response.meta['id']
        # 第一次采集的帖子数量
        stop_count = response.meta['stop_count']
        # 是否为第一次请求
        is_first = response.meta['is_first']
        if self.content(api_data,_id):
            # 解析爬取的数据
            all_data = get_article(api_data,stop_time,is_first)
            response.meta['count_num'] += len(all_data['data'])
            for data in all_data['data']:
                item = XcrawlerItem()
                item['user_id_str'] = data['user_id_str']
                item['name'] = data['name']
                item['user_name'] = data['user_name']
                item['header_link'] = data['header_link']
                item['create_time'] = data['create_time']
                item['X_full_text'] = data['X_full_text']
                item['X_link'] = data['X_link']
                item['photo_list'] = data['photo_list']
                item['video_list'] = data['video_list']
                item['quote_result'] = data['quote_result']
                item['x_info_inner'] = data['x_info_inner']
                item['is_download'] = 0
                yield item
            if is_first:
                self.update_stop_time(all_data['stop_time'],_id)
                response.meta['is_first'] = False
            if all_data['next_status'] or response.meta['count_num'] >= stop_count:
                api_url = self.format_nexturl(api_data,user_id)
                yield Request(api_url,callback=self.parse,meta=response.meta)

    def content(self,data,_id):
        if data['data']['user'] == {}:
            logger.error(f"user_id失效")
            sql = f' update "X_Information" set status = 2 where id = {_id}'
            sql_account = get_config.postgreconfig()
            db_data = psycopg2.connect(host=sql_account['link'],user=sql_account['user'],password = sql_account['passwd'],database = sql_account['dbname'],port=sql_account['port'])
            cursor = db_data.cursor()
            try:
                cursor.execute(sql)
                db_data.commit()
            except Exception as e:
                logger.error(f"更新数据库错误：{e}")
                db_data.rollback()
            cursor.close()
            db_data.close()
            return False
        return True

    def format_nexturl(self,data,_id):
        '''
        组合获取下一页的url
        '''
        next_token = data.get('data').get('user').get('result').get('timeline_v2').get('timeline').get('instructions')[-1].get('entries')[-1].get('content').get('value')
        url = "https://x.com/i/api/graphql/GA3HM3gm-TtZJNVsvnF5Yg/UserTweets?variables={}&features={}&fieldToggles={}"
        variables = {
            "userId":_id,
            "count":20,
            "cursor":next_token,
            "includePromotedContent":False,
            "withQuickPromoteEligibilityTweetFields":True,
            "withVoice":False,
            "withV2Timeline":True
        }
        features ={
            "responsive_web_graphql_exclude_directive_enabled":True,
            "verified_phone_label_enabled":False,
            "creator_subscriptions_tweet_preview_api_enabled":True,
            "responsive_web_graphql_timeline_navigation_enabled":True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
            "communities_web_enable_tweet_community_results_fetch":True,
            "c9s_tweet_anatomy_moderator_badge_enabled":True,
            "tweetypie_unmention_optimization_enabled":True,
            "responsive_web_edit_tweet_api_enabled":True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
            "view_counts_everywhere_api_enabled":True,
            "longform_notetweets_consumption_enabled":True,
            "responsive_web_twitter_article_tweet_consumption_enabled":True,
            "tweet_awards_web_tipping_enabled":False,
            "freedom_of_speech_not_reach_fetch_enabled":True,
            "standardized_nudges_misinfo":True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":True,
            "rweb_video_timestamps_enabled":True,
            "longform_notetweets_rich_text_read_enabled":True,
            "longform_notetweets_inline_media_enabled":True,
            "responsive_web_enhance_cards_enabled":False
        }
        fieldToggles = {
            "withArticlePlainText":False
        }
        return url.format(json.dumps(variables,ensure_ascii=False),json.dumps(features,ensure_ascii=False),json.dumps(fieldToggles,ensure_ascii=False))



    def update_stop_time(self,stop_time,_id):
        '''
        更新最新的帖子时间
        '''
        # sql = f" update "X_Information" set stop_time = '{stop_time}' where id = {_id} "
        sql = ' update "X_Information" set stop_time = ' + f" '{stop_time}' where id = {_id}"
        sql_account = get_config.postgreconfig()
        db_data = psycopg2.connect(host=sql_account['link'],user=sql_account['user'],password = sql_account['passwd'],database = sql_account['dbname'],port=sql_account['port'])
        cursor = db_data.cursor()
        try:
            cursor.execute(sql)
            db_data.commit()
        except Exception as e:
            logger.error(f"更新数据库错误：{e}")
