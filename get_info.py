import requests
import json
import time


class BoxOffice(object):
    def __init__(self, url):
        self.url = url

    def get_msg(self):
        r = requests.get(self.url)
        msg_dir = json.loads(r.text)
        data = msg_dir['data']
        msg = ''
        msg += '实时电影票房排名前十名：\r\n'
        for info in data[:-1]:
            information = "第%(Irank)s名，《%(MovieName)s》，实时票房：%(BoxOffice)s万，" \
                          "累计票房：%(sumBoxOffice)s万，已上映%(movieDay)s天，票房占比：" \
                          "%(boxPer)s%%" % {'Irank': info['Irank'], 'MovieName': info['MovieName'],
                                          'BoxOffice': info['BoxOffice'], 'sumBoxOffice': info['sumBoxOffice'],
                                          'movieDay': info['movieDay'], 'boxPer': info['boxPer']}
            msg += information + '\r\n'

        times = msg_dir['data'][0]['time']
        timeStruct = time.strptime(times, "%Y-%m-%d %H:%M:%S")
        times = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
        msg += '数据获取时间：%s，由Robot_zq自动发送' % times

        return msg


class TodayVideo(object):
    def __init__(self, url):
        self.url = url

    def get_msg(self):
        r = requests.get(self.url)
        msg_dir = json.loads(r.text)
        results = msg_dir['result']
        # 带视频的信息列表
        need_info_list = []
        for result in results:
            if result['type'] == 'followCard':
                video_info = {}
                data = result['data']['content']['data']
                video_info['description'] = data['description']
                video_info['title'] = data['title']
                video_info['playUrl'] = data['playUrl']
                need_info_list.append(video_info)

        return need_info_list

    def download_video(self):
        info_list = self.get_msg()
        headers = {
            'Host': 'baobab.kaiyanapp.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36'
        }
        for info in info_list:
            play_url = info['playUrl']
            name = info['title']
            print('开始下载《{}》...'.format(name))
            result = requests.Session()
            r = result.get(play_url, headers=headers, allow_redirects=False)
            video_url = r.headers['Location']
            v = requests.get(video_url, stream=True)
            with open('video_dir/{}.mp4'.format(name) , "wb") as mp4:
                for chunk in v.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        mp4.write(chunk)
            print('《{}》下载完成！'.format(name))
            print('===========================================')


def get_box_office():
    bo = BoxOffice('https://api.shenjian.io/?appid=1de107add5b59023ba21ac594d1b46a2')
    bo.get_msg()
    print(bo.get_msg())


def get_today_video():
    tv = TodayVideo('https://api.apiopen.top/todayVideo')
    # tv.get_msg()
    # print(tv.get_msg())
    tv.download_video()


if __name__ == '__main__':
    # get_box_office()
    get_today_video()
