from django.urls import path

from clients import views


app_name = 'clients'

urlpatterns = [
    path('', views.index, name='main'),
    path('upload-files/', views.upload_files, name='upload_files'),
    path('clients/', views.ClientView.as_view(), name='clients_list'),
    path('organizations/', views.OrganizationView.as_view(), name='organizations_list'),
    path('bills/', views.BillsView.as_view(), name='bills_list'),
    path('clients/<slug:slug>/', views.ClientDetailViews.as_view(), name='clients_detailed')
]
