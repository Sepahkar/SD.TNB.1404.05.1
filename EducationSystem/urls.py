from django.urls import path
from . import views

app_name = 'ConfigurationChangeRequest'

urlpatterns = [
    # ایجاد درخواست جدید
    path('', views.test, name='request_create'),
    ]
