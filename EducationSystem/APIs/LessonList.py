from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course

# Create your views here.
def test(request):
    # Sample test data
    ctx = {
        "student": {
            "first_name": "امیرحسین",
            "last_name": "رجبی",
            "student_no": "403159414",
            "admission_term": "4041",
            "father_name": "غلامرضا",
            "faculty_group": "فنی و مهندسی",
            "level": "کارشناسی ناپیوسته",
            "major": "مهندسی نرم‌افزار",
        }
    }
    return render(request, "EducationSystem/pages/Loan.html", ctx)

def welcome(request):
    return render(request, "EducationSystem/pages/welcome.html")

def login_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        password = request.POST.get("password")

        # TODO:
        return redirect("dashboard")

    return render(request, "EducationSystem/pages/login.html")

# صفحه داشبورد
def dashboard_view(request):
    passed = 72     # مقدار دیفالت
    total = 144     # مقدار دیفالت
    percent = (passed / total) * 100
    return render(request, "EducationSystem/pages/dashboard.html", {
        "passed": passed,
        "total": total,
        "percent": percent,
    })

# صفحه پروفایل
def profile_view(request):
    return render(request, "EducationSystem/pages/profile.html")

# صفحه وام
def loan(request):
    # Sample data - should be replaced with actual student data from database
    ctx = {
        "student": {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "student_no": "123456789",
            "admission_term": "1402",
            "father_name": "نام پدر",
            "faculty_group": "دانشکده نمونه",
            "level": "کارشناسی",
            "major": "رشته نمونه",
        }
    }
    return render(request, "EducationSystem/pages/Loan.html", ctx)

#صفحه مدیریت دانشجویان
def student_management(request):
    return render(request, 'EducationSystem/pages/student_management.html')

#صفحه مدیریت دانشجویان
def course_management(request):
    return render(request, 'EducationSystem/pages/course_management.html')


# ============================================
# API Views
# ============================================

class CoursesProvidedAPIView(APIView):
    """
    لیست دروس ارائه شده به همراه فیلتر اسم درس
    
    GET /api/courses/provided
    
    Request Body Example:
    {
        "filter": {
            "course_name": "توسعه"
        }
    }
    
    Response Example:
    {
        "query": "توسعه",
        "results": [
            {
                "course_id": "123456",
                "name_course": "توسعه نرم افزار"
            }
        ]
    }
    """
    
    def get(self, request):
        """
        دریافت لیست دروس ارائه شده با قابلیت فیلتر بر اساس نام درس
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: JSON response containing query and results
        """
        try:
            # استخراج فیلتر از request body یا query params
            filter_data = request.data.get('filter', {}) if request.data else {}
            course_name_filter = filter_data.get('course_name', '')
            
            # اگر فیلتر در body نبود، از query params بخوان
            if not course_name_filter:
                course_name_filter = request.query_params.get('course_name', '')
            
            # شروع کوئری - فقط دروس فعال
            queryset = Course.objects.filter(is_active=True).order_by('name')
            
            # اعمال فیلتر نام درس (جستجوی partial)
            if course_name_filter:
                queryset = queryset.filter(name__icontains=course_name_filter)
            
            # ساخت لیست نتایج
            results = []
            for course in queryset:
                results.append({
                    "course_id": str(course.id),
                    "name_course": course.name
                })
            
            # ساخت response
            response_data = {
                "query": course_name_filter if course_name_filter else "",
                "results": results
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # مدیریت خطا
            return Response(
                {
                    "error": "خطا در دریافت لیست دروس",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )