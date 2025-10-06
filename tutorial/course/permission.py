from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        所有请求都有读权限，允许的方法为 GET/HEAD/OPTIONS
        :param request:
        :param view:
        :param obj:
        :return: bool
        """
        if request.method in permissions.SAFE_METHODS:  # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
            return True
        return obj.teacher == request.user # 其他方法，如果请求用户不是 Course.teacher 则返回false