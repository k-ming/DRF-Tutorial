from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from .models import Course
from .serializer import CourseSerializer
from .permission import IsOwnerOrReadOnly

"""
generics.ListCreateAPIView 可以实现列表查询，和新建
"""
class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,BasicAuthentication)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,BasicAuthentication)
    permission_classes = (IsOwnerOrReadOnly, )


