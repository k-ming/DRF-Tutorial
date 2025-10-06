from functools import partial
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Course
from .serializer import CourseSerializer
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

"""
DRF的FBV， 装饰器api_view视图
"""
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
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
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
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

"""
DRF 的CBV， APIView
"""
class CourseList(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query_set = Course.objects.all()
        serializer = CourseSerializer(query_set, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetail(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            query_set = Course.objects.get(pk=pk)
            serializer = CourseSerializer(query_set, many=False)
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response({"msg":"course is no exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            query_set = Course.objects.get(pk=pk)
            serializer = CourseSerializer(query_set, data=request.data)
            if serializer.is_valid():
                serializer.save(teacher=request.user, partial=True)
                return Response(serializer.data)
        except Course.DoesNotExist:
            return Response({"msg":"course is no exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            query_set = Course.objects.get(pk=pk)
            query_set.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            return Response({"msg":"course is no exist"}, status=status.HTTP_404_NOT_FOUND)

