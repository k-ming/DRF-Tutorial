from django.db import models
from django.conf import settings

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text='课程名称', verbose_name='课程名称')
    introduction = models.TextField(help_text='课程介绍', verbose_name='介绍')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='课程讲师', verbose_name='讲师', default=None)  # 外键关联 auth.User
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text='课程价格', verbose_name='价格')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'course' # 指定表名
        app_label = 'course'  # 指定app名，用于多数据库映射
        verbose_name = '课程信息'
        verbose_name_plural = verbose_name
        ordering = ['price'] # 排序字段
