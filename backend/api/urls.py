from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework import routers

from api.views import *

app_name = "api"
router = routers.DefaultRouter()
# router.register('users', CustomUserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('djoser.urls')),#не точно
    path('auth/', include('djoser.urls.authtoken')),#не точно
]