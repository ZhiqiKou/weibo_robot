# _*_ coding: utf-8 _*_

"""
python_weibo.py by xianhu
"""

import re
import rsa
import time
import json
import base64
import logging
import binascii
import urllib.parse
from weibo_robot.ruokuai import *
from weibo_robot.config import WEIBO_USERNAME, WEIBO_PASSWORD, RUOKUAI_USERNAME, RUOKUAI_PASSWORD, IS_AUTOMATIC_CODE


class WeiBoRobot(object):
    """
    class of WeiBoLogin, to login weibo.com
    """

    def __init__(self):
        """
        constructor
        """
        self.user_name = None
        self.pass_word = None
        self.user_uniqueid = None
        self.user_nick = None

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"})
        self.session.get("http://weibo.com/login.php")
        return

    def login(self, user_name, pass_word):
        """
        login weibo.com, return True or False
        """
        self.user_name = user_name
        self.pass_word = pass_word
        self.user_uniqueid = None
        self.user_nick = None

        # get json data
        s_user_name = self.get_username()
        json_data = self.get_json_data(su_value=s_user_name)
        if not json_data:
            return False
        s_pass_word = self.get_password(json_data["servertime"], json_data["nonce"], json_data["pubkey"])

        # make post_data
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "userticket": "1",
            "vsnf": "1",
            "service": "miniblog",
            "encoding": "UTF-8",
            "pwencode": "rsa2",
            "sr": "1280*800",
            "prelt": "529",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "rsakv": json_data["rsakv"],
            "servertime": json_data["servertime"],
            "nonce": json_data["nonce"],
            "su": s_user_name,
            "sp": s_pass_word,
            "returntype": "TEXT",
        }

        # get captcha code
        if json_data["showpin"] == 1:
            url = "http://login.sina.com.cn/cgi/pin.php?r=%d&s=0&p=%s" % (int(time.time()), json_data["pcid"])

            if IS_AUTOMATIC_CODE:
                rc = RClient(RUOKUAI_USERNAME, RUOKUAI_PASSWORD, '125314', 'ae2d42b0653e4f57969ec0b27e5d4c69')
                im = self.session.get(url).content
                code = rc.rk_create(im, 3050)['Result']
            else:
                with open("captcha.jpeg", "wb") as file_out:
                    file_out.write(self.session.get(url).content)
                code = input("请输入验证码:")
            post_data["pcid"] = json_data["pcid"]
            post_data["door"] = code

        # login weibo.com
        login_url_1 = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=%d" % int(time.time())
        json_data_1 = self.session.post(login_url_1, data=post_data).json()
        if json_data_1["retcode"] == "0":
            params = {
                "callback": "sinaSSOController.callbackLoginStatus",
                "client": "ssologin.js(v1.4.18)",
                "ticket": json_data_1["ticket"],
                "ssosavestate": int(time.time()),
                "_": int(time.time()*1000),
            }
            response = self.session.get("https://passport.weibo.com/wbsso/login", params=params)
            json_data_2 = json.loads(re.search(r"\((?P<result>.*)\)", response.text).group("result"))
            if json_data_2["result"] is True:
                self.user_uniqueid = json_data_2["userinfo"]["uniqueid"]
                self.user_nick = json_data_2["userinfo"]["displayname"]
                logging.warning("WeiBoLogin succeed: %s", json_data_2)
            else:
                logging.warning("WeiBoLogin failed: %s", json_data_2)
        else:
            logging.warning("WeiBoLogin failed: %s", json_data_1)
        return True if self.user_uniqueid and self.user_nick else False

    def send_msg(self, msg):
        data = {
            'location': 'v6_content_home',
            'text': msg,
            'appkey': '',
            'style_type': '1',
            'pic_id': '',
            'tid': '',
            'pdetail': '',
            'mid': '',
            'isReEdit': 'false',
            'rank': '0',
            'rankid': '',
            'module': 'stissue',
            'pub_source': 'main_',
            'pub_type': 'dialog',
            'isPri': '0',
            '_t': '0',
        }
        self.session.headers["Referer"] = 'https://weibo.com/u/%s/home?topnav=1&wvr=6' % self.user_uniqueid
        times = int(time.time() * 1000)
        self.session.post(url='https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=' + str(times),
                          data=data)

    def get_username(self):
        """
        get legal username
        """
        username_quote = urllib.parse.quote_plus(self.user_name)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    def get_json_data(self, su_value):
        """
        get the value of "servertime", "nonce", "pubkey", "rsakv" and "showpin", etc
        """
        params = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.18)",
            "su": su_value,
            "_": int(time.time()*1000),
        }
        try:
            response = self.session.get("http://login.sina.com.cn/sso/prelogin.php", params=params)
            json_data = json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except Exception as excep:
            json_data = {}
            logging.error("WeiBoLogin get_json_data error: %s", excep)

        logging.debug("WeiBoLogin get_json_data: %s", json_data)
        return json_data

    def get_password(self, servertime, nonce, pubkey):
        """
        get legal password
        """
        string = (str(servertime) + "\t" + str(nonce) + "\n" + str(self.pass_word)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
        password = rsa.encrypt(string, public_key)
        password = binascii.b2a_hex(password)
        return password.decode()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")
    weibo = WeiBoRobot()
    is_logined = weibo.login(WEIBO_USERNAME, WEIBO_PASSWORD)

    def send(is_logined):
        if is_logined:
            weibo.send_msg('test')
        else:
            is_logined = weibo.login(WEIBO_USERNAME, WEIBO_PASSWORD)
            send(is_logined)

    send(is_logined)

