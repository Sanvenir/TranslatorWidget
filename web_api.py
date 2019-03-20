# -*- coding: utf-8 -*-
import hashlib
import json
import time
import uuid
from datetime import datetime

import requests

import config_parser
from exceptions import WebException, ConfigException
import locale


class WebRequest:
    def __init__(self, config):
        self.config = config

    def connect(self, query) -> dict or None:
        raise NotImplementedError()


class YouDaoRequest(WebRequest):
    YOUDAO_URL = 'http://openapi.youdao.com/api'
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

    def __init__(self, config):
        super().__init__(config)
        self.start_time = time.mktime(datetime.utcnow().timetuple())
        self.start_web_time = self.get_start_web_time()

    def get_web_time(self):
        return self.start_web_time - self.start_time + time.time()

    @staticmethod
    def get_start_web_time():
        response = requests.post(YouDaoRequest.YOUDAO_URL, headers=YouDaoRequest.HEADERS)
        web_time = response.headers.get("Date")
        if web_time is None:
            raise WebException()
        time_locale = locale.setlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, 'C')
        time_tuple = time.strptime(web_time[5:25], "%d %b %Y %H:%M:%S")
        locale.setlocale(locale.LC_TIME, time_locale)
        return time.mktime(time_tuple)

    @staticmethod
    def encrypt(signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()

    @staticmethod
    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

    @staticmethod
    def do_request(data):
        return requests.post(YouDaoRequest.YOUDAO_URL, data=data, headers=YouDaoRequest.HEADERS)

    def connect(self, query="Hello world!"):
        app_key = self.config.APP_KEY
        app_secret = self.config.APP_SECRET
        if not app_key or not app_secret:
            raise ConfigException()
        data = {'from': 'EN', 'to': 'zh-CHS', 'signType': 'v3'}
        curtime = str(int(self.get_web_time()))
        data['curtime'] = curtime
        salt = str(uuid.uuid1())
        signStr = app_key + self.truncate(query) + salt + curtime + app_secret
        sign = self.encrypt(signStr)
        data['appKey'] = app_key
        data['q'] = query
        data['salt'] = salt
        data['sign'] = sign
        response = self.do_request(data)
        return json.loads(response.content.decode("utf8"))


def test():
    config = config_parser.Configuration()
    req = YouDaoRequest(config)
    result = req.connect()
    print(result)


if __name__ == "__main__":
    test()
