# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config
from unipath import Path
import ldap
from django_auth_ldap.config import LDAPSearch
from django_auth_ldap.config import ActiveDirectoryGroupType
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# load production server from .env
#ALLOWED_HOSTS = ['localhost', '127.0.0.1', config('SERVER', default='127.0.0.1')]
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor', #para formulario com edição
    'wkhtmltopdf',
    'bootstrapform', #FORMULARIOS BOOTSTRAP 
    'bootstrap_datepicker_plus', #FORMULARIOS DE DATAS
    'app',  # Enable the inner app 
    'system', # Aplicação para controle de cadastros do ADMIN
    'geral', # Cadastro de informações gerais relacionadas ao sistema
    'pedagogico', #Sistema Pedagogicos
    'ged' #Sistema de registro de atas
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "core/templates")  # ROOT dir for templates

# Configurações personalizadas do CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom', # Indica que usaremos uma toolbar customizada
        'toolbar_Custom': [ # Define os botões da toolbar
           {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'insert', 'items': ['Table', 'HorizontalRule', 'SpecialChar']},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            '/', # Quebra de linha na barra de ferramentas
        ],
        'height': 300,
        'width': '100%',
        # Remove plugins de imagem do editor
        'removePlugins': 'image,image2,picture', 
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

##DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME'  : 'db.sqlite3',
#    }

try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()

# [START db_setup]
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '/cloudsql/sistema-311913:southamerica-east1:sistema',
            'NAME': 'sistema',
            'USER': 'jefferson',
            'PASSWORD': 'senha',
        }
    }
else:
    # Running locally so connect to either a local MySQL instance or connect to
    # Cloud SQL via the proxy. To start the proxy via command line:
    #
    #     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    #
    # See https://cloud.google.com/sql/docs/mysql-connect-proxy
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'NAME': 'sistemasifsc',
            'USER': 'ifsc',
            'PASSWORD': 'ifsc@2021',
        }
    }

    #DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.db.backends.mysql',
    #        'HOST': '127.0.0.1',
    #        'PORT': '3306',
    #        'NAME': 'sistemasifsc',
    #        'USER': 'jefferson',
    #        'PASSWORD': 'Je@784512',
    #    }
    #}
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.mysql',
#            'HOST': '200.135.162.154',
#            'PORT': '3306',
#            'NAME': 'sistemasifsc',
#            'USER': 'jefferson',
#            'PASSWORD': 'Je@784512',
#        }
#    }



# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_LDAP_SERVER_URI = 'ldap://191.36.16.2'
AUTH_LDAP_BIND_DN = "cn=manager,dc=cefetsc,dc=edu,dc=br"
AUTH_LDAP_BIND_PASSWORD = "k4br4-c3g4*bal"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
            "ou=Usuarios,dc=cefetsc,dc=edu,dc=br", ldap.SCOPE_SUBTREE, "cn=%(user)s"
            )

AUTH_LDAP_USER_ATTR_MAP = {
            "username": "sAMAccountName",
            "first_name": "givenName",
            "last_name": "sn",
            "email": "mail",
}

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
            "dc=cefetsc,dc=edu,dc=br", ldap.SCOPE_SUBTREE, "(objectCategory=Group)"
            )
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType(name_attr="cn")
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
            "is_superuser": "cn=manager,dc=cefetsc,dc=edu,dc=br",
            "is_staff": "cn=manager,dc=cefetsc,dc=edu,dc=br",
            }
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 1  # 1 hour cache

AUTHENTICATION_BACKENDS = [
            'django_auth_ldap.backend.LDAPBackend',
            'django.contrib.auth.backends.ModelBackend',
]

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATE_FORMAT = 'd/m/Y'

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
#STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_ROOT = 'static'
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'core/static'),
)
#############################################################
#############################################################
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
SILENCED_SYSTEM_CHECKS = ['ckeditor.W001']