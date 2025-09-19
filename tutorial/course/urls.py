from django.urls import path, include
from . import djangoViews

app_name = 'course'

urlpatterns = [
    path('fbv/list/', djangoViews.courseList, name='Django FBV list'),
    path('fbv/detail/<int:pk>', djangoViews.courseDetail, name='Django FBV detail'),
    path('cbv/list/', djangoViews.CourseList.as_view(), name='Django CBV list'),
]
