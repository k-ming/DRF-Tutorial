from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from .models import Course
from .serializer import CourseSerializer
from django.db.models.signals import post_save # 引入model保存时的信号
from django.dispatch import receiver # 引入信号接收器，执行被装饰的函数
from django.contrib.auth.models import User # 方法一：引入Django的User模型类
from django.conf import settings # 方法一：引入Django, 通过settings.AUTH_USER_MODEL 指定sender
from rest_framework.authtoken.models import Token  # 引入drf token模型类

@receiver(post_save, sender=settings.AUTH_USER_MODEL) # sender 发送着是Django的User模型类
def generate_token(sender, instance=None, created=False, **kwargs):
    if created: # 如果用户创建成功
        Token.objects.create(user=instance)


"""
继承ModelViewSet
优点：极大简化代码，实现了列表和详情集成到一个类中
"""
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication,)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)