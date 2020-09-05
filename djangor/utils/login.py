#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : login.py
# @Time    : 2019/12/18 20:52
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from django.contrib.auth.backends import ModelBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_jwt.views import ObtainJSONWebToken

from djangor.utils import logger


class ThirdPartyView(ObtainJSONWebToken, viewsets.GenericViewSet):
    def post(self, request, *args, **kwargs):
        """
        如果要自定义返回的结果，可重写该函数
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return super(ThirdPartyView, self).post(request, *args, **kwargs)
    
    @action(methods=["POST"], detail=False, url_path='logout')
    def logout(self, request, *args, **kwargs):
        pass
