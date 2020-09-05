#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : auth.py
# @Time    : 2020/9/4 21:55
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from djangor.utils import logger



# ==========================================================================
# permissions 权限验证类型：不验证，登录验证，特殊用户名验证

class SpecialUserPermission(BasePermission):
    """
    登录成功，并且是指定的用户名才能通过认证
    """
    
    def has_permission(self, request, view):
        return bool(request.user and
                    request.user.is_authenticated and
                    request.user.username == 'isme'
                    )


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    get 方法不需要校验，开放访问，其他方法需要校验
    """
    
    def has_permission(self, request, view):
        return bool(
            request.method.upper() in ['GET'] or
            request.user and
            request.user.is_authenticated
            )


# ============================================================================
# authentication 权限验证方式：token有效性校验

class ApiAuthentication(BaseAuthentication):
    """
    用于api接口校验，其他系统调用api接口，校验的因子需要不变的
    """
    www_authenticate_realm = 'api'
    
    def authenticate(self, request):
        # Authorization
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        auth = auth.split()
        if not auth or auth[0].lower() != self.www_authenticate_realm:
            return None
        
        if len(auth) < 3:
            msg = 'Invalid basic header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 3:
            msg = 'Invalid basic header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        
        username, password = auth[1], auth[2]
        return self.authenticate_credentials(username, password)
    
    def authenticate_credentials(self, username, password):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username="api_user", password=password)
            logger.info(f"{self.www_authenticate_realm}认证成功,username：{username}")
        except UserModel.DoesNotExist:
            logger.info(f"{self.www_authenticate_realm}认证失败，username：{username},error: 用户名密码错误")
            raise exceptions.AuthenticationFailed('用户名密码错误')
        except Exception as e:
            logger.info(f"{self.www_authenticate_realm}认证失败，username：{username},error: {e}")
            raise exceptions.AuthenticationFailed(str(e))
        
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid username/password.')
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        
        return (user, None)
    
    def authenticate_header(self, request):
        return 'authentication realm="%s"' % self.www_authenticate_realm


class PublicAuthentication(ApiAuthentication):
    www_authenticate_realm = 'public'
    
    def authenticate_credentials(self, username, password):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username, password=password)
            logger.info(f"{self.www_authenticate_realm}认证成功,username：{username}")
        except UserModel.DoesNotExist:
            logger.info(f"{self.www_authenticate_realm}认证失败，username：{username},error: 用户名密码错误")
            raise exceptions.AuthenticationFailed('用户名密码错误')
        except Exception as e:
            logger.info(f"{self.www_authenticate_realm}认证失败，username：{username},error: {e}")
            raise exceptions.AuthenticationFailed(str(e))
        
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid username/password.')
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        
        return (user, None)


class ThirdPartyAuthentication(BaseAuthentication):
    www_authenticate_realm = 'third'
    
    def authenticate(self, request):
        # Authorization
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth:
            auth = request.COOKIES.get("Authorization", '')
        
        auth = auth.split()
        if not auth or auth[0].lower() != self.www_authenticate_realm:
            return None
        
        if len(auth) < 2:
            msg = 'Invalid basic header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid basic header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        
        token = auth[1]
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token):
        UserModel = get_user_model()
        
        res = third_check_token(token)
        if not res["ok"]:
            raise exceptions.AuthenticationFailed(f'Invalid failed {res["message"]}.')
        
        username = res["data"]["username"]
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(
                username=username,
                is_active=1
                )
        except Exception as e:
            logger.error(f"{self.www_authenticate_realm}认证失败，username：{username},error: {e}")
            raise exceptions.AuthenticationFailed(f"本地用户创建失败 {e}")
        
        user.last_login = datetime.datetime.now()
        user.save()
        
        return (user, token)


# ===================================================================
# 登录后端校验

class ThirdPartyAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username == 'admin':
            return super(ThirdPartyAuthBackend, self).authenticate(request, username=username, password=password,
                                                                   **kwargs)
        res = third_check_user(username, password)
        if not res:
            logger.error(f"第三方认证失败")
            return None
        
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(
                username=username,
                is_active=1
                )
        except Exception as e:
            logger.error("用户查询失败 %s " % e)
            return None
        
        user.last_login = datetime.datetime.now()
        user.save()
        return user


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义登录成功后返回的结果
    :param token:
    :param user:
    :param request:
    :return:
    """
    return {
        "user_id": user.id,
        "username": user.username,
        "token": token,
        }


def third_check_user(username, password):
    """
    模拟第三方校验
    :param username:
    :param password:
    :return:
    """
    if 'u' in username:
        return True
    
    return False


def third_check_token(token):
    """
    模拟第三方校验
    :param username:
    :param password:
    :return:
    """
    if 'u' in token:
        data = {
            "ok": True,
            "message": "校验成功",
            "data": {"user_id": 10086, "username": "user1"}
            }
    else:
        data = {
            "ok": False,
            "message": "校验失败",
            "data": None
            }
    
    return data