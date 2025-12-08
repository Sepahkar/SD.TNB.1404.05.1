from django.shortcuts import redirect, render

# Create your views here.
def test(request):
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

#صفحه مدیریت دانشجویان
def student_management(request):
    return render(request, 'EducationSystem/pages/student_management.html')

#صفحه مدیریت دروس
def course_management(request):
    return render(request, 'EducationSystem/pages/course_management.html')

#صفحه انتخاب واحد
def course_selection(request):
    return render(request, 'EducationSystem/pages/course_selection.html')