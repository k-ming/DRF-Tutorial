from rest_framework import generics
from rest_framework.response import Response
from .models import Course
from .serializer import CourseSerializer

"""
generics.ListCreateAPIView 可以实现列表查询，和新建
"""
class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
