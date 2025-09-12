from django.utils.translation.trans_real import activate

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
    'rest_framework',
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
## 二、模型
### 2.1、开发课程信息模型类
## 三、序列化
### 3.1、继承ModelSerializer序列化模型类
### 3.2、带URL的HyperlinkedModelSerializer
## 四、DRF视图和路由
### 4.1 Django的views开发RESTful API接口
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