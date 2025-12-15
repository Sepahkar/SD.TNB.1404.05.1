from django.urls import path
from . import views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentFullSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

# app_name = 'ConfigurationChangeRequest'

urlpatterns = [
    # ایجاد درخواست جدید
    # path('', views.test, name='request_create'),
    path('', views.welcome, name='welcome'),           # صفحه اول
    path('login/', views.login_view, name='login'),    # صفحه لاگین
    path('dashboard/', views.dashboard_view, name='dashboard'),  # صفحه داشبورد
    path('profile/', views.profile_view, name='profile'),        # صفحه پروفایل
    path('course_selection/', views.course_selection_view, name='course_selection'),        # صفحه پروفایل
    path('loan/', views.loan, name='loan_page'),
    path('loan/', views.loan, name='loan_page'),
    path('student-management/', views.student_management, name='student_management'),
    path('course-management/', views.course_management, name='course_management'),
    path('course-selection/', views.course_selection, name='course_selection'),
]


# app/views.py


# Optional: if you use Simple JWT

class StudentProfileFullView(APIView):
    """
    GET /student/profile/full
    Prefer student id from JWT (claim 'student_id' or 'studentId').
    Fallback to query param ?studentId=...
    """
    authentication_classes = [JWTAuthentication]  # optional
    permission_classes = []  # allow both authenticated and unauthenticated (we check payload)

    def get(self, request, *args, **kwargs):
        student_id = None

        # try extract from JWT payload if present
        try:
            token = getattr(request, 'auth', None)
            if token:
                payload = getattr(token, 'payload', None) or token
                if isinstance(payload, dict):
                    student_id = payload.get('student_id') or payload.get('studentId') or payload.get('sub')
        except Exception:
            student_id = None

        # fallback to query param
        if not student_id:
            student_id = request.query_params.get('studentId') or request.query_params.get('student_id')

        if not student_id:
            return Response({"detail": "studentId not provided. Provide Authorization JWT or ?studentId=..."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ensure integer
        try:
            student_id = int(student_id)
        except Exception:
            return Response({"detail": "studentId must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentFullSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    path('student-management/', views.student_management, name='student_management'),
    path('course-management/', views.course_management, name='course_management'),
    
    # ============================================
    # API Endpoints
    # ============================================
    
    # لیست دروس ارائه شده به همراه فیلتر اسم درس
    # GET /api/courses/provided
    path('courses/provided', views.CoursesProvidedAPIView.as_view(), name='courses_provided'),
]
    

