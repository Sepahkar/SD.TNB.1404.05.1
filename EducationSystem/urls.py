from django.urls import path
from . import views

# app_name = 'ConfigurationChangeRequest'

urlpatterns = [
    # ایجاد درخواست جدید
    # path('', views.test, name='request_create'),
    path('', views.welcome, name='welcome'),           # صفحه اول
    path('login/', views.login_view, name='login'),    # صفحه لاگین
    path('dashboard/', views.dashboard_view, name='dashboard'),  # صفحه داشبورد
    path('profile/', views.profile_view, name='profile'),        # صفحه پروفایل
        path('loan/', views.loan, name='loan_page'),

    ]
    
