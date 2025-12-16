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

def course_registration(request):
    return

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


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import jwt
from .models import Class, Student, StudentClassRegistration

# این کلید برای رمزگشایی JWT استفاده می‌شود.
# باید در settings یا env قرار بگیرد، ولی فعلاً برای سادگی اینجاست.
SECRET_KEY = "mysecretkey"


# =====================================================================
#     API: پروفایل دانشجو (ورودی از توکن JWT)
# =====================================================================
@csrf_exempt
def student_basic_profile(request):
    try:
        # 1) گرفتن مقدار هدر Authorization از درخواست
        #   توکن JWT همیشه از سمت کلاینت در این هدر ارسال می‌شود.
        auth = request.headers.get("Authorization")
        if not auth:
            return JsonResponse({"error": "Token missing"}, status=401)

        # 2) حذف پیشوند Bearer از مقدار هدر
        #   چون مقدار هدر به صورت:
        #       "Bearer xxxxx.yyyyy.zzzzz"
        #   ارسال می‌شود و ما فقط خود توکن خام را نیاز داریم.
        token = auth.replace("Bearer ", "")

        # 3) باز کردن و اعتبارسنجی توکن JWT
        #   اگر توکن معتبر نباشد (منقضی یا دستکاری شده باشد) خطا می‌دهد.
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # 4) استخراج studentId از داخل توکن
        #   این همان اطلاعات هویتی کاربر است که موقع لاگین داخل توکن قرار داده‌ایم.
        studentId = payload.get("studentId")

        # 5) پیدا کردن دانشجو در دیتابیس با studentId استخراج‌شده از توکن
        student = Student.objects.get(studentId=studentId)

        # 6) ساخت خروجی واقعی برای پاسخ API
        #   در این مرحله داده‌ها از دیتابیس خوانده می‌شوند، نه مقدار ثابت.
        data = {
            "studentId": student.studentId,
            "fullName": student.fullName,
            "gender": student.gender,
        }
        return JsonResponse(data)

    except Student.DoesNotExist:
        # اگر studentId از توکن درست بود ولی در دیتابیس وجود نداشت
        return JsonResponse({"error": "Student not found"}, status=404)

    except Exception:
        # هرگونه خطای JWT مثل امضای نامعتبر، تاریخ انقضای گذشته، مقدار خراب، ...
        return JsonResponse({"error": "Invalid token"}, status=401)



# =====================================================================
#     API: انتخاب و ثبت یک درس برای دانشجو
# =====================================================================
@csrf_exempt
def api_course_registration(request):

    # ✅ اگر متد GET بود، لیست همه کلاس‌ها رو برمی‌گردونیم
    if request.method == "GET":
        classes = Class.objects.all()
        results = []
        for c in classes:
            results.append({
                "class_code": c.class_code,
                "course_room": c.room.code,
                "course_name": c.course.code,
                "class_term" : c.term.code,
                "capacity": c.capacity,
               # "registered_students": c.registered_students,
               # "is_available": c.registered_students < c.capacity
            })
        return JsonResponse({
            "status": "success",
            "results": results
        })

    # ✅ بقیه منطق برای متد POST (ثبت درس)
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST allowed"
        })

    try:
        body = json.loads(request.body)
        class_id = body.get("class_id")
    except:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON"
        })

    if not class_id:
        return JsonResponse({
            "status": "error",
            "message": "class_id is required"
        })

    try:
        target_class = Class.objects.get(class_id=class_id)
    except Class.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Class not found"
        })

    student = Student.objects.first()

    if StudentClassRegistration.objects.filter(student=student, _class=target_class).exists():
        return JsonResponse({
            "status": "error",
            "message": "Already registered"
        })

    if target_class.registered_students >= target_class.capacity:
        return JsonResponse({
            "status": "error",
            "message": "Class is full"
        })

    StudentClassRegistration.objects.create(
        student=student,
        _class=target_class,
        status="enrolled"
    )

    target_class.registered_students += 1
    target_class.save()

    return JsonResponse({
        "status": "success",
        "message": "درس با موفقیت انتخاب شد",
        "class_id": class_id
    })

