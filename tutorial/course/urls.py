from django.urls import path
from . import djangoViews, drfView

app_name = 'course'

urlpatterns = [
    path('dj_fbv/list/', djangoViews.courseList, name='Django FBV list'),
    path('dj_fbv/detail/<int:pk>', djangoViews.courseDetail, name='Django FBV detail'),
    path('dj_cbv/list/', djangoViews.CourseList.as_view(), name='Django CBV list'),
    path('drf_fbv/list/', drfView.course_list, name='DRF FBV list'),
    path('drf_fbv/detail/<int:pk>', drfView.course_detail, name='DRF FBV detail'),
]
