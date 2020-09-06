"""
Django settings for djangor project.

Generated by 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import datetime
import sys

from djangor.config import Mysql, DEBUG


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#添加工程导包路径
sys.path.insert(0,os.path.join(BASE_DIR,"djangor"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%s@n9q(7jlwrym=^h4-9^y7^1&*&!)k@u*uez^f-6384cow843'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # 跨域支持
    "books.apps.BooksConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # 跨域支持
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'HOST': Mysql.host,  # 数据库主机
        'PORT': Mysql.port,  # 数据库端口
        'USER': Mysql.user,  # 数据库用户名
        'PASSWORD': Mysql.password,  # 数据库用户密码
        'NAME': Mysql.db  # 数据库名字
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'




# DRF配置文件
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 需要登录成功的用户才能访问
        ],
    # 认证处理方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'djangor.utils.auth.ApiAuthentication',  # 自定义认证
        'djangor.utils.auth.ThirdPartyAuthentication',  # 自定义认证
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',  # JWT认证
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        ),
    # 异常处理
    'EXCEPTION_HANDLER': 'djangor.utils.exceptions.my_exception_handler',
    # 全局分页配置类
    # 'DEFAULT_PAGINATION_CLASS': 'midomall.utils.my_pagination.StandardResultsSetPagination',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)-8s %(asctime)s %(module)s %(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',  # 时间格式
            },
        'simple': {
            'format': '%(levelname)-8s %(module)s %(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',  # 时间格式
            },
            
        },
    'filters': {  # 对日志进行过滤,一般不会用到
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
            },
        },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'debug_file': {  # 向文件中输出日志
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 轮转日志
            'filename': os.path.join(BASE_DIR, "logs/log.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
            },
        'error_file': {  # 向文件中输出日志
            'level': 'ERROR',
            'class': 'logging.FileHandler',  # 单文件日志
            'filename': os.path.join(BASE_DIR, "logs/error.log"),  # 日志文件的位置
            'formatter': 'verbose'
            },
        },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'debug_file', 'error_file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
            },
        }
    }

# JWT配置文件
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),  # JWT认证有效期
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'djangor.utils.auth.jwt_response_payload_handler',  # 登录成功后返回的参数
    'JWT_AUTH_COOKIE': 'Authorization'  # 认证是否支持cookie
    }

# 自定义的用户模型类
# AUTH_USER_MODEL = 'users.User'

# 告知Django使用我们自定义的认证后端
AUTHENTICATION_BACKENDS = [
    'djangor.utils.auth.ThirdPartyAuthBackend',
    ]

# CORS 跨域请求
# CORS_ORIGIN_ALLOW_ALL = True # 允许所有的站点
# 跨域请求 白名单
CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
    "http://127.0.0.1:9000",
    "https://google.com",
    )
# 跨域请求正则
CORS_ORIGIN_REGEX_WHITELIST = [
    r"^https://\w+\.example\.com$",
    ]
CORS_ALLOW_CREDENTIALS = True  # 保证跨域请求中,允许携带cookie