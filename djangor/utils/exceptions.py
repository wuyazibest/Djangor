#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : exceptions.py
# @Time    : 2020/1/1 18:25
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from django.http import JsonResponse, Http404
from redis import RedisError
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler, set_rollback

from djangor.utils import logger, json_resp
from djangor.utils.response_code import RET


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        view = context['view']
        if isinstance(exc, (DatabaseError, RedisError)):
            # 数据库异常
            set_rollback()
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部错误'}, status=RET.DBERR)
    
    return response


def my_exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    
    if isinstance(exc, exceptions.APIException):
        set_rollback()
    
    # 自定义错误捕获和返回的结果，将返回结果变成自定义格式
    if isinstance(exc, exceptions.ValidationError):
        return json_resp(RET.PARAMERR, f"参数错误 error: {exc}")
    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.PermissionDenied, exceptions.NotAuthenticated)):
        return json_resp(RET.PARAMERR, f"用户身份认证失败 error: {exc}")
    
    if isinstance(exc, Exception):
        view = context['view']
        logger.error(f"接口请求错误 {view} {type(exc)} error: {exc}")
        return json_resp(RET.SERVERERR, f"服务器内部错误 error: {exc}")
    
    return None
