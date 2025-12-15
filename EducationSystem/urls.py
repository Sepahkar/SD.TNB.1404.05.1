from django.urls import path
from . import views
from .APIs.StudentInformation import StudentProfileFullView
from .APIs.LessonList import CoursesProvidedAPIView

# app_name = 'EducationSystem'

urlpatterns = [
    # ============================================
    # HTML Page Routes
    # ============================================
    
    path('', views.welcome, name='welcome'),           # صفحه اول
    path('login/', views.login_view, name='login'),    # صفحه لاگین
    path('logout/', views.logout_view, name='logout'),  # خروج
    path('dashboard/', views.dashboard_view, name='dashboard'),  # صفحه داشبورد
    path('profile/', views.profile_view, name='profile'),        # صفحه پروفایل
    path('course-selection/', views.course_selection_view, name='course_selection'),  # صفحه انتخاب واحد
    path('loan/', views.loan, name='loan_page'),  # صفحه وام
    path('student-management/', views.student_management, name='student_management'),  # مدیریت دانشجویان
    path('course-management/', views.course_management, name='course_management'),  # مدیریت دروس
    
    # ============================================
    # API Endpoints (for AJAX calls from HTML pages)
    # ============================================
    
    # احراز هویت
    # POST /api/auth/login
    path('api/auth/login/', views.api_login, name='api_login'),
    
    # اطلاعات دانشجو
    # GET /api/student/profile/basic
    path('api/student/profile/basic/', views.api_student_basic_profile, name='api_student_basic_profile'),
    # GET /api/student/profile/full
    path('api/student/profile/full/', StudentProfileFullView.as_view(), name='api_student_profile_full'),
    # GET /api/student/dashboard
    path('api/student/dashboard/', views.api_student_dashboard, name='api_student_dashboard'),
    
    # دروس
    # GET /api/courses/provided
    path('api/courses/provided/', CoursesProvidedAPIView.as_view(), name='api_courses_provided'),
]
