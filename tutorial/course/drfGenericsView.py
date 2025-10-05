from rest_framework import generics
from .models import Course
from .serializer import CourseSerializer

"""
generics.ListCreateAPIView 可以实现列表查询，和新建
"""
class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


