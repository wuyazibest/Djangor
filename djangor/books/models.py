from django.db import models

# Create your models here.
from djangor.utils import BaseModel, RichBaseModel


class BookKind(models.TextChoices):
    """传给前端的为英文  前端根据键值字典去显示中文名，不应该直接返回中文名
    展示名 与存储值不能混淆
    """
    CL = ("classical", "古典")
    ST = ("story", "小说")
    KN = ("knowledge", "科学知识类")
    EM = ("emotion", "故事情感")
    MI = ("miscellaneous", "杂项")


class BookModel(RichBaseModel):
    """
    书模型类
    """
    PUBLISHING_CHOICE = (
        (0, "未出版"),
        (1, "已出版"),
        )
    name = models.CharField(max_length=191, verbose_name="名称")
    writer = models.CharField(blank=True, max_length=191, verbose_name="作者")
    kind = models.CharField(max_length=191, choices=BookKind.choices, default=BookKind.ST, verbose_name="类型")
    link = models.CharField(max_length=191, blank=True, verbose_name="链接")
    directory = models.CharField(max_length=191, blank=True, verbose_name="存储目录")
    publishing = models.IntegerField(choices=PUBLISHING_CHOICE, default=0, verbose_name="出版标识")
    publication_date = models.DateField(null=True, verbose_name="出版日期")
    
    class Meta:
        unique_together = ("name", "is_deleted")
        db_table = "books_book"
        verbose_name = "书"
        verbose_name_plural = verbose_name
        ordering = ["-update_time"]  # 指明默认排序规则,查询之后自动将结果排序


class LabelModel(RichBaseModel):
    """
    标签
    """
    name = models.CharField(max_length=191, verbose_name="标签名")
    description = models.TextField(blank=True, verbose_name="详细说明")
    
    class Meta:
        unique_together = ("name", "is_deleted")
        db_table = "books_label"
        verbose_name = "标签表"
        verbose_name_plural = verbose_name


class BookBeLabelModel(BaseModel):
    """
    文章标签关系
    """
    book_id = models.IntegerField(verbose_name="文档id")
    label_id = models.IntegerField(verbose_name="标签id")
    
    class Meta:
        unique_together = ("book_id", "label_id")
        db_table = "books_book_bo_label"
        verbose_name = "书籍标签关系表"
        verbose_name_plural = verbose_name
