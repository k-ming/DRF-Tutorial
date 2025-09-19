import json

from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Course

"""
Django function base view 
Django 函数视图
Django serializer
Django 原生序列化器
"""
@csrf_exempt
def courseList(request):
    courses = Course.objects.all()
    if request.method == "GET":
        return HttpResponse(
            serialize('json', courses),
            content_type="application/json",
            status=200,
        )
    if request.method == "POST":
        data = json.loads(request.body)
        errors = {}
        # 字段验证
        if not data.get("name"):
            errors['msg'] = 'name is required'
        elif not data.get("price"):
            errors['msg'] = 'price is required'
        elif errors:
            return HttpResponse(
                json.dumps(errors),
                content_type="application/json",
            )
        else:
            course = Course.objects.create(
                name=data["name"],
                teacher=User.objects.get(username='admin'),
                price=data["price"],
                introduction=data["introduction"],
            )
            course.save()
            return HttpResponse(serialize('json', [course]), status=201)

@csrf_exempt
def courseDetail(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return JsonResponse({"msg": "course does not exist"}, status=404)
    if request.method == "GET":
        return HttpResponse(
            serialize('json', [course]),
            status=200,
            content_type="application/json")
    else:
        return JsonResponse({"msg":"method not allowed"}, status=405)

"""
Django Class based view 
Django 类视图
"""
@method_decorator(csrf_exempt, name='dispatch')
class CourseList(View):
    def get(self, request):
        query_set = Course.objects.all()
        return HttpResponse(serialize('json', query_set), status=200, content_type="application/json")

    def post(self, request):
        data = json.loads(request.body)
        errors = {}
        if not data.get("name"):
            errors['msg'] = 'name is required'
        if not data.get("price"):
            errors['msg'] = 'price is required'
        if not errors:
            course = Course.objects.create(
                name=data["name"],
                teacher=User.objects.get(username='kingming'),
                price=data["price"],
                introduction=data["introduction"],
            )
            course.save()
            return JsonResponse(json.loads(serialize('json', [course])), status=201, safe=False)
        else:
            return JsonResponse(errors, status=404)

class CourseDetail(View):
    def get(self, request, pk):
        try:
            query_set = Course.objects.get(id=pk)
        except Course.DoesNotExist:
            return JsonResponse({"msg": "course does not exist"}, status=404)
        return HttpResponse(serialize('json', [query_set]), status=200, content_type="application/json")
    def put(self, request, pk):
        pass
    def delete(self, request, pk):
        pass