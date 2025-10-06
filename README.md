from tutorial.tutorial.settings import INSTALLED_APPSfrom pexpect.replwrap import pythonfrom django.utils.translation.trans_real import activate

# DRF-Tutorial
Django rest framework 示例教程


## 一、环境准备
### 1.1 创建虚拟环境，安装django，djangorestframework
```python
# 1、创建目录DRF-Tutorial，创建虚拟环境
mkdir DRF-Tutorial
cd DRF-Tutorial
python3 -m venv .env

# 2、激活虚拟环境，安装django, djangorestframework
source .env/bin/activate
pip install django
pip install djangorestframework
```

### 1.2 创建project Tutorial，创建 app course
```python
# 创建Tutorial项目，注意：macOS 可能会出现找不到django-admin的情况，可以指定manage.py的目录
.env/bin/django-admin startproject tutorial

# 进入tutorial，创建course app
cd tutorial
../env/bin/django-admin startapp course

```

### 1.3 创建管理员账户，访问admin后台
```python
# 第一次提交数据库
python3 manage.py migrate

# 控制台创建超级管理员,设置密码123456
python3 manage.py createsuperuser admin
```

### 1.4 配置项
- 打开tutorial/setting.py，如下配置
```python
# 注册 admin相关app，djangorestframework， course
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # 注册rest_framework
    'rest_framework.authtoken', # 注册 drf token 认证
    'course.apps.CourseConfig', # 注册 course.apps.CourseConfig
]

LANGUAGE_CODE = 'zh-CN' # 语言

TIME_ZONE = 'Asia/Shanghai' # 时区
```
- DRF全局配置
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', # 分页
    'PAGE_SIZE': 50, # 每页大小
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S', # 接口时间格式
    'DEFAULT_RENDERER_CLASSES': ( # 重定向
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': ( # 解析request.data
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser'
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': ( # 权限控制
        'rest_framework.permissions.IsAuthenticated',
    ), 
    'DEFAULT_AUTHENTICATION_CLASSES': [ # 认证
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ] 
}
```
- 因为注册了 rest_framework.authtoken 再次提交数据表，会创建 authtoken_token 表
```python
(.env) hb32366@hb32366deMacBook-Pro tutorial % manage.py makemigrations
No changes detected
(.env) hb32366@hb32366deMacBook-Pro tutorial % manage.py migrate       
Operations to perform:
  Apply all migrations: admin, auth, authtoken, contenttypes, sessions
Running migrations:
  Applying authtoken.0001_initial... OK
  Applying authtoken.0002_auto_20160226_1747... OK
  Applying authtoken.0003_tokenproxy... OK
  Applying authtoken.0004_alter_tokenproxy_options... OK

```
- 配置rest_framework.authtoken 路由, 就可以直接访问api_auth/login接口了
```python
from django.urls import path, include

urlpatterns = [
    path('api_auth/', include('rest_framework.urls'), name='api_auth'), # drf的登录登出接口
    
```


## 二、模型

### 2.1、多数据库配置，可以在setting中定义多个数据库实例
- 在setting.py文件中配置多数据库实例default、myApi
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'myApi':{
        'ENGINE':'django.db.backends.mysql',
        'NAME': 'myApi',
        'USER': 'test',
        'PASSWORD': '123456',
        'HOST': 'ec2-78-12-183-10.mx-central-1.compute.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8'},
    }
}
```
- 在setting.py 同级目录创建 db_router.py（内容固定写法，可直接copy使用），实现自动路由数据库
```python
from django.conf import settings

DATABASE_MAPPING = settings.DATABASE_APPS_MAPPING

class DatabaseAppsRouter(object):
    """
    A router to control all database operations on models for different
    databases.
    In case an app is not set in settings.DATABASE_APPS_MAPPING, the router
    will fallback to the `default` database.
    Settings example:
    DATABASE_APPS_MAPPING = {'app1': 'db1', 'app2': 'db2'}
    """

    def db_for_read(self, model, **hints):
        """"Point all read operations to the specific database."""
        """将所有读操作指向特定的数据库。"""
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        """将所有写操作指向特定的数据库。"""
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        """允许使用相同数据库的应用程序之间的任何关系"""
        db_obj1 = DATABASE_MAPPING.get(obj1._meta.app_label)
        db_obj2 = DATABASE_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        else:
            return None

    def allow_syncdb(self, db, model):
        """Make sure that apps only appear in the related database."""
        """确保这些应用程序只出现在相关的数据库中。"""
        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(model._meta.app_label) == db
        elif model._meta.app_label in DATABASE_MAPPING:
            return False
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """Make sure the auth app only appears in the 'auth_db' database."""
        """确保身份验证应用程序只出现在“authdb”数据库中。"""
        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(app_label) == db
        elif app_label in DATABASE_MAPPING:
            return False
        return None
```
- 在setting.py文件中配置app 和 db 映射，并指定db_router
```python
# APP - DB 映射, 格式app:database
DATABASE_APPS_MAPPING = {
   'tutorial' : 'default',
   'course' : 'myApi'
}

# 数据库路由
DATABASE_ROUTERS = ['tutorial.db_router.DatabaseAppsRouter']
```

### 2.2、开发课程信息模型类
- 在course.models.py 中定义课程信息模型, app_label = 'course' 来指定app名，用于多数据库映射,teacher是外键，指定为User表的实例
- on_delete是Django模型中ForeignKey、OneToOneField和ManyToManyField的一个重要参数，它定义了当被引用的对象被删除时，引用它的对象应该如何处理。

| 场景 | 推荐选项 | 原因 |
| :-----| ----: | :----: |
| 强依赖关系 | CASCADE | 子对象无独立存在意义 |
| 重要数据保护 | PROTECT | 防止意外删除 |
|  可选关联   |  SET_NULL   |  允许对象独立存在   |
|   有默认值  |  SET_DEFAULT   |  提供备用方案   |
|  特殊处理   |  SET   |  自定义处理逻辑   |

```python
from django.db import models
from django.conf import settings

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text='课程名称', verbose_name='课程名称')
    introduction = models.TextField(help_text='课程介绍', verbose_name='介绍')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='课程讲师', verbose_name='讲师', default=None)
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text='课程价格', verbose_name='价格')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    class Meta:
        db_table = 'course' # 指定表名
        app_label = 'course'  # 指定app名，用于多数据库映射
        verbose_name = '课程信息'
        verbose_name_plural = verbose_name
        ordering = ['price'] # 排序字段
```

- 迁移course表数据，需要指定数据表 和 数据库，才能创建Course表
- 注意，如果不能更新，可尝试删除django_migrates记录，再操作
```python
manage.py makemigrations course 
manage.py migrate course --database myApi
```

-  编辑admin.py, 注册 Course 到admin 后台，实现后台操作数据，做完这步操作后就可以去admin后台添加记录了

```python
from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'price', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    ordering = ['price']
    list_per_page = 10
    list_editable = ['price']
```


## 三、序列化

### 3.1、继承ModelSerializer序列化模型类, 其中teacher为外键关联，序列化后输出是老师的姓名，并且是只读字段
```python
from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')
    class Meta:
        model = Course
        # fields = '__all__'
        fields = ('name', 'price', 'introduction', 'teacher')
        read_only_fields = ('teacher',)
        # exclude = ('teacher',)
```

### 3.2、带URL的HyperlinkedModelSerializer


## 四、DRF视图和路由

### 4.1 Django的views开发RESTful API接口
- Django原生function base view，主要用了django的JsonResponse 和 HttpResponse
- 使用django.core.serializers.serialize 进行序列化的时候需要 指定序列化格式为 json
- 使用post请求时，需要用 @csrf_exempt 装饰，才能进行跨域请求
```python
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

```
- Django原生class base view，和FBV类似，处理序列话，响应，还需要自己实现数据的验证，分页，权限控制
- 其中teacher字段使用的是 User模型的实例，使用原生view无法获取到登录用户
- 跨域可以用类装饰器，然后指定方法装饰器，同时需要指定方法是 dispatch，在Django中dispatch会自动定位到post方法
```python
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
```
- 在course中定义路由，并添加到项目urls.py 中
```python
from . import djangoViews

app_name = 'course'

urlpatterns = [
    path('fbv/list/', djangoViews.courseList, name='Django FBV list'),
    path('fbv/detail/<int:pk>', djangoViews.courseDetail, name='Django FBV detail'),
    path('cbv/list/', djangoViews.CourseList.as_view(), name='Django CBV list'),
]

# 在项目的URL中添加
path('course/', include('course.urls'), name='course'),
```

### 4.2 DRF中的装饰器api_view, 使用api_view 装饰器事，需要指定支持的方法，以数组形式存储
- 需要注意的是，当反序列化时，创建只需要指定data, 更新需要指定 instance 和 data
- 反序列化自带is_valid()方法验证入参
```python
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
```

### 4.3 DRF中的视图APIView，只需继承APIView类，实现List 和 Detail类即可
```python
"""
DRF 的CBV， APIView
"""
class CourseList(APIView):
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
```

### 4.4 DRF中的通用类视图GenericAPIView
-  使用generics.ListCreateAPIView实现列表查询，和创建课程,只需要指定查询集和序列器即可
```python
from rest_framework import generics
from .models import Course
from .serializer import CourseSerializer
class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
```
- 但是当我们发起post请求时，会报下面的错误，是因为我们在之前的view中手动指定了teacher字段，而ListCreateAPIView没有这样的实现
```shell
django.db.utils.IntegrityError: NOT NULL constraint failed: course.teacher_id
```
- 通过查看ListCreateAPIView源码，它提供了 perform_create方法，这里可以重写，来实现指定teacher字段
```shell
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
```
- 同样的，查询操作单个课程详情，只需要继承 generics.RetrieveUpdateDestroyAPIView 即可
```python
class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
```

### 4.5 DRF的viewsets开发课程信息的增删改查接口
- 使用viewsets.ModelViewSet 实现接口，代码极大简化了
```python
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
```
- 下面我们只要实现路由部分即可，方法一比较麻烦，需要指定 协议与方法的字典,其中 list、create、retrieve、update、delete、partial_update都是该类下定义的方法
```python
path('drf_viewset/', drfViewSet.CourseViewSet.as_view({"get":"list", "post":"create"}), name='DRF ViewSet list'),
path('drf_viewset/<int:pk>', drfViewSet.CourseViewSet.as_view({"get":"retrieve", "put":"update", "delete":"destroy", "patch":"partial_update"}), name='DRF ViewSet detail'), 
```

### 4.6 Django的URLs与DRF的Routers，使用路由来注册ViewSet, 这种方法相对简单些
```python

router = routers.DefaultRouter()
router.register(r'drf_viewset', drfViewSet.CourseViewSet)
path("", include(router.urls), name='drf ViewSet'),

```


## 五、DRF的认证和权限

### 5.1 Django信号机制自动生成Token
- 5.1.1 setting中设置全局认证方式
```python
    'DEFAULT_AUTHENTICATION_CLASSES': [ # 认证方式
        'rest_framework.authentication.TokenAuthentication',
    ]
```
- 5.1.2 app中注册 token, 并使用数据库迁移命令，生成authtoken_token数据表
```python
INSTALLED_APPS ={
        'rest_framework.authtoken', # 注册 drf token 认证
}
```
- 5.1.3 FBV、CBV对象级别设置认证方式，这种优先级高于 setting中的设置
- 5.1.4 测试生成token， 使用manage命令生成token，执行完毕，我们可以看到表里成功写入token
```python
python manage.py drf_create_token admin
Generated token 1758906d786a32f6260440b23f3217e0e77fdf89 for user admin
```
- 5.1.4 使用Django的信号机制，在创建用户的时候生成token, 此处我们在drfViewSet视图中实现
```python
from django.db.models.signals import post_save # 引入model保存时的信号
from django.dispatch import receiver # 引入信号接收器，执行被装饰的函数
from django.contrib.auth.models import User # 方法一：引入Django的User模型类
from django.conf import settings # 方法一：引入Django, 通过settings.AUTH_USER_MODEL 指定sender
from rest_framework.authtoken.models import Token  # 引入drf token模型类

@receiver(post_save, sender=settings.AUTH_USER_MODEL) # sender 发送着是Django的User模型类
def generate_token(sender, instance=None, created=False, **kwargs):
    if created: # 如果用户创建成功
        Token.objects.create(user=instance)
```
- 5.1.5 我们在admin后台创建用户成功后，可看到表了已经写入token，但是后续的请求需要使用token认证，那我们必须要能获取token
- 5.1.5 在总路由urls.py 中使用auth_token.views 获取已存在的token，使用post请求，json格式用户名密码认证
```python
from rest_framework.authtoken import views
path('auth_token/', views.obtain_auth_token, name='auth_token'), # 获取drf token

curl --location 'http://127.0.0.1:8000/auth_token/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=mXGVKeuVNmcRtdK5chhh6arLUcqMgfbS' \
--data '{
    "username": "admin",
    "password": "123456"
}'

# 可以看到成功获取到了token
{
    "token": "1758906d786a32f6260440b23f3217e0e77fdf89"
}

```
- 5.1.6 携带token请求接口
- 对于drf CBV，只需要指定认证方式，然后在请求头中加上 Authorization:Token dbf20be5f2149fb62a4d6ed40c5d1d1911e4e28c
```python
authentication_classes = (BasicAuthentication, TokenAuthentication,)

# 请求头中携带 Token ，注意固定格式
curl --location 'http://127.0.0.1:8000/course/drf_viewset/' \
--header 'Authorization: Token dbf20be5f2149fb62a4d6ed40c5d1d1911e4e28c' \
--header 'Cookie: csrftoken=mXGVKeuVNmcRtdK5chhh6arLUcqMgfbS'
```
- 对于drf FBV, 我们使用装饰器的方式来指定认证， 例如在drfView.py文件中, 我们导入 authentication_classes装饰器，然后直接在FBV上添加装饰器，指定认证方式，需要注意的是，次装饰器要放在api_view之后
```python
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes

@authentication_classes([TokenAuthentication, BasicAuthentication])
def course_list(request):
    pass

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
def course_detail(request, pk):
    pass
```
- token认证成功可以返回数据，token认证失败，返回失败提示
```python
{
    "detail": "认证令牌无效。"
}
```

### 5.2 DRF的权限控制
- 5.2.1 设置全局权限控制, 在setting文件中设置 DEFAULT_PERMISSION_CLASSES
```python
    'DEFAULT_PERMISSION_CLASSES': ( # 权限控制
        'rest_framework.permissions.IsAuthenticated', # 是否认证
        'rest_framework.permissions.IsAuthenticatedOrReadOnly', # 是否认证或只读
        'rest_framework.permissions.IsAdminUser', # 是否admin用户，由User.is_staff 字段控制
    )
```
- 5.2.2 对象级别权限控制, 对于drf CDB 直接用 permission_class指定， 对于drf FBV 使用装饰器permission_classes指定，例如我们针对drfView.py操作
```python
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def course_list(request):
    pass 

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def course_detail(request, pk):
    ...

class CourseList(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    ...

class CourseList(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

# 如果不需要权限控制，直接指定 permission_classes = [AllowAny]
```
- 5.2.3 自定义对象级别权限控制, 对于上文中权限控制，只要是登录用户都能访问修改所有课程，现在的需求是课程老师才有权限修改自己的课程，就必须自定义权限了
  - 创建permission.py 文件，用例自定义权限，继承drf permission.BasePermission
```python
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
```
- 下面以genericsView 为例，添加自定义权限， 查询接口不限制，修改接口必须是所属用户
```python
from .permission import IsOwnerOrReadOnly

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,BasicAuthentication)
    permission_classes = (IsOwnerOrReadOnly, )
```
- 当修改用户不是课程所属用户时会提示下面的错误
```python
{
    "detail": "您没有执行该操作的权限。"
}
```

## 六、API接口文档
### 6.1 setting中配置API文档默认类 DEFAULT_SCHEMA_CLASS, 需要安装  pip install drf-spectacular
```python
'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
```
### 6.2 配置 SPECTACULAR_SETTINGS_
```python
SPECTACULAR_SETTINGS = {
    "title": "Django Rest Framework API",
    "description": "Django Rest Framework 入门",
    "version": "1.0.0",
    'SERVE_INCLUDE_SCHEMA': False,
}
```
### 6.3 在总路由urls.py 中定义docs 文档路径, 请求docs/接口就可以访问swagger的接口文档了
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```
### 七、总结
- Django Rest FrameWork
    - 配置 Setting
    - 请求 Request
    - 响应 Response
      - 状态 Status
    - 模型 Model
    - 序列化 
      - 常用序列化器 ModelSerializer 
      - 带URL的序列化器 HyperlinkedModelSerializer
      - 验证 Validator
    - 视图 View
      - 原生django视图 
        - 函数视图 FBV （function base view）
        - 类视图 CBV （class base view）
      - rest framework 视图
        - 装饰器FBV视图 @api_view['GET', 'POST']
        - 类视图CBV APIView
        - 通用类视图 generics View
        - 视图集 ViewSet
    - 路由
      - 注册路由
    - 认证 Auth
    - 权限 Permission
    - 限流 Throttling
    - 分页 Pagination
    - 过滤 Filters
    - 版本 Version
    - 异常 Exception
    - 内容协商 Negotiation
    - 元数据 Metadata
    - 渲染器 Renderers