import psycopg2
import get_config
import redis
import logging
import json
from fake_useragent import UserAgent
from datetime import datetime
import time
from threading import Thread
import re
import random
import requests

cookie_num = 0
KEY = 'start_urls'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logfile = 'logger.txt'
fh = logging.FileHandler(logfile, mode='a',encoding='utf-8', delay=False)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


class GetAllUserID:
    '''
    获取所有的目标的user_id
    '''
    def __init__(self) -> None:
        self.au = UserAgent()
        self.proxies = [
            {"https":"192.168.1.254:10811"}
        ]
    

    def get_token(self):
        '''
        获取访问token
        '''
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        }
        proxy = random.choice(self.proxies)
        response = requests.get(url='https://x.com'+'?mx=2',headers=headers,proxies=proxy)
        data = re.findall('gt=(\\d+)',response.text)
        if len(data) == 0:
            return None
        return data[0]
    
    def format_id_url(self,url):
        name = url.split('/')[-1]
        api_url = 'https://api.x.com/graphql/qW5u-DAuXpMEG0zA1F7UGQ/UserByScreenName?variables={}&features={}&fieldToggles={}'
        variables = {
            "screen_name":name,
            "withSafetyModeUserFields":True
        }
        features = {
            "hidden_profile_likes_enabled": True,
            "hidden_profile_subscriptions_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "subscriptions_verification_info_is_identity_verified_enabled": True,
            "subscriptions_verification_info_verified_since_enabled": True,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_notes_tab_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True
        }
        fieldToggles = {
            "withAuxiliaryUserLabels":False
        }
        api_url = api_url.format(json.dumps(variables,ensure_ascii=False),json.dumps(features,ensure_ascii=False),json.dumps(fieldToggles,ensure_ascii=False))
        return api_url
    
    def update_UserId(self,_id,id):
        sql = '''
        update "X_Information" set status = 0,target_id = %s where id = %s
        '''
        psycopgdb = get_config.postgreconfig()
        db_data = psycopg2.connect(
                            host = psycopgdb['link'],
                            user = psycopgdb['user'],
                            password = psycopgdb['passwd'],
                            database = psycopgdb['dbname'],
                            port = psycopgdb['port']
                        )
        cursor = db_data.cursor()
        try:
            cursor.execute(sql,(_id,id))
            db_data.commit()
        except Exception as e:
            logger.error(f"更新数据库错误{e}")
            db_data.rollback()

    def request(self,data):
        try:
            url = self.format_id_url(data['url'])
            token = self.get_token()
            header = {
                'User-Agent':self.au.random,
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'x-guest-token': token,
                'content-type': 'application/json'
            }
            proxy = random.choice(self.proxies)
            response = requests.get(url,headers=header,proxies=proxy)
            response_data = response.json()
            user_Id = response_data.get('data').get('user').get('result').get('rest_id')
            data['user_id'] = user_Id
            self.update_UserId(user_Id,data['id'])
        except Exception as e:
            logger.error(f'获取user_id错误:{e}')
            data['user_id'] = None
        return data


def push_data(datas):
    '''
    向redis发送需要爬取的任务
    '''
    psycopgdb = get_config.redisconfig()
    redis_obj = redis.StrictRedis(host=psycopgdb['link'], port=psycopgdb['port'], db=psycopgdb['dbname'])
    pipeline = redis_obj.pipeline()
    tank_num = 0
    for data in datas:
        if data['user_id'] == None or data['status'] == 2:
            data = GetAllUserID().request(data)
        if tank_num == 0:
            cookie = get_cookies()
        if data['stop_time'] == None:
            stop_count = 100
        else:
            stop_count = 999
        tank_data = {
            'url':format_url(data['user_id']),
            "meta": {
                "cookie_id":cookie.get('id'),
                "target_id":data.get('id'),
                "stop_count":stop_count,
                "stop_time":data.get('stop_time'),
                'headers':{
                    'User-Agent':UserAgent().random,
                    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                    'content-type': 'application/json',
                    'X-Csrf-Token': cookie.get('cookie').get('ct0')
                },
                'cookies':cookie.get('cookie'),
                'user_id':data['user_id'],
                'get_first': True,
                'id':data['id'],
                'is_first':True,
                'count_num':0
            }
        }
        pipeline.rpush(KEY,json.dumps(tank_data,ensure_ascii=False))
        tank_num += 1
        if tank_num == 5:
            tank_num = 0
            pipeline.execute()
    pipeline.execute()
    pipeline.close()
    redis_obj.close()


def format_url(userId):
    '''
    拼接第一次请求的url
    '''
    features ={
            "responsive_web_graphql_exclude_directive_enabled":True,
            "verified_phone_label_enabled":False,
            "rweb_tipjar_consumption_enabled": True,
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
    variables = {
            "userId":userId,
            "count":20,
            "includePromotedContent":False,
            "withQuickPromoteEligibilityTweetFields":True,
            "withVoice":False,
            "withV2Timeline":True
        }
    fieldToggles = {
            "withArticlePlainText":False
        }
    api_url = "https://x.com/i/api/graphql/GA3HM3gm-TtZJNVsvnF5Yg/UserTweets?variables={}&features={}&fieldToggles={}"
    url = api_url.format(json.dumps(variables,ensure_ascii=False),json.dumps(features,ensure_ascii=False),json.dumps(fieldToggles,ensure_ascii=False))
    return url

def get_cookies():
    '''
    根据获取到的目标数获取采集账号cookie
    '''
    global cookie_num
    sql = 'select id,cookie from "X_account" where status != 2 and get_num = {} LIMIT 1'
    psycopgdb = get_config.postgreconfig()
    db_data = psycopg2.connect(
                    host = psycopgdb['link'],
                    user = psycopgdb['user'],
                    password = psycopgdb['passwd'],
                    database = psycopgdb['dbname'],
                    port = psycopgdb['port']
                )
    cursor = db_data.cursor()
    while True:
        cursor.execute(sql.format(str(cookie_num)))
        data = cursor.fetchall() 
        if len(data) != 0:
            break
        cookie_num += 1
    update_num(data[0],cookie_num+1,db_data,cursor)
    cursor.close()
    db_data.close()
    cookie = format_cookie(data[0][1])
    return {'cookie':cookie,'id':data[0][0]}


def update_num(_id,num,db_data,cursor):
    sql = ' update "X_account" set get_num = %s where id = %s '
    try:
        cursor.execute(sql,(num,_id[0]))
        db_data.commit()
    except Exception as e:
        logger.error(f"更新数据库错误{e}")
        db_data.rollback()


def format_cookie(datas):
    _data = json.loads(datas)
    cookies = dict()
    for data in _data:
        cookies[data['name']] = data['value']
    return cookies

def refresh_num():
    '''
    每15分钟，更新一下账号为429状态的账号
    每天过0点刷新所有账号的使用次数
    '''
    global cookie_num
    # 刷新所有账号的使用次数为0
    sql1 = '''
        update "X_account" set get_num = 0
    '''
    # 回复所有账号429状态的账号为正常状态
    sql2 = '''
        update "X_account" set status = 0 where status = 1
    '''
    DAY = datetime.now().strftime('%Y%m%d')
    psycopgdb = get_config.postgreconfig()
    while True:
        db_data = psycopg2.connect(
                    host = psycopgdb['link'],
                    user = psycopgdb['user'],
                    password = psycopgdb['passwd'],
                    database = psycopgdb['dbname'],
                    port = psycopgdb['port']
                )
        cursor = db_data.cursor()
        try:
            cursor.execute(sql2)
            db_data.commit()
            now = datetime.now().strftime('%Y%m%d')
            if DAY < now:
                cursor.execute(sql1)
                db_data.commit()
                cookie_num = 0
        except Exception as e:
            logger.error(f"执行sql错误，{e}")
        finally:
            cursor.close()
            db_data.close()
        time.sleep(15)


def take_tank():
    '''
    获取所有的任务,并且取出需要爬取的任务目标
    '''
    sql = '''
        SELECT id,url,target_id,stop_time,status FROM "X_Information" where status != 1
    '''
    psycopgdb = get_config.postgreconfig()
    db_data = psycopg2.connect(
                    host = psycopgdb['link'],
                    user = psycopgdb['user'],
                    password = psycopgdb['passwd'],
                    database = psycopgdb['dbname'],
                    port = psycopgdb['port']
                )
    cursor = db_data.cursor()
    cursor.execute(sql)
    datas = cursor.fetchall()
    cursor.close()
    db_data.close()
    all_tanks = list()
    for data in datas:
        _data = {
            'id':data[0],
            'stop_count': '',
            'stop_time':data[3],
            'user_id':data[2],
            'last_active_time':data[3],
            'status':data[4],
            'url':data[1]
        }
        if _data['last_active_time'] == None:
            _data['last_active_time'] = '2000-01-01 00:00:00'
        if _data['stop_time'] == None:
            _data['stop_time'] = '2000-01-01 00:00:00'
        all_tanks.append(_data)
    return all_tanks

def main():
    Thread(target=refresh_num).start()
    while True:
        push_data(take_tank())
        time.sleep(15*60)

if __name__ == '__main__':
    main()