# -*- coding: utf-8 -*-
import json
import uuid
import requests
import hashlib
import time

import config_parser

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


def connect(app_key, app_secret, query="Hello world!"):
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


if __name__ == "__main__":
    config = config_parser.Configuration()
    result = connect(config.APP_KEY, config.APP_SECRET)
    result = json.loads(result, encoding="utf8")
    print(result)
