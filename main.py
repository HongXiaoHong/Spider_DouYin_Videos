import json
import os
import time
import urllib.request

import requests

from config import IS_SAVE, SAVE_FOLDER, USER_SEC_UID, IS_WRITE_TO_CSV, LOGIN_COOKIE, CSV_FILE_NAME
from tools.util import get_current_time_format, generate_url_with_xbs, sleep_random, fix_video_desc, \
    fix_title_video_publish_time


class DouYinUtil(object):

    def __init__(self, sec_uid: str):
        """
        :param sec_uid: 抖音id
        """
        self.sec_uid = sec_uid
        self.is_save = IS_SAVE
        self.save_folder = SAVE_FOLDER
        self.is_write_to_csv = IS_WRITE_TO_CSV
        self.csv_name = CSV_FILE_NAME
        self.video_api_url = ''
        self.api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Referer': 'https://www.douyin.com/',
            'Cookie': LOGIN_COOKIE
        }
        self.cursor = 0
        self.videos_list = []  # 视频列表id
        self.video_info_list = []
        self.video_info_dict = {}
        self.stop_flag = False  # 默认不停止

    def get_user_video_info(self, url: str):
        res = requests.get(url, headers=self.api_headers)
        res.encoding = 'utf-8'
        res_text = res.text
        return json.loads(res_text)

    def get_all_videos(self):
        """
        获取所有的视频
        :return:
        """
        while not self.stop_flag:
            self.video_api_url = f'https://www.douyin.com/aweme/v1/web/aweme/post/?aid=6383&sec_user_id={self.sec_uid}&count=35&max_cursor={self.cursor}&cookie_enabled=true&platform=PC&downlink=10'
            xbs = generate_url_with_xbs(self.video_api_url, self.api_headers.get('User-Agent'))
            user_video_url = self.video_api_url + '&X-Bogus=' + xbs
            user_info = self.get_user_video_info(user_video_url)
            aweme_list = user_info['aweme_list']
            for aweme_info in aweme_list:
                self.video_info_list.append(aweme_info)
                self.video_info_dict.setdefault(aweme_info['aweme_id'], aweme_info)
                self.videos_list.append(aweme_info['aweme_id'])
            if int(user_info['has_more']) == 0:
                self.stop_flag = True
            else:
                self.cursor = user_info['max_cursor']
            sleep_random()
        return self.videos_list

    def download_video(self, video_url: str, file_name: str = None):
        """
        下载视频
        :param video_url: 视频地址
        :param file_name: 视频保存文件名: 默认为空
        :return:
        """
        if not self.is_save:
            print("当前不需要保存")
            return
        save_folder = f"{self.save_folder}/{self.sec_uid}"
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        real_file_name = f"{save_folder}/{file_name}"
        print(f"下载url:{video_url}\n保存文件名:{real_file_name}")
        if os.path.exists(real_file_name):
            os.remove(real_file_name)
        urllib.request.urlretrieve(video_url, real_file_name)

    def get_video_detail_info(self, video_id: str):
        """
        获取视频详细信息
        :param video_id: 视频id
        :return:
        """
        default_response = {
            'video_id': video_id,  # 视频id
            'link': 'None',  # 视频链接
            'is_video': True,  # 是否为视频
            'title': 'None',  # 标题
            'thumb_up_num': 0,  # 点赞数
            'comment_num': 0,  # 评论数
            'cover_url': 'http://www.baidu.com',  # 视频封面
            'publish_time': '',  # 发布日期
            'record_time': '记录日期',  # 更新日期
        }
        res_info = self.video_info_dict.get(video_id, None)
        if res_info is None:
            return default_response
        default_response['title'] = res_info['desc']
        create_time = res_info['create_time']
        local_time = time.localtime(create_time)
        local_time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        default_response['publish_time'] = local_time_str
        default_response['record_time'] = get_current_time_format()
        if res_info['images'] is None:
            default_response['link'] = res_info["video"]["play_addr"]["url_list"][0]
            default_response['cover_url'] = res_info["video"]["cover"]["url_list"][0]
            default_response['is_video'] = True
        else:
            default_response['link'] = str(list(map(lambda x: x["url_list"][-1], res_info["images"])))
            default_response['is_video'] = False
        default_response['thumb_up_num'] = res_info['statistics']['admire_count']
        default_response['comment_num'] = res_info['statistics']['comment_count']
        return default_response


if __name__ == '__main__':
    import sys
    params_list_size = len(sys.argv)
    if params_list_size == 2:
        USER_SEC_UID = sys.argv[1]
    elif params_list_size == 3:
        USER_SEC_UID = sys.argv[1]
        SAVE_FOLDER = sys.argv[2]

    dy_util = DouYinUtil(sec_uid=USER_SEC_UID)
    all_video_list = dy_util.get_all_videos()
    for video_id in all_video_list:
        video_info = dy_util.get_video_detail_info(video_id)
        # 文件名使用 上传时间_文件描述
        video_title = video_info["title"]
        publish_time = video_info["publish_time"]
        if video_info['is_video'] is True:
            dy_util.download_video(video_info['link'], f"{fix_title_video_publish_time(publish_time)}_{fix_video_desc(video_title)}.mp4")
