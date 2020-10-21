#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : comment.py
# @Time    : 2020/9/4 21:54
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import json
import logging

import datetime
import redis
import requests
import time

from django.http import JsonResponse
from jsonschema import validate
from retrying import retry

from djangor import config
from djangor.utils.response_code import RET, error_map

logger = logging.getLogger('django')


def json_resp(code, message, **kwargs):
    kwargs["code"] = code
    kwargs["message"] = message or error_map.get(code, "未知消息")
    return JsonResponse(kwargs)


class PlusException(Exception):
    def __init__(self, *args, code=RET.PARAMERR, status=None, **kwargs):
        super(PlusException, self).__init__(*args)
        self.code = code
        self.status = status
        for k, v in kwargs.items():
            setattr(self, k, v)


class Redis(object):
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True, long=False, **kwargs):
        self.__kw = dict(host=host, port=port, db=db, decode_responses=decode_responses, **kwargs)
        self.long = long
        if self.long:
            connection_pool = redis.ConnectionPool(**self.__kw)
            self.__long_conn = redis.Redis(connection_pool=connection_pool)
    
    @property
    def __conn(self):
        if self.long:
            return self.__long_conn
        return redis.Redis(**self.__kw)
    
    def __getattr__(self, item):
        def _(*args, **kwargs):
            try:
                return getattr(self.__conn, item)(*args, **kwargs)
            except Exception as e:
                logger.error(f"redis操作失败 {e}")
        
        return _


redis_store = Redis(host=config.RedisConf.host, port=config.RedisConf.port, db=config.RedisConf.db2, long=True)  # type: redis.Redis


def redis_conn(db=None) -> redis.Redis:
    return Redis(host=config.RedisConf.host, port=config.RedisConf.port, db=db or config.RedisConf.db1)


class Pager(object):
    def __init__(self, object_list, limit):
        self.object_list = object_list
        self.limit = int(limit)
        self.total = len(self.object_list)
    
    def page(self, offset):
        try:
            if not (isinstance(offset, int) or offset.isdecimail()):
                offset = 1
            else:
                offset = int(offset)
            
            bottom = (offset - 1) * self.limit
            top = bottom + self.limit
            if not self.total:
                return []
            if bottom < 0:
                ret = self.object_list[0:self.limit]
            else:
                ret = self.object_list[bottom:top]
        except Exception as e:
            logger.error(f"分页查询出错 error: {e} {self.object_list[0]}")
            ret = self.object_list[0:self.limit]
        
        return ret


@retry(stop_max_attempt_number=2)
def _parse_url(method, url, **kwargs):
    if method.upper() in ["GET"]:
        kwargs.setdefault('allow_redirects', default=True)
    tt = time.time()
    resp = requests.request(method, url, timeout=10, **kwargs)
    logger.debug(f">>>> time:{(time.time()-tt):.3f} url: {method} {resp.url}")
    if resp.status_code != 200:
        raise Exception(resp.content.decode())
    print(f"========= \n {json.dumps(kwargs,ensure_ascii=False)} \n {resp.content.decode()} \n ===============")
    return resp.json()


def parse_url(url, params=None, data=None, json=None, headers=None, method="GET", raise_exception=False):
    try:
        resp_json = _parse_url(method, url, params=params, data=data, json=json, headers=headers)
    except Exception as e:
        msg = f"地址请求失败 {method} {url} kwargs:{params or data or json} error:{e}"
        logger.error(msg)
        resp_json = {}
        if raise_exception:
            raise Exception(msg)
    return resp_json


def get_request_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        request_ip = x_forwarded_for.split(",")[0]
    else:
        request_ip = request.META.get("REMOTE_ADDR")
    return request_ip


def check_json(instance, schema):
    try:
        validate(instance, schema, types=dict(array=(list, tuple)))
        return True
    except Exception as e:
        logger.error(f"json数据校验失败:{instance}   error: %s" % e)
        return False


def check_datetime_fmt(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.datetime.strptime(date_str, fmt)
    except:
        return False
