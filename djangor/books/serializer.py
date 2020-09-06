#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : serializer.py
# @Time    : 2020/9/5 23:12
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import json

from .models import *
from djangor.utils import BaseSerializer, ChoiceField, redis_store


class BookSerializer(BaseSerializer):
    publishing = ChoiceField(choices=BookModel.PUBLISHING_CHOICE)
    
    class Meta:
        model = BookModel
        exclude = ["is_deleted"]
    
    def to_representation(self, instance):
        """Convert `username` to lowercase."""
        ret = super().to_representation(instance)
        ret["kind_display"] = {x[0]: x[1] for x in BookKind.choices}.get(instance.kind)
        return ret


class LabelSerializer(BaseSerializer):
    class Meta:
        model = LabelModel
        fields = "__all__"
    
    @classmethod
    def get_map(cls):
        key = "book_label_map"
        data_map = redis_store.get(key)
        if data_map:
            data_map = json.loads(data_map)
        else:
            data_list = cls(instance=cls.Meta.model.get_active().all(), many=True).data
            data_map = {x["id"]: x for x in data_list}
            redis_store.set(key, json.dumps(data_map), ex=60 * 60 * 24 * 7)
        return data_map
    
    def save(self, **kwargs):
        redis_store.delete("book_label_map")
        return super(LabelSerializer, self).save(**kwargs)


class BookBeLabelSerializer(BaseSerializer):
    class Meta:
        model = BookBeLabelModel
        exclude = []
    
    @classmethod
    def get_label(cls, book_id):
        data_list = cls(instance=cls.Meta.model.objects.filter(book_id=book_id).all(), many=True).data
        return [LabelSerializer.get_map()[x["label_id"]] for x in data_list]
    
    @classmethod
    def get_book(cls, label_id):
        data_list = cls(instance=cls.Meta.model.objects.filter(label_id=label_id).all(), many=True).data
        book_id_list = [x["book_id"] for x in data_list]
        return BookSerializer(instance=BookModel.objects.filter(id__in=book_id_list, is_deleted=0).all(),
                              many=True).data
