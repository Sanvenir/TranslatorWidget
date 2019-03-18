# -*- coding: utf-8 -*-
import hashlib
import time
import uuid

import requests

YOUDAO_URL = 'http://openapi.youdao.com/api'


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(config, query="Hello world!"):
    app_key = config.APP_KEY
    app_secret = config.APP_SECRET
    if not app_key or not app_secret:
        return None
    data = {'from': 'EN', 'to': 'zh-CHS', 'signType': 'v3'}
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = app_key + truncate(query) + salt + curtime + app_secret
    sign = encrypt(signStr)
    data['appKey'] = app_key
    data['q'] = query
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    return response.content


