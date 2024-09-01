import time

def get_article(api_data,stop_time,is_first) -> dict:
    '''
    获取置顶帖和正常发帖的信息
    '''
    return_data = {
        'data':[],
        'stop_time':stop_time,
        'next_status':True
    }
    all_data = list()
    if stop_time == None:
        stop_time == '2000-01-01 00:00:00'
    # 获取数据中存放帖子的列表
    datalist = api_data.get('data').get('user').get('result').get('timeline_v2').get('timeline').get('instructions')
    for data in datalist:
        try:
        # 获取置顶帖
            if data['type'] == "TimelinePinEntry":
                result = data['entry'].get('content').get('itemContent').get('tweet_results').get('result')
                _data = get_parse(result,stop_time)
                if _data != None:
                    all_data.append(_data)
            # 获取正常帖
            elif data['type'] == "TimelineAddEntries":
                entries = data['entries']
                for entry in entries:
                    if 'tweet-' in entry.get('entryId') or 'homeConversation-' in entry.get('entryId'):
                        if entry.get('content').get('entryType') == 'TimelineTimelineItem':
                            result = entry.get('content').get('itemContent').get('tweet_results').get('result')
                            _data = get_parse(result,stop_time)
                            # 解析返回空，结束采集
                            if _data == None:
                                return_data['next_status'] = False
                                break
                            all_data.append(_data)
        except Exception as e:
            print(f"解析帖子错误{e}")
    if is_first:
        return_data['stop_time'] = get_stop_time(all_data)
    return return_data



def get_stop_time(datas):
    '''
    获取最新帖子的时间
    '''
    create_time = ''
    for data in datas:
        if data['create_time'] > create_time:
            create_time = data['create_time']
    return create_time

def get_parse(data,stop_time):
    X_info = None
    if 'Tweet' in data.get('__typename'):
        X_info = get_data(data)
        X_info['x_info_inner'] = None
        X_info['quote_result'] = None
        # 判断是否为转推
        if data.get('__typename') == 'TweetWithVisibilityResults':
            X_info_inner = get_data(data.get('tweet'))
            X_info['x_info_inner'] = X_info_inner
        if 'legacy' in data:
            # 判断是否为引用帖子
            if data.get('legacy').get('is_quote_status'):
                quoted_status = data.get('legacy').get('quoted_status_result')
                if quoted_status:
                    quote_result = get_data(quoted_status.get('result'))
                    X_info['quote_result'] = quote_result
            # 判断是否为转推
            if data.get('legacy').get('retweeted_status_result'):
                result_inner = data.get('legacy').get('retweeted_status_result').get('result')
                if result_inner.get('__typename') == 'Tweet':
                    X_info_inner = get_data(result_inner)
                    X_info['x_info_inner'] = X_info_inner
    # 记录时间大于采集到的时间则停止采集
    if X_info['create_time'] < stop_time:
        X_info = None
    return X_info

def get_data(data):
    # 获取用户信息
    core = data.get('core')
    # 获取core为None
    if core == None:
        core = data.get('tweet').get('core')
        data = data.get('tweet')

    user_result_legacy = core.get('user_results').get('result').get('legacy')

    # 用户id
    user_id = core.get('user_results').get('result').get('rest_id')
    # 用户名字
    name = user_result_legacy.get('name')
    # 用户名
    screen_name = user_result_legacy.get('screen_name')
    # 用户头像链接
    header = user_result_legacy.get('profile_image_url_https')
    # 获取帖子数据
    legacy = data.get('legacy')
    # 发帖时间
    create_time = format_time(legacy.get('created_at'))
    # 帖子链接
    X_link = 'https://x.com/' + screen_name + '/status/' + legacy.get('id_str')
    # 获取帖子全文
    X_full_text = legacy.get('full_text')
    # 帖子图片及视频
    photo_list = []
    video_list = []
    extended_entities = legacy.get('extended_entities', '')
    if extended_entities != '':
        medias = extended_entities.get('media', '')
        if medias != '':
            for media in medias:
                if media['type'] == 'photo':
                    media_url = media["media_url_https"]
                    photo_list.append(media_url)
                elif media['type'] == 'video':
                    quote_bitrate = 0
                    url_str = ''
                    video_info = media['video_info']
                    video_urls = video_info['variants']
                    for url in video_urls:
                        if url['content_type'] == 'video/mp4':
                            if quote_bitrate == 0:
                                quote_bitrate = url['bitrate']
                                url_str = url['url']
                            elif quote_bitrate > url['bitrate']:
                                quote_bitrate = url['bitrate']
                                url_str = url['url']
                    video_list.append(url_str)

    return {
        'user_id_str' :      user_id,
        'name' :             name,
        'user_name' :        screen_name,
        'header_link' :      header,
        'create_time' :      create_time,
        'X_full_text' :  X_full_text,
        'X_link' :       X_link,
        'photo_list' :       photo_list,
        'video_list' :       video_list
    }
    



def format_time(utc_times):
    timeArray = time.strptime(utc_times, '%a %b %d %H:%M:%S +0000 %Y')
    utc_timestamp = time.mktime(timeArray)
    local_timestamp = utc_timestamp + 8*60*60
    local_tuptime = time.localtime(local_timestamp)
    local_time = time.strftime('%Y-%m-%d %H:%M:%S', local_tuptime)
    return local_time
