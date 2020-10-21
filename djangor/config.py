#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : config.py
# @Time    : 2020/9/4 21:54
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import configparser
import os

config_name = "development"
filename = {
    "development": "conf/conf_development.ini",
    "preparation": "conf/conf_preparation.ini",
    "production": "conf/conf_production.ini",
    }
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CONFIG = configparser.ConfigParser()
_CONFIG.read(os.path.join(BASE_DIR, filename[config_name]), encoding="utf-8")

DEBUG = _CONFIG.getboolean("default", "debug")

DEFAULT_REQUEST_TIMEOUT = _CONFIG.getint("default", "request_timeout")
DEFAULT_REQUEST_RETRY = _CONFIG.getint("default", "request_retry")
THREAD_NUMBER = _CONFIG.getint("default", "thread_number")
MAX_RETRY_TIMES = _CONFIG.getint("default", "max_retry_times")
WAIT_TIME = _CONFIG.getint("default", "wait_time")


class MysqlConf:
    host = _CONFIG.get("database", "host")
    port = _CONFIG.getint("database", "port")
    user = _CONFIG.get("database", "user")
    password = _CONFIG.get("database", "password")
    db = _CONFIG.get("database", "db")
    charset = _CONFIG.get("database", "charset")
    maxconnections = _CONFIG.getint("database", "maxconnections")
    echo = _CONFIG.getboolean("database", "echo")
    pool_recycle = _CONFIG.getint("database", "pool_recycle")
    pool_size = _CONFIG.getint("database", "pool_size")


class RedisConf:
    host = _CONFIG.get("redis", "host")
    port = _CONFIG.getint("redis", "port")
    db1 = _CONFIG.getint("redis", "db1")
    db2 = _CONFIG.getint("redis", "db2")
    expires = _CONFIG.getint("redis", "expires")
