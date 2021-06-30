# -*- coding: utf-8 -*-
# @Time     : 2021/6/30 15:55
# @Author   : ruochen
# @Email    : wangrui@ruochen.email
# @File     : CSDN.py
# @Project  : Project

import requests
import json
import os
import base64
import hashlib
import hmac
import time
import urllib.parse

# ==============  1.CSDN 个人信息 ============== #
CSDN_ID = os.environ['CSDN_ID']  # 必填！用户ID
COOKIE = os.environ['COOKIE']  # 必填！用户COOKIE

# ==============  2.功能开关配置项 ============== #
# 填 on 则开启，开启的同时也需要配置3中的选项，不填或填其他则关闭
IF_LUCK_DRAW = os.environ['IF_LUCK_DRAW']  # 选填！是否开启抽奖
IF_SERVER = os.environ['IF_SERVER']  # 选填！是否开启 server 酱通知
IF_WECHAT = os.environ['IF_WECHAT']  # 选填！是否开启企业微信通知
IF_DING = os.environ['IF_DING']  # 选填！是否开启钉钉通知

# ==============  3.消息通知配置项 ============== #
SERVER_SCKEY = os.environ['SERVER_SCKEY']  # 选填！server 酱的 SCKEY
WECHAT_URL = os.environ['WECHAT_URL']  # 选填！企业微信机器人 url
DING_URL = os.environ['DING_URL']  # 选填！钉钉机器人 url
DING_SECRET = os.environ['DING_SECRET']  # 选填！钉钉机器人加签 secret

# ==============  4.准备发送的消息 ============== #
TEXT = ''  # 消息标题
DESP = ''  # 消息内容


class CSDN:
    # -> None 表示返回类型为None
    def __init__(self) -> None:
        # 第二个参数代表分割成两个
        self.UUID = COOKIE.split(';', 1)[0].split('=', 1)[1]
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        # 签到路径
        self.SIGN_IN_URL = 'https://me.csdn.net/api/LuckyDraw_v2/signIn'
        # 抽奖路径
        self.LUCKY_DRAW_URL = 'https://me.csdn.net/api/LuckyDraw_v2/goodLuck'
        # 可抽奖次数
        self.DRAW_TIMES = 0
        self.HEADERS = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-length': '243',
            'content-type': 'application/json;charset=UTF-8',
            'cookie': COOKIE,
            'origin': 'https://i.csdn.net',
            'referer': 'https://i.csdn.net/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.USER_AGENT
        }
        self.DATA = {
            'ip': '',
            'platform': 'pc-my',
            'product': 'pc',
            'user_agent': self.USER_AGENT,
            'username': CSDN_ID,
            'uuid': self.UUID
        }

    def csdn_sign_in(self) -> None:
        global TEXT, DESP
        response = requests.post(url=self.SIGN_IN_URL, headers=self.HEADERS, data=self.DATA)
        result = json.loads(response.text)

        if result['code'] == 200:
            if not result['data']['isSigned'] and result['data']['signed']:
                keep_count = result['data']['keepCount']  # 连续签到天数
                total_count = result['data']['totalCount']  # 累计签到天数
                total_signed_count = result['data']['totalSignedCount']  # 当前签到人数
                self.DRAW_TIMES = result['data']['drawTimes']
                TEXT = 'CSDN 签到成功！'
                DESP = 'CSDN 签到成功！你已连续签到 {} 天，累计签到 {} 天，当前已有 {} 人签到。'.format(keep_count, total_count,
                                                                             total_signed_count)
                print('签到成功！你已连续签到 {} 天，累计签到 {} 天，当前已有 {} 人签到。'.format(keep_count, total_count, total_signed_count))
            elif result['data']['isSigned']:
                TEXT = 'CSDN 签到失败！'
                DESP = 'CSDN 签到失败！你今天已经签到过了！'
                print('你今天已经签到过了！')
            else:
                TEXT = 'CSDN 签到失败！'
                print('签到失败！')
        elif result['code'] == 400102:
            TEXT = 'CSDN 签到失败！'
            DESP = 'CSDN 签到失败！{} 用户不存在或者 cookie 错误！'.format(CSDN_ID)
            print('签到失败！{} 用户不存在或者 cookie 错误！'.format(CSDN_ID))
        else:
            TEXT = 'CSDN 签到失败！'
            print('签到失败！')

    def csdn_luck_draw(self) -> None:
        global TEXT, DESP
        if self.DRAW_TIMES != 0:
            response = requests.post(url=self.LUCKY_DRAW_URL, headers=self.HEADERS, data=self.DATA)
            result = json.loads(response.text)
            if result['code'] == 200:
                if result['data']['can_draw']:
                    prize_title = result['data']['prize_title']
                    TEXT += 'CSDN 抽奖成功！'
                    DESP += 'CSDN 抽奖成功！恭喜你获得{}！'.format(prize_title)
                    print('抽奖成功！恭喜你获得{}！'.format(prize_title))
                elif not result['data']['can_draw']:
                    TEXT += 'CSDN 抽奖失败！'
                    DESP += 'CSDN 抽奖失败！抽奖机会已用完！'
                    print('抽奖机会已用完！')
                else:
                    TEXT += 'CSDN 抽奖失败！'
                    print('抽奖失败！')
            elif result['code'] == 400102:
                TEXT += 'CSDN 抽奖失败！'
                DESP += 'CSDN 抽奖失败！{} 用户不存在或者 cookie 错误！'.format(CSDN_ID)
                print('抽奖失败！{} 用户不存在或者 cookie 错误！'.format(CSDN_ID))
            else:
                TEXT += 'CSDN 抽奖失败！'
                print('抽奖失败！')
        else:
            TEXT += 'CSDN 抽奖失败！抽奖机会已用完！'
            print('抽奖机会已用完')


class Notice:
    @staticmethod
    def server():
        requests.get('https://sc.ftqq.com/{}.send?text={}&desp={}'.format(SERVER_SCKEY, TEXT, DESP))

    @staticmethod
    def wechat():
        data = {
            'msgtype': 'text',
            'text': {
                'content': DESP
            }
        }
        headers = {'content-type': 'application/json'}
        requests.post(url=WECHAT_URL, headers=headers, data=json.dumps(data))

    @staticmethod
    def ding():
        timestamp = str(round(time.time()) * 1000)
        secret = DING_SECRET
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        headers = {'Content-Type': 'application/json'}
        complete_url = DING_URL + '&timestamp=' + timestamp + "&sign=" + sign
        data = {
            'text': {
                'content': DESP
            },
            'msgtype': 'text'
        }
        requests.post(url=complete_url, headers=headers, data=data)

def run():
    c = CSDN()
    n = Notice()
    c.csdn_sign_in()

    if IF_LUCK_DRAW == 'on':
        n.server()
    if IF_SERVER == 'on':
        n.server()
    if IF_WECHAT == 'on':
        n.wechat()
    if IF_DING == 'on':
        n.ding()

if __name__ == '__main__':
    run()
