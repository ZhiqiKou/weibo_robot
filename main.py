from python_weibo import WeiBoRobot
from get_info import BoxOffice
import config
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")
weibo = WeiBoRobot()
is_logined = weibo.login(config.WEIBO_USERNAME, config.WEIBO_PASSWORD)
bo = BoxOffice('https://api.shenjian.io/?appid=1de107add5b59023ba21ac594d1b46a2')
bo_msg = bo.get_msg()

def send(is_logined):
    if is_logined:
        weibo.send_msg(bo_msg)
    else:
        is_logined = weibo.login(config.WEIBO_USERNAME, config.WEIBO_PASSWORD)
        send(is_logined)
send(is_logined)