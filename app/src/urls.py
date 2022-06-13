from django.contrib import admin
from django.urls import path, include

from src import views


urlpatterns = [
    path('', views.index, name='main'),
    path('admin/', admin.site.urls),
    path('clients/', include('clients.urls'), name='clients'),
    path('api/', include('api.urls'), name='api'),
]
