from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Configure your production database here
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "mydatabase",
#         "USER": "mydatabaseuser",
#         "PASSWORD": "mypassword",
#         "HOST": "127.0.0.1",
#         "PORT": "5432",
#     }
# }

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles_build"

