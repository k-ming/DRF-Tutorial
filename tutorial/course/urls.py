from django.urls import path, include
from rest_framework import routers

from . import djangoViews, drfView, drfGenericsView,drfViewSet

app_name = 'course'

router = routers.DefaultRouter()
router.register(r'drf_viewset', drfViewSet.CourseViewSet)

urlpatterns = [
    path('dj_fbv/list/', djangoViews.courseList, name='Django FBV list'),
    path('dj_fbv/detail/<int:pk>', djangoViews.courseDetail, name='Django FBV detail'),
    path('dj_cbv/list/', djangoViews.CourseList.as_view(), name='Django CBV list'),
    path('drf_fbv/list/', drfView.course_list, name='DRF FBV list'),
    path('drf_fbv/detail/<int:pk>', drfView.course_detail, name='DRF FBV detail'),
    path('drf_cbv/list/', drfView.CourseList.as_view(), name='DRF CBV list'),
    path('drf_cbv/detail/<int:pk>', drfView.CourseDetail.as_view(), name='DRF CBV detail'),
    path('drf_gv/list/', drfGenericsView.CourseList.as_view(), name='DRF GV list'),
    path('drf_gv/detail/<int:pk>', drfGenericsView.CourseDetail.as_view(), name='DRF GV detail'),
    # path('drf_viewset/', drfViewSet.CourseViewSet.as_view({"get":"list", "post":"create"}), name='DRF ViewSet list'),
    # path('drf_viewset/<int:pk>', drfViewSet.CourseViewSet.as_view({"get":"retrieve", "put":"update", "delete":"destroy", "patch":"partial_update"}), name='DRF ViewSet detail'),
    path("", include(router.urls), name='drf ViewSet'),
]
