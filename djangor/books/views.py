from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .serializer import *
from djangor.utils import BaseView, logger, Pager, RET, json_resp


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
def index(request):
    logger.info(f"Books app home. user:{request.user.username} params:{request.query_params}")
    return HttpResponse("this is Books app home.")


class BookView(BaseView):
    queryset = BookModel.get_active()
    serializer_class = BookSerializer
    resources = "书籍"
    query_field = (
        "id",
        "name",
        "writer",
        "kind",
        "publishing",
        "publication_date",
        )
    create_field = (
        "name",
        "writer",
        "kind",
        "link",
        "publishing",
        "publication_date",
        )
    update_field = (
        "id",
        "name",
        "writer",
        "kind",
        "link",
        "publishing",
        "publication_date",
        )
    create_required_field = (
        "name",
        "kind",
        "publishing",
        )
    
    def menu_option(self, request, *args, **kwargs):
        data = {
            "kind": {x[0]: x[1] for x in BookKind.choices},
            "publishing": {x[0]: x[1] for x in BookModel.PUBLISHING_CHOICE},
            }
        return json_resp(RET.OK, f"{self.resources}菜单选项查询成功", data=data)
    
    def query_attach_label(self, request, *args, **kwargs):
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
            
            data = []
            for i in serializer.data:
                i["label_info"] = BookBeLabelSerializer.get_label(i["id"])
                data.append(i)
            
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)


class LabelView(BaseView):
    queryset = LabelModel.get_active()
    serializer_class = LabelSerializer
    resources = "标签"
    query_field = (
        "id",
        "name",
        )
    create_field = (
        "name",
        "description",
        )
    update_field = (
        "id",
        "name",
        "description",
        )
    create_required_field = (
        "name",
        )
    
    def query_attach_book(self, request, *args, **kwargs):
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
            
            data = []
            for i in serializer.data:
                i["book_info"] = BookBeLabelSerializer.get_book(i["id"])
                data.append(i)
            
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{request.data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    def delete_queryset(self):
        return self.queryset.filter(is_used=False)


class BookBeLabelView(BaseView):
    queryset = BookBeLabelModel.objects.filter()
    serializer_class = BookBeLabelSerializer
    resources = "书籍标签关系"
    create_field = (
        "book_id",
        "label_id",
        )
    create_required_field = (
        "book_id",
        "label_id",
        )
