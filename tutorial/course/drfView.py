from functools import partial

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Course
from .serializer import CourseSerializer

"""
DRF的FBV， 装饰器api_view视图
"""
@api_view(['GET', 'POST'])
def course_list(request):
    query_set = Course.objects.all()
    serializer = CourseSerializer(query_set, many=True)
    if request.method == 'GET':
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user) # 获取author.User
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def course_detail(request, pk):
    try:
        query_set = Course.objects.get(pk=pk)
        serializer = CourseSerializer(query_set, many=False)
    except Course.DoesNotExist:
        return Response({"msg":"course is no exist"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = CourseSerializer(data=request.data, instance=query_set)
        if serializer.is_valid():
            serializer.save(partial=True)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        serializer = CourseSerializer(data=request.data, instance=query_set)
        if serializer.is_valid():
            serializer.save(partial=True, teacher=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        query_set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)