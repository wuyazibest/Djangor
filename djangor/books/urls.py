#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : urls.py
# @Time    : 2020/9/5 18:28
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from django.urls import path

from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("book/menu_option/", BookView.as_view({"get": "menu_option"}), name="book"),
    path("book/query_attach_label/", BookView.as_view({"post": "query_attach_label"}), name="book"),
    path("book/", BookView.as_view({
        "get": "get_query",
        "post": "create",
        "put": "update",
        "delete": "delete",
        }), name="book"),
    path("label/query_attach_book/", LabelView.as_view({"post": "query_attach_book"}), name="label"),
    path("label/", LabelView.as_view({
        "get": "get_query",
        "post": "create",
        "put": "update",
        "delete": "delete",
        }), name="label"),
    path("related/", BookBeLabelView.as_view({
        "post": "create",
        "delete": "abs_delete",
        }), name="related"),
    ]
