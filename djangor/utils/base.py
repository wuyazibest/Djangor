#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : base.py
# @Time    : 2020/9/4 21:54
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import datetime
from django.db import models
from rest_framework import serializers, viewsets

from rest_framework.decorators import action

from djangor.utils import logger, json_resp, RET, Pager, PlusException


# ================================================================
# model

class BooleanField(models.BooleanField):
    TRUE_VALUES = {
        "t", "T",
        "y", "Y", "yes", "YES",
        "true", "True", "TRUE",
        "on", "On", "ON",
        "1", 1,
        True
        }
    FALSE_VALUES = {
        "f", "F",
        "n", "N", "no", "NO",
        "false", "False", "FALSE",
        "off", "Off", "OFF",
        "0", 0, 0.0,
        False
        }
    NULL_VALUES = {"null", "Null", "NULL", "", None}
    
    def to_python(self, value):
        if value in self.TRUE_VALUES:
            return True
        if value in self.FALSE_VALUES:
            return False
        if value in self.NULL_VALUES:
            return None
        if str(value).isdecimal() and int(value) > 0:
            return True
        return super(BooleanField, self).to_python(value)


class ChoiceMixin:
    """
    有点：对于视图层透明，使用obj.field得到的是choice转换后的值
    缺点：无法使用serializer的校验，无法自动检验choice选项值
    """
    
    def __init__(self, choices_dict, *args, **kwargs):
        self.choices_dict = choices_dict
        super().__init__(*args, **kwargs)
    
    def get_prep_value(self, value):
        """将python数据加工后存入到db
        """
        if value is None:
            return None
        value = [k for k, v in self.choices_dict.items() if v == value][0]
        return super().get_prep_value(value)
    
    def from_db_value(self, value, expression, connection):
        """从数据库取出数据加工后吐出
        """
        return self.choices_dict.get(value) or value
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["choices_dict"] = self.choices_dict
        return name, path, args, kwargs


class IntChoiceField(ChoiceMixin, models.IntegerField): pass


class StrChoiceField(ChoiceMixin, models.CharField): pass


class BaseModel(models.Model):
    # id = models.IntegerField(primary_key=True, verbose_name="自增id")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    user = models.CharField(max_length=191, blank=True, verbose_name="创建人/修改人")
    
    class Meta:
        abstract = True
    
    @classmethod
    def data_bulk_create(cls, data_list, batch_size=500):
        if data_list:
            obj_list = [cls(**x) for x in data_list]
            cls.objects.bulk_create(obj_list, batch_size=batch_size)
    
    @classmethod
    def data_bulk_update(cls, data_list, fields, batch_size=500):
        if data_list:
            if "update_time" not in fields:
                fields.append("update_time")
            
            update_time = datetime.datetime.now()
            obj_list = [cls(**dict(x, **{"update_time": update_time})) for x in data_list]
            cls.objects.bulk_update(obj_list, fields, batch_size=batch_size)


class RichBaseModel(BaseModel):
    comment = models.CharField(max_length=191, blank=True, verbose_name="备注")
    is_used = BooleanField(default=False, verbose_name="使用标识")
    is_deleted = models.IntegerField(default=0, verbose_name="删除标识")
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_deleted=0)


# ================================================================
# serializer

class ChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if data == "" and self.allow_blank:
            return ""
        
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)
    
    def to_representation(self, value):
        return self._choices[value]


class BaseSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)


# ================================================================
# view

class BaseView(viewsets.GenericViewSet):
    resources = ""
    query_field = ()
    create_field = ()
    update_field = ()
    create_required_field = ()
    update_required_field = ("id",)
    
    @action(methods=["GET"], detail=False, url_path="get_query")
    def get_query(self, request, *args, **kwargs):
        try:
            logger.info(f"{self.resources}查询 user:{request.user.username} params:{request.query_params}")
            params = {x: request.query_params.get(x) for x in self.query_field if request.query_params.get(x, "") != ""}
            
            instance = self.queryset.filter(**params).all()
            offset = request.query_params.get("offset")
            limit = request.query_params.get("limit")
            if offset and limit:
                pag = Pager(instance, limit)
                instance = pag.page(offset)
                total = pag.total
            else:
                instance = instance
                total = len(instance)
            serializer = self.get_serializer(instance, many=True)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=serializer.data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{request.query_params} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    @action(methods=["POST"], detail=False, url_path="post_query")
    def post_query(self, request, *args, **kwargs):
        try:
            logger.info(f"{self.resources}查询 user:{request.user.username} params:{request.data}")
            params = {x: request.data.get(x) for x in self.query_field if request.data.get(x, "") != ""}
            
            instance = self.queryset.filter(**params).all()
            offset = request.data.get("offset")
            limit = request.data.get("limit")
            if offset and limit:
                pag = Pager(instance, limit)
                instance = pag.page(offset)
                total = pag.total
            else:
                instance = instance
                total = len(instance)
            serializer = self.get_serializer(instance, many=True)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=serializer.data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    @action(methods=["POST"], detail=False, url_path="create")
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"{self.resources}创建 user:{request.user.username} params:{request.data}")
            params = {x: request.data.get(x) for x in self.create_field if request.data.get(x) is not None}
            
            if not all([x in params for x in self.create_required_field]):
                raise PlusException(f"缺少必填参数")
            
            params["user"] = request.user.username
            serializer = self.get_serializer(data=params)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return json_resp(RET.OK, f"{self.resources}创建成功", data=serializer.data)
        except Exception as e:
            logger.error(f"{self.resources}创建错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}创建错误 error:{e}", data=None)
    
    def update_queryset(self):
        return self.queryset
    
    @action(methods=["PUT"], detail=False, url_path="update")
    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"{self.resources}更新 user:{request.user.username} params:{request.data}")
            params = {x: request.data.get(x) for x in self.update_field if request.data.get(x) is not None}
            
            if not all([x in params for x in self.update_required_field]):
                raise PlusException("缺少必填参数")
            pk = params.pop("id")
            
            instance = self.update_queryset().get(pk=pk)
            params["user"] = request.user.username
            serializer = self.get_serializer(instance=instance, data=params, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return json_resp(RET.OK, f"{self.resources}更新成功", data=serializer.data)
        except Exception as e:
            logger.error(f"{self.resources}更新错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}更新错误 error:{e}", data=None)
    
    def delete_queryset(self):
        return self.queryset
    
    @action(methods=["DELETE"], detail=False, url_path="delete")
    def delete(self, request, *args, **kwargs):
        try:
            logger.info(f"{self.resources}删除 user:{request.user.username} params:{request.data}")
            
            pk = request.data.get("id")
            is_deleted = request.data.get("is_deleted", True)
            if pk is None:
                raise PlusException("缺少id参数")
            
            instance = self.delete_queryset().get(pk=pk)
            instance.is_deleted = pk if is_deleted else 0
            instance.user = request.user.username
            instance.save()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=pk)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)
    
    @action(methods=["DELETE"], detail=False, url_path="abs_delete")
    def abs_delete(self, request, *args, **kwargs):
        try:
            logger.info(f"{self.resources}删除 user:{request.user.username} params:{request.data}")
            
            pk = request.data.get("id")
            if pk is None:
                raise PlusException("缺少id参数")
            
            instance = self.delete_queryset().get(pk=pk)
            instance.delete()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=pk)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)
