from django.contrib import admin
from .models import Course


# 注册 Course 到admin 后台，实现后台操作数据

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'price', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    ordering = ['price']
    list_per_page = 10
    list_editable = ['price']
    list_display_links = ['name']
