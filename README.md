from pexpect.replwrap import pythonfrom django.utils.translation.trans_real import activate

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
- 在course.models.py 中定义课程信息模型, app_label = 'course' 来指定app名，用于多数据库映射,teacher是外键，指定为author表的id, 需要设置默认值，否则迁移表时回报错
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
### 3.1、继承ModelSerializer序列化模型类
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
### 4.2 DRF中的装饰器api_view
### 4.3 DRF中的视图APIView
### 4.4 DRF中的通用类视图GenericAPIView
### 4.5 DRF的viewsets开发课程信息的增删改查接口
### 4.6 Django的URLs与DRF的Routers
## 五、DRF的认证和权限
### 5.1 DRF认证方式介绍
### 5.2 Django信号机制自动生成Token
### 5.3 DRF的权限控制
## 六、API接口文档
### 6.1 如何生成API接口文档
### 6.2 DRF的概要功能讲解，如何配置认证，如何与接口数据交互
### 七、