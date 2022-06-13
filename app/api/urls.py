from django.urls import path
from rest_framework.routers import DefaultRouter

from api import views


app_name = 'api'

router = DefaultRouter()

router.register('clients', views.ClientViewSet, 'clients')
router.register('organizations', views.OrganizationViewSet, 'organizations')
router.register('bills', views.BillViewSet, 'bills')

urlpatterns = [
    path('', views.index, name='main'),
    path('upload-files/', views.upload_files, name='upload_files'),
    *router.urls,
]
