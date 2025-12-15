from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login
# Note: Using session-based auth instead of Django's login_required
# since we're using Student model directly, not User model
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import json

# Import models
from .models import Student, Course, Class, StudentClassRegistration, FieldOfStudy, ProfessorCourseAssignment

# Import API views from APIs folder
from .APIs.StudentInformation import StudentProfileFullView
from .APIs.LessonList import CoursesProvidedAPIView

# Import serializers
from .serializers import StudentFullSerializer


# ============================================
# Helper Functions
# ============================================

def get_student_from_session(request):
    """Get student from session"""
    student_id = request.session.get('student_id')
    if student_id:
        try:
            return Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return None
    return None


def get_student_from_request(request):
    """Get student from request (session or query param)"""
    student = get_student_from_session(request)
    if not student:
        student_id = request.GET.get('student_id') or request.GET.get('studentId')
        if student_id:
            try:
                student = Student.objects.get(student_number=student_id)
            except Student.DoesNotExist:
                pass
    return student


# ============================================
# HTML Page Views
# ============================================

def welcome(request):
    """صفحه خوش‌آمدگویی"""
    return render(request, "EducationSystem/pages/welcome.html")


def login_view(request):
    """صفحه لاگین و احراز هویت"""
    if request.method == "POST":
        student_id = request.POST.get("student_id") or request.POST.get("studentId")
        password = request.POST.get("password")
        
        # TODO: Implement proper password authentication
        # For now, we'll use student_number as a simple check
        try:
            student = Student.objects.get(student_number=student_id)
            # Store student ID in session
            request.session['student_id'] = student.id
            request.session['student_number'] = student.student_number
            return redirect('dashboard')
        except Student.DoesNotExist:
            return render(request, "EducationSystem/pages/login.html", {
                'error': 'شماره دانشجویی یا رمز عبور اشتباه است'
            })
    
    return render(request, "EducationSystem/pages/login.html")


def logout_view(request):
    """خروج از سیستم"""
    request.session.flush()
    return redirect('welcome')


def dashboard_view(request):
    """صفحه داشبورد"""
    student = get_student_from_session(request)
    
    if not student:
        return redirect('login')
    
    # Calculate passed and total units
    passed_units = student.total_credits_passed or 0
    total_units = student.field_of_study.total_credits if student.field_of_study else 144
    percent = (passed_units / total_units * 100) if total_units > 0 else 0
    
    # Get GPA
    gpa = student.gpa or 0
    
    # Comparison chart data (placeholder - should be calculated from database)
    comparison_chart = {
        'sameEntranceAvg': 10.0,
        'sameMajorAvg': 22.0,
        'sameFacultyAvg': 42.0,
        'universityAvg': 62.0
    }
    
    context = {
        'passed': passed_units,
        'total': total_units,
        'percent': round(percent, 2),
        'gpa': round(gpa, 2),
        'comparison_chart': comparison_chart,
        'student': student
    }
    
    return render(request, "EducationSystem/pages/dashboard.html", context)


def profile_view(request):
    """صفحه پروفایل دانشجو"""
    student = get_student_from_session(request)
    
    if not student:
        return redirect('login')
    
    # Format enrollment date for display
    entry_semester = None
    if student.enrollment_date:
        # Convert to Persian date format (simplified)
        entry_semester = student.enrollment_date.strftime('%y%m')
    
    context = {
        'student': {
            'first_name': student.first_name,
            'last_name': student.last_name,
            'student_number': student.student_number,
            'national_id': student.national_id,
            'entry_semester': entry_semester,
            'field_of_study': student.field_of_study.name if student.field_of_study else '',
            'specialization': student.specialization.name if student.specialization else '',
            'degree': student.field_of_study.degree_level if student.field_of_study else '',
        }
    }
    
    return render(request, "EducationSystem/pages/profile.html", context)


def course_selection_view(request):
    """صفحه انتخاب واحد"""
    student = get_student_from_session(request)
    
    if not student:
        return redirect('login')
    
    # Get courses if search is performed
    courses = []
    course_name_filter = None
    
    if request.method == "POST":
        course_name_filter = request.POST.get('course_name', '')
        if course_name_filter:
            courses = Course.objects.filter(
                name__icontains=course_name_filter,
                is_active=True
            ).select_related('field_of_study')[:20]
    
    # Get classes for each course
    course_data = []
    for course in courses:
        classes = Class.objects.filter(
            course=course,
            term__is_registration_open=True,
            is_active=True
        ).select_related('room', 'term')[:5]
        
        for cls in classes:
            # Format class time
            day_name = dict(Class.DAY_CHOICES).get(cls.day_of_week, cls.day_of_week)
            class_time = f"{day_name} {cls.start_time.strftime('%H:%M')}-{cls.end_time.strftime('%H:%M')}"
            
            # Get professor name
            professor_assignment = ProfessorCourseAssignment.objects.filter(
                class_course=cls,
                is_primary=True
            ).select_related('professor').first()
            professor_name = professor_assignment.professor.full_name if professor_assignment and professor_assignment.professor else 'تعیین نشده'
            
            # Get registered count
            registered_count = StudentClassRegistration.objects.filter(
                class_course=cls,
                status__in=['R', 'P', 'F']
            ).count()
            
            course_data.append({
                'course_id': course.id,
                'course_name': course.name,
                'course_code': course.code,
                'class_id': cls.id,
                'professor_name': professor_name,
                'class_time': class_time,
                'class_location': cls.room.name if cls.room else 'تعیین نشده',
                'exam_date': 'تعیین نشده',  # Would need exam_date field in Class model
                'capacity': cls.capacity,
                'registered': registered_count,
            })
    
    context = {
        'student': student,
        'courses': course_data,
        'course_name_filter': course_name_filter or '',
    }
    
    return render(request, "EducationSystem/pages/course_selection.html", context)


def loan(request):
    """صفحه وام"""
    student = get_student_from_session(request)
    
    if not student:
        return redirect('login')
    
    # Format enrollment date
    admission_term = None
    if student.enrollment_date:
        admission_term = student.enrollment_date.strftime('%y%m')
    
    context = {
        "student": {
            "first_name": student.first_name,
            "last_name": student.last_name,
            "student_no": student.student_number,
            "admission_term": admission_term or "1400",
            "father_name": "",  # Not in Student model, would need to be added
            "faculty_group": student.field_of_study.college.name if student.field_of_study and student.field_of_study.college else "تعیین نشده",
            "level": student.field_of_study.degree_level if student.field_of_study else "تعیین نشده",
            "major": student.field_of_study.name if student.field_of_study else "تعیین نشده",
        }
    }
    
    return render(request, "EducationSystem/pages/Loan.html", context)


def student_management(request):
    """صفحه مدیریت دانشجویان"""
    return render(request, 'EducationSystem/pages/student_management.html')


def course_management(request):
    """صفحه مدیریت دروس"""
    return render(request, 'EducationSystem/pages/course_management.html')


# ============================================
# API Endpoints (for AJAX calls from HTML pages)
# ============================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_student_basic_profile(request):
    """API: اطلاعات اولیه دانشجو برای هدر"""
    student = get_student_from_request(request)
    
    if not student:
        return Response(
            {"detail": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        "studentId": student.student_number,
        "fullName": student.full_name,
        "gender": "Female" if student.gender == 'F' else "Male"
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_student_dashboard(request):
    """API: اطلاعات داشبورد دانشجو"""
    student = get_student_from_request(request)
    
    if not student:
        return Response(
            {"detail": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    passed_units = student.total_credits_passed or 0
    total_units = student.field_of_study.total_credits if student.field_of_study else 144
    gpa = student.gpa or 0
    
    return Response({
        "passedUnits": passed_units,
        "totalUnits": total_units,
        "gpa": round(gpa, 2),
        "gender": "Female" if student.gender == 'F' else "Male",
        "comparisonChart": {
            "sameEntranceAvg": 10.0,
            "sameMajorAvg": 22.0,
            "sameFacultyAvg": 42.0,
            "universityAvg": 62.0
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API: ورود با نام کاربری و رمز عبور"""
    student_id = request.data.get('studentId') or request.data.get('student_id')
    password = request.data.get('password')
    
    if not student_id:
        return Response(
            {"detail": "studentId is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        student = Student.objects.get(student_number=student_id)
        # TODO: Implement proper password authentication
        # For now, return a simple token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken()
        refresh['student_id'] = student.id
        refresh['student_number'] = student.student_number
        
        return Response({
            "token": str(refresh.access_token),
            "refresh": str(refresh)
        })
    except Student.DoesNotExist:
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )


# Export API views for use in urls.py
__all__ = [
    'welcome',
    'login_view',
    'logout_view',
    'dashboard_view',
    'profile_view',
    'course_selection_view',
    'loan',
    'student_management',
    'course_management',
    'api_student_basic_profile',
    'api_student_dashboard',
    'api_login',
    'StudentProfileFullView',  # From APIs/StudentInformation
    'CoursesProvidedAPIView',  # From APIs/LessonList
]
