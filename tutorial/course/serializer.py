from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')
    class Meta:
        model = Course
        # fields = '__all__'
        fields = ('id', 'name', 'price', 'introduction', 'teacher')
        read_only_fields = ('teacher',)
        # exclude = ('teacher',)