from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

# 1. تعریف مدل‌های داده (Pydantic Models)
# ----------------------------------------

# مدل برای ورودی احراز هویت (ورود)
class LoginRequest(BaseModel):
    studentid: str
    password: str

# مدل برای پاسخ احراز هویت
class AuthResponse(BaseModel):
    token: str # مثال: "JWT_TOKEN"

# مدل برای اطلاعات پایه دانشجو
class BasicProfileResponse(BaseModel):
    studentid: str
    fullName: str
    gender: str

# مدل برای جزئیات نمودار مقایسه در داشبورد
class ComparisonChart(BaseModel):
    sameEntranceAvg: float
    sameMajorAvg: float
    sameFacultyAvg: float
    universityAvg: float

# مدل برای پاسخ داشبورد
class DashboardResponse(BaseModel):
    passedUnits: int # مثال: 72
    totalUnits: int # مثال: 144
    gpa: float # مثال: 19.94
    gender: str # مثال: "Female"
    comparisonChart: ComparisonChart

# مدل برای پاسخ کامل پروفایل دانشجو
class FullProfileResponse(BaseModel):
    studentid: str # مثال: "402777321"
    first_name: str # مثال: "مهرشاد"
    last_name: str # مثال: "شاکری بنا"
    father_name: str # مثال: "حسن"
    national_code: str # مثال: "0025176447"
    entry_semester: str # مثال: "0202"
    major: str # مثال: "مهندسی نرم افزار"
    degree: str # مثال: "کارشناسی ناپیوسله"

# مدل برای اطلاعات یک درس
class Course(BaseModel):
    course_id: str # مثال: "123456"
    course_name: str # مثال: "توسعه نرم افزار"

# مدل برای فیلتر دروس ارائه شده (که در Response Example آمده است)
class CoursesProvidedFilter(BaseModel):
    course_name: Optional[str] = None # مثال: "توسعه"

# مدل برای پاسخ لیست دروس ارائه شده
class CoursesProvidedResponse(BaseModel):
    query: str # مثال: "توسعه"
    filter: CoursesProvidedFilter
    results: List[Course]

# مدل برای زمان‌بندی کلاس
class ClassTime(BaseModel):
    day: str # مثال: "سه شنبه"
    start: str # مثال: "10:00"
    end: str # مثال: "12:45"

# مدل برای جزئیات کامل کلاس
class ClassDetails(BaseModel):
    class_id: str # مثال: "cl_123"
    master_name: str # مثال: "محمد سپه کار"
    class_time: ClassTime
    class_location: str # مثال: "B403"
    exam_date: str # مثال: "1404/04/17"
    capacity: int # مثال: 40
    registred: int # مثال: 35
    is_available: bool # مثال: True

# مدل برای ورودی درخواست جزئیات کلاس‌ها
class CourseClassRequest(BaseModel):
    course_id: str # مثال: "123456"

# مدل برای پاسخ جزئیات کلاس‌ها
class CourseClassResponse(BaseModel):
    course_id: str
    course_name: str
    classes: List[ClassDetails]

# مدل برای درخواست انتخاب درس
class CourseRegistrationRequest(BaseModel):
    class_id: str # مثال: "cl_123"

# مدل برای پاسخ موفقیت‌آمیز (برای ثبت درس و انتخاب واحد)
class RegistrationSuccess(BaseModel):
    status: str = "success"
    message: str # مثال: "درس با موفقیت انتخاب شد"
    class_id: Optional[str] = None # فقط برای ثبت درس
    
# مدل برای جزئیات دروس در انتخاب واحد
class SemesterClass(BaseModel):
    course_id: str # مثال: "123456"
    class_id: str # مثال: "cl_123"

# مدل برای درخواست ثبت انتخاب واحد
class SemesterRegistrationRequest(BaseModel):
    semester: str # مثال: "0402"
    classes: List[SemesterClass]


# 2. تعریف برنامه FastAPI
# -------------------------

app = FastAPI(
    title="سامانه API دانشجویی",
    description="پیاده‌سازی Endpoints بر اساس مستندات API",
    version="1.0.0"
)

# 3. تعریف Endpointها (Routes)
# -----------------------------

@app.get("/", tags=["عمومی"])
async def read_root():
    """
    مسیر پایه برای تست سلامت سرور و راهنمایی.
    """
    return {
        "message": "به سرویس API دانشجویی خوش آمدید.",
        "docs_url": "/docs",
        "endpoints": "لیست کامل Endpoints در /docs موجود است."
    }

@app.post("/auth/login", response_model=AuthResponse, tags=["احراز هویت"])
async def login_user(request_body: LoginRequest):
    """
    ورود با نام کاربری و رمز عبور (POST /auth/login)
    """
    # ** TODO: منطق واقعی احراز هویت باید اینجا اضافه شود (مثلاً بررسی DB) **
    if request_body.studentid == "402777321" and request_body.password == "securepass":
        # در صورت موفقیت، یک توکن JWT فرضی برگردانده می‌شود.
        return {"token": "FAKE_JWT_TOKEN_FOR_AUTHENTICATED_USER"}
    
    # در صورت عدم موفقیت
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="نام کاربری یا رمز عبور اشتباه است.")

@app.get("/student/profile/basic", response_model=BasicProfileResponse, tags=["دانشجو"])
async def get_basic_profile():
    """
    اطلاعات اولیه دانشجو برای هدر (GET /student/profile/basic)
    """
    # ** TODO: منطق بازیابی اطلاعات پایه دانشجو (بر اساس توکن Auth) **
    return {
        "studentid": "402777321",
        "fullName": "مهرشاد شاکری بنا",
        "gender": "Female"
    }

@app.get("/student/dashboard", response_model=DashboardResponse, tags=["دانشجو"])
async def get_dashboard_info():
    """
    اطلاعات کامل داشبورد (GET /student/dashboard)
    """
    # ** TODO: منطق بازیابی داده‌های داشبورد **
    return {
        "passedUnits": 72,
        "totalUnits": 144,
        "gpa": 19.94,
        "gender": "Female",
        "comparisonChart": {
            "sameEntranceAvg": 10.0,
            "sameMajorAvg": 22.0,
            "sameFacultyAvg": 42.0,
            "universityAvg": 62.0
        }
    }

@app.get("/student/profile/full", response_model=FullProfileResponse, tags=["دانشجو"])
async def get_full_profile():
    """
    اطلاعات کامل دانشجو برای صفحه اصلی (GET /student/profile/full)
    """
    # ** TODO: منطق بازیابی اطلاعات کامل دانشجو **
    return {
        "studentid": "402777321",
        "first_name": "مهرشاد",
        "last_name": "شاکری بنا",
        "father_name": "حسن",
        "national_code": "0025176447",
        "entry_semester": "0202",
        "major": "مهندسی نرم افزار",
        "degree": "کارشناسی ناپیوسله"
    }

@app.get("/courses/provided", response_model=CoursesProvidedResponse, tags=["دروس"])
async def get_provided_courses(course_name: Optional[str] = None):
    """
    لیست دروس ارائه شده به همراه فیلتر اسم درس (GET /courses/provided)
    """
    # ** TODO: منطق فیلتر و بازیابی دروس ارائه شده از DB **
    
    query_text = f"فیلتر شده با: {course_name}" if course_name else "همه دروس"
    
    # نمونه داده فرضی
    all_courses = [
        {"course_id": "123456", "course_name": "توسعه نرم افزار"},
        {"course_id": "654321", "course_name": "سیستم‌های توزیع شده"},
        {"course_id": "987654", "course_name": "شبکه‌های کامپیوتری"},
    ]
    
    # اعمال فیلتر (اگر course_name در نام درس وجود داشته باشد)
    if course_name:
        results = [c for c in all_courses if course_name in c["course_name"]]
    else:
        results = all_courses
        
    return {
        "query": query_text,
        "filter": CoursesProvidedFilter(course_name=course_name),
        "results": results
    }

@app.post("/courses/class", response_model=CourseClassResponse, tags=["دروس"])
async def get_course_classes(request_body: CourseClassRequest):
    """
    اطلاعات کلاس‌های یک درس بر اساس شماره درس (POST /courses/class)
    """
    # ** TODO: منطق بازیابی کلاس‌های درس بر اساس course_id **
    if request_body.course_id == "123456":
        return {
            "course_id": "123456",
            "course_name": "توسعه نرم افزار",
            "classes": [
                {
                    "class_id": "cl_123",
                    "master_name": "محمد سپه کار",
                    "class_time": {"day": "سه شنبه", "start": "10:00", "end": "12:45"},
                    "class_location": "B403",
                    "exam_date": "1404/04/17",
                    "capacity": 40,
                    "registred": 35,
                    "is_available": True
                }
            ]
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درس مورد نظر یافت نشد.")

@app.post("/student/course_registration", response_model=RegistrationSuccess, tags=["انتخاب واحد"])
async def register_course(request_body: CourseRegistrationRequest):
    """
    انتخاب و ثبت درس (POST /student/course_registration)
    """
    # ** TODO: منطق بررسی ظرفیت، پیش‌نیاز، تداخل زمانی و ثبت درس **
    
    if request_body.class_id == "cl_123":
        return {
            "status": "success",
            "message": f"درس با موفقیت انتخاب شد: کلاس {request_body.class_id}",
            "class_id": request_body.class_id
        }
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ثبت درس ناموفق بود. (مثلاً ظرفیت تکمیل یا تداخل زمانی)")

@app.post("/student/semester_registration", response_model=RegistrationSuccess, tags=["انتخاب واحد"])
async def register_semester(request_body: SemesterRegistrationRequest):
    """
    ثبت نهایی انتخاب واحد (POST /student/semester_registration)
    """
    # ** TODO: منطق نهایی کردن و قفل کردن انتخاب واحد برای ترم مشخص **
    
    if request_body.semester and len(request_body.classes) > 0:
        return {
            "status": "success",
            "message": f"انتخاب واحد با موفقیت برای ترم {request_body.semester} انجام شد."
        }
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="درخواست انتخاب واحد ناقص است. (مثلاً درسی انتخاب نشده)")