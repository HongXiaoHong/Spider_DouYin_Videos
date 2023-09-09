import datetime
import random
import re
import time
import urllib.parse

import execjs


def sleep_random(sleep_time: int = None):
    """
    睡眠时间
    :param sleep_time:
    :return:
    """
    if sleep_time is None:
        time.sleep(random.randint(1, 5))
    else:
        time.sleep(sleep_time)


def get_current_time_format(format_info: str = None):
    """
    获取当前的时间的格式化 [ex: 2023-02-25 11:22:11]
    :param format_info:
    :return:
    """
    if format_info is None:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.now().strftime(format_info)


def generate_url_with_xbs(url, user_agent):
    """
    生成x_bogus
    :param url:
    :param user_agent:
    :return:
    """
    query = urllib.parse.urlparse(url).query
    x_bogus = execjs.compile(open('tools/X-Bogus.js').read()).call('sign', query, user_agent)
    return x_bogus


def fix_video_desc(desc):
    """
    OSError: [Errno 22] Invalid argument: 'D:/download/douyin/MS4wLjABAAAAi2oukRVcHpgD-HbVdzsxE7tYykr91YuIKukR_X_Yy08EFWRQhRrECDF6FvbvT8Xa/技术的尽头是魔术\n#JavaScript #前端开发工程师   #编程  #程序员 #web前端  #前端.mp4'
    文件名称 fix 为 windows 系统可以接受的字符
    :param desc: 文件描述, 带有各种特殊字符
    :return: 截取正常的字符作为文件描述名字
    """
    index = len(desc)
    search = re.search(r"[\n|#]", desc)
    if search:
        index = search.start()
    return desc[0:index]


def fix_title_video_publish_time(publish_time):
    """
    上传时间截取, 只要年月日
    :param publish_time: 视频上传时间 年-月-日 时:分:秒
    :return: 时间: 年-月-日
    """
    return publish_time[0:10]
