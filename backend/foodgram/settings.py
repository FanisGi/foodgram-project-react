import os

from dotenv import load_dotenv

load_dotenv('../infra/.env')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECRET_KEY = os.getenv(key='SECRET_KEY')
SECRET_KEY = '^e&d+2drlanlltrt6!##-sr1^8@u6v@^v*nw(f@yxe=u)2$gcy'

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'recipes',
    'api',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'djoser',
]

AUTH_USER_MODEL = 'users.Users'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', 
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',

    'PAGE_SIZE': 3,

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning'
}

DJOSER = {
    'SERIALIZERS': {
        'user': 'api.serializers.CustomUserSerializer',
    },
    # 'PERMISSIONS': {
    #     'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly'],
    #     'user_list': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    # },
    'HIDE_USERS': False,
}

# SIMPLE_JWT = {
#    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
#    'AUTH_HEADER_TYPES': ('Bearer',),
# } 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES_DIRS = os.path.join(BASE_DIR, '../docs')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'),)

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
