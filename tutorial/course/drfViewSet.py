from rest_framework import viewsets
from .models import Course
from .serializer import CourseSerializer

"""
继承ModelViewSet
优点：极大简化代码，实现了列表和详情集成到一个类中
"""
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)