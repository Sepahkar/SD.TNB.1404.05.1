"""
پنل ادمین فارسی برای سیستم آموزشی
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count, Q, F
from django.utils.safestring import mark_safe
from .models import (
    Country, Province, City, ContactType, ContactInfo,
    Student, Professor, Staff,
    College, FieldOfStudy, Specialization,
    Term, Course, CoursePrerequisite, CourseCorequisite,
    Room, Class, StudentClassRegistration, ProfessorCourseAssignment,
    ProfessorSurvey
)
import jdatetime


# ============================================
# Custom Admin Filters
# ============================================

class StudentGPAFilter(admin.SimpleListFilter):
    """فیلتر بر اساس معدل دانشجو"""
    title = 'وضعیت تحصیلی'
    parameter_name = 'gpa_status'

    def lookups(self, request, model_admin):
        return (
            ('excellent', 'دانشجویان ممتاز (معدل بالای 18)'),
            ('conditional', 'دانشجویان مشروطی (معدل کمتر از 12)'),
            ('normal', 'دانشجویان عادی (معدل بین 12 تا 18)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'excellent':
            # دانشجویان با معدل بالای 18
            student_ids = []
            for student in queryset:
                gpa = student.gpa
                if gpa and gpa > 18:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        elif self.value() == 'conditional':
            # دانشجویان با معدل کمتر از 12
            student_ids = []
            for student in queryset:
                gpa = student.gpa
                if gpa and gpa < 12:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        elif self.value() == 'normal':
            # دانشجویان با معدل بین 12 تا 18
            student_ids = []
            for student in queryset:
                gpa = student.gpa
                if gpa and 12 <= gpa <= 18:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        return queryset


class StudentGraduationFilter(admin.SimpleListFilter):
    """فیلتر بر اساس وضعیت فارغ‌التحصیلی"""
    title = 'وضعیت فارغ‌التحصیلی'
    parameter_name = 'graduation_status'

    def lookups(self, request, model_admin):
        return (
            ('graduated', 'دانشجویان فارغ‌التحصیل (واحدهای پاس‌شده ≥ 140)'),
            ('studying', 'دانشجویان در حال تحصیل'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'graduated':
            student_ids = []
            for student in queryset:
                credits = student.total_credits_passed
                if credits and credits >= 140:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        elif self.value() == 'studying':
            student_ids = []
            for student in queryset:
                credits = student.total_credits_passed
                if not credits or credits < 140:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        return queryset


class StudentTermFilter(admin.SimpleListFilter):
    """فیلتر بر اساس ترم دانشجو"""
    title = 'وضعیت ترم'
    parameter_name = 'term_status'

    def lookups(self, request, model_admin):
        return (
            ('first', 'دانشجویان ترم اول'),
            ('last', 'دانشجویان ترم آخر'),
            ('middle', 'دانشجویان در حال تحصیل (نه ترم اول و نه ترم آخر)'),
        )

    def queryset(self, request, queryset):
        # این فیلتر نیاز به محاسبه دارد - ساده‌سازی شده
        if self.value() == 'first':
            # دانشجویانی که فقط در ترم اول ثبت‌نام کرده‌اند
            return queryset.filter(is_active=True)
        elif self.value() == 'last':
            # دانشجویانی که نزدیک به فارغ‌التحصیلی هستند
            student_ids = []
            for student in queryset:
                credits = student.total_credits_passed
                if credits and credits >= 120:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        elif self.value() == 'middle':
            # دانشجویانی که نه ترم اول هستند و نه آخر
            student_ids = []
            for student in queryset:
                credits = student.total_credits_passed
                if credits and 20 < credits < 120:
                    student_ids.append(student.id)
            return queryset.filter(id__in=student_ids)
        return queryset


class StudentEnrollmentYearFilter(admin.SimpleListFilter):
    """فیلتر بر اساس سال ورود"""
    title = 'سال ورود'
    parameter_name = 'enrollment_year'

    def lookups(self, request, model_admin):
        years = Student.objects.values_list('enrollment_date', flat=True).distinct()
        year_list = []
        for date_str in years:
            if date_str:
                year = date_str.split('/')[0]
                if year not in [y[0] for y in year_list]:
                    year_list.append((year, f'سال {year}'))
        return sorted(year_list, reverse=True)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(enrollment_date__startswith=self.value())
        return queryset


class ProfessorTeachingExperienceFilter(admin.SimpleListFilter):
    """فیلتر بر اساس سابقه تدریس"""
    title = 'سابقه تدریس'
    parameter_name = 'teaching_experience'

    def lookups(self, request, model_admin):
        return (
            ('less_1', 'کمتر از 1 سال'),
            ('1_5', 'بین 1 تا 5 سال'),
            ('5_10', 'بین 5 تا 10 سال'),
            ('more_10', 'بیشتر از 10 سال'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'less_1':
            professor_ids = []
            for prof in queryset:
                exp = prof.teaching_experience_years
                if exp and exp < 1:
                    professor_ids.append(prof.id)
            return queryset.filter(id__in=professor_ids)
        elif self.value() == '1_5':
            professor_ids = []
            for prof in queryset:
                exp = prof.teaching_experience_years
                if exp and 1 <= exp < 5:
                    professor_ids.append(prof.id)
            return queryset.filter(id__in=professor_ids)
        elif self.value() == '5_10':
            professor_ids = []
            for prof in queryset:
                exp = prof.teaching_experience_years
                if exp and 5 <= exp < 10:
                    professor_ids.append(prof.id)
            return queryset.filter(id__in=professor_ids)
        elif self.value() == 'more_10':
            professor_ids = []
            for prof in queryset:
                exp = prof.teaching_experience_years
                if exp and exp >= 10:
                    professor_ids.append(prof.id)
            return queryset.filter(id__in=professor_ids)
        return queryset


# ============================================
# Inline Admin Classes
# ============================================

class StudentClassRegistrationInline(admin.TabularInline):
    """Inline برای نمایش ثبت‌نام‌های دانشجو"""
    model = StudentClassRegistration
    extra = 0
    readonly_fields = ('registration_date', 'course_name', 'term_name', 'grade_display')
    fields = ('class_course', 'course_name', 'term_name', 'grade_display', 'status', 'registration_date')
    can_delete = False
    
    def course_name(self, obj):
        if obj.class_course:
            return obj.class_course.course.name
        return '-'
    course_name.short_description = 'نام درس'
    
    def term_name(self, obj):
        if obj.class_course:
            return obj.class_course.term.name
        return '-'
    term_name.short_description = 'ترم'
    
    def grade_display(self, obj):
        if obj.grade is not None:
            return f"{obj.grade:.2f}"
        return '-'
    grade_display.short_description = 'نمره'


class ProfessorCourseAssignmentInline(admin.TabularInline):
    """Inline برای نمایش کلاس‌های تدریس‌شده استاد"""
    model = ProfessorCourseAssignment
    extra = 0
    readonly_fields = ('assignment_date', 'course_name', 'term_name', 'student_count', 'average_grade')
    fields = ('class_course', 'course_name', 'term_name', 'student_count', 'average_grade', 'is_primary', 'assignment_date')
    can_delete = False
    
    def course_name(self, obj):
        if obj.class_course:
            return obj.class_course.course.name
        return '-'
    course_name.short_description = 'نام درس'
    
    def term_name(self, obj):
        if obj.class_course:
            return obj.class_course.term.name
        return '-'
    term_name.short_description = 'ترم'
    
    def student_count(self, obj):
        if obj.class_course:
            return obj.class_course.student_registrations.count()
        return 0
    student_count.short_description = 'تعداد دانشجو'
    
    def average_grade(self, obj):
        if obj.class_course:
            grades = obj.class_course.student_registrations.filter(grade__isnull=False).values_list('grade', flat=True)
            if grades:
                avg = sum(float(g) for g in grades) / len(grades)
                return f"{avg:.2f}"
        return '-'
    average_grade.short_description = 'میانگین نمره'


class CourseInline(admin.TabularInline):
    """Inline برای نمایش دروس مرتبط"""
    model = Course
    extra = 0
    readonly_fields = ('course_code', 'course_name', 'credits_display')
    fields = ('course_code', 'course_name', 'credits_display', 'course_type', 'is_active')
    can_delete = False
    
    def course_code(self, obj):
        return obj.code
    course_code.short_description = 'کد درس'
    
    def course_name(self, obj):
        return obj.name
    course_name.short_description = 'نام درس'
    
    def credits_display(self, obj):
        return obj.credits
    credits_display.short_description = 'واحد'


class StudentInline(admin.TabularInline):
    """Inline برای نمایش دانشجویان"""
    model = Student
    extra = 0
    readonly_fields = ('student_number_display', 'full_name_display')
    fields = ('student_number_display', 'full_name_display', 'is_active')
    can_delete = False
    
    def student_number_display(self, obj):
        return obj.student_number
    student_number_display.short_description = 'شماره دانشجویی'
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'نام کامل'


class ClassInline(admin.TabularInline):
    """Inline برای نمایش کلاس‌ها"""
    model = Class
    extra = 0
    readonly_fields = ('class_code_display', 'term_name', 'professor_name', 'student_count')
    fields = ('class_code_display', 'term_name', 'day_of_week', 'start_time', 'end_time', 'professor_name', 'student_count', 'capacity')
    can_delete = False
    
    def class_code_display(self, obj):
        return obj.class_code
    class_code_display.short_description = 'کد کلاس'
    
    def term_name(self, obj):
        return obj.term.name
    term_name.short_description = 'ترم'
    
    def professor_name(self, obj):
        assignment = obj.professor_assignments.filter(is_primary=True).first()
        if assignment:
            return assignment.professor.full_name
        return '-'
    professor_name.short_description = 'استاد'
    
    def student_count(self, obj):
        return obj.student_registrations.count()
    student_count.short_description = 'تعداد دانشجو'


class CoursePrerequisiteInline(admin.TabularInline):
    """Inline برای نمایش پیش‌نیازها"""
    model = CoursePrerequisite
    fk_name = 'course'
    extra = 0
    readonly_fields = ('prerequisite_name',)
    fields = ('prerequisite_course', 'prerequisite_name', 'is_mandatory')
    
    def prerequisite_name(self, obj):
        return obj.prerequisite_course.name
    prerequisite_name.short_description = 'نام پیش‌نیاز'


class CourseCorequisiteInline(admin.TabularInline):
    """Inline برای نمایش هم‌نیازها"""
    model = CourseCorequisite
    fk_name = 'course'
    extra = 0
    readonly_fields = ('corequisite_name',)
    fields = ('corequisite_course', 'corequisite_name', 'is_mandatory')
    
    def corequisite_name(self, obj):
        return obj.corequisite_course.name
    corequisite_name.short_description = 'نام هم‌نیاز'


class ClassStudentInline(admin.TabularInline):
    """Inline برای نمایش دانشجویان کلاس"""
    model = StudentClassRegistration
    extra = 0
    readonly_fields = ('student_number', 'student_name', 'grade_display')
    fields = ('student', 'student_number', 'student_name', 'grade_display', 'status')
    can_delete = False
    
    def student_number(self, obj):
        return obj.student.student_number
    student_number.short_description = 'شماره دانشجویی'
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'نام دانشجو'
    
    def grade_display(self, obj):
        if obj.grade is not None:
            return f"{obj.grade:.2f}"
        return '-'
    grade_display.short_description = 'نمره'


# ============================================
# Admin Classes
# ============================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """پنل ادمین برای دانشجویان"""
    list_display = (
        'student_number', 'full_name', 'field_of_study', 'specialization',
        'enrollment_year', 'age_display', 'gpa_display', 'credits_passed_display',
        'credits_remaining_display', 'graduation_status_display', 'is_active'
    )
    list_filter = (
        StudentGPAFilter,
        StudentGraduationFilter,
        StudentTermFilter,
        StudentEnrollmentYearFilter,
        'field_of_study',
        'specialization',
        'is_active',
        'gender',
        'marital_status',
    )
    search_fields = (
        'student_number', 'first_name', 'last_name', 'national_id',
        'field_of_study__name', 'specialization__name'
    )
    readonly_fields = (
        'student_number', 'national_id', 'id_number', 'age_display',
        'gpa_display', 'credits_passed_display', 'credits_remaining_display',
        'graduation_status_display', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_id', 'id_number',
                      'birth_date_shamsi', 'birth_place', 'gender', 'marital_status',
                      'military_status', 'address', 'age_display')
        }),
        ('اطلاعات دانشجویی', {
            'fields': ('student_number', 'field_of_study', 'specialization',
                      'enrollment_date', 'is_active')
        }),
        ('وضعیت تحصیلی', {
            'fields': ('gpa_display', 'credits_passed_display', 'credits_remaining_display',
                      'graduation_status_display')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [StudentClassRegistrationInline]
    ordering = ['-enrollment_date', 'student_number']
    
    def enrollment_year(self, obj):
        """سال ورود"""
        if obj.enrollment_date:
            return obj.enrollment_date.split('/')[0]
        return '-'
    enrollment_year.short_description = 'سال ورود'
    enrollment_year.admin_order_field = 'enrollment_date'
    
    def age_display(self, obj):
        """نمایش سن"""
        age = obj.age
        if age:
            return f"{age} سال"
        return '-'
    age_display.short_description = 'سن'
    
    def gpa_display(self, obj):
        """نمایش معدل"""
        gpa = obj.gpa
        if gpa:
            color = 'green' if gpa >= 17 else 'orange' if gpa >= 12 else 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{:.2f}</span>', color, gpa)
        return '-'
    gpa_display.short_description = 'معدل'
    
    def credits_passed_display(self, obj):
        """نمایش واحدهای گذرانده"""
        credits = obj.total_credits_passed
        if credits is not None:
            return f"{credits} واحد"
        return '-'
    credits_passed_display.short_description = 'واحدهای گذرانده'
    
    def credits_remaining_display(self, obj):
        """نمایش واحدهای باقیمانده"""
        credits = obj.total_credits_remaining
        if credits is not None:
            return f"{credits} واحد"
        return '-'
    credits_remaining_display.short_description = 'واحدهای باقیمانده'
    
    def graduation_status_display(self, obj):
        """وضعیت فارغ‌التحصیلی"""
        credits = obj.total_credits_passed
        if credits and credits >= 140:
            return format_html('<span style="color: green; font-weight: bold;">فارغ‌التحصیل</span>')
        elif credits:
            return format_html('<span style="color: blue;">در حال تحصیل ({}/140)</span>', credits)
        return format_html('<span style="color: gray;">بدون واحد</span>')
    graduation_status_display.short_description = 'وضعیت فارغ‌التحصیلی'


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    """پنل ادمین برای اساتید"""
    list_display = (
        'professor_code', 'full_name', 'contract_type', 'teaching_experience_display',
        'current_term_courses_display', 'total_students_display', 'average_grade_display', 'is_active'
    )
    list_filter = (
        ProfessorTeachingExperienceFilter,
        'contract_type',
        'is_active',
        'gender',
    )
    search_fields = (
        'professor_code', 'first_name', 'last_name', 'national_id',
        'employee_number', 'expertise'
    )
    readonly_fields = (
        'professor_code', 'national_id', 'teaching_experience_display',
        'current_term_courses_display', 'total_students_display',
        'average_grade_display', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_id', 'id_number',
                      'birth_date_shamsi', 'birth_place', 'gender', 'marital_status',
                      'military_status', 'address')
        }),
        ('اطلاعات استادی', {
            'fields': ('professor_code', 'employee_number', 'contract_type',
                      'hire_date', 'expertise', 'is_active')
        }),
        ('آمار تدریس', {
            'fields': ('teaching_experience_display', 'current_term_courses_display',
                      'total_students_display', 'average_grade_display')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ProfessorCourseAssignmentInline]
    ordering = ['professor_code']
    
    def teaching_experience_display(self, obj):
        """نمایش سابقه تدریس"""
        exp = obj.teaching_experience_years
        if exp:
            return f"{exp} سال"
        return '-'
    teaching_experience_display.short_description = 'سابقه تدریس'
    
    def current_term_courses_display(self, obj):
        """نمایش تعداد درس‌های ترم جاری"""
        count = obj.current_term_courses_count
        return f"{count} درس"
    current_term_courses_display.short_description = 'درس‌های ترم جاری'
    
    def total_students_display(self, obj):
        """تعداد کل دانشجویان تدریس‌شده"""
        total = 0
        for assignment in obj.course_assignments.all():
            total += assignment.class_course.student_registrations.count()
        return f"{total} دانشجو"
    total_students_display.short_description = 'کل دانشجویان'
    
    def average_grade_display(self, obj):
        """میانگین نمرات کلاس‌های تدریس‌شده"""
        all_grades = []
        for assignment in obj.course_assignments.all():
            grades = assignment.class_course.student_registrations.filter(
                grade__isnull=False
            ).values_list('grade', flat=True)
            all_grades.extend([float(g) for g in grades])
        
        if all_grades:
            avg = sum(all_grades) / len(all_grades)
            return f"{avg:.2f}"
        return '-'
    average_grade_display.short_description = 'میانگین نمرات'


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    """پنل ادمین برای دانشکده‌ها"""
    list_display = ('name', 'code', 'fields_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    readonly_fields = ('fields_count',)
    inlines = []
    ordering = ['name']
    
    def fields_count(self, obj):
        """تعداد رشته‌ها"""
        return obj.fields_of_study.count()
    fields_count.short_description = 'تعداد رشته‌ها'


@admin.register(FieldOfStudy)
class FieldOfStudyAdmin(admin.ModelAdmin):
    """پنل ادمین برای رشته‌های تحصیلی"""
    list_display = ('name', 'code', 'college', 'degree_level', 'total_credits', 'students_count', 'courses_count', 'is_active')
    list_filter = ('college', 'degree_level', 'is_active')
    search_fields = ('name', 'code', 'college__name')
    readonly_fields = ('students_count', 'courses_count')
    inlines = [CourseInline, StudentInline]
    ordering = ['college', 'name']
    
    def students_count(self, obj):
        """تعداد دانشجویان"""
        return obj.students.count()
    students_count.short_description = 'تعداد دانشجویان'
    
    def courses_count(self, obj):
        """تعداد دروس"""
        return obj.courses.count()
    courses_count.short_description = 'تعداد دروس'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """پنل ادمین برای دروس"""
    list_display = ('code', 'name', 'field_of_study', 'credits', 'course_type', 'classes_count', 'is_active')
    list_filter = ('field_of_study', 'course_type', 'is_active')
    search_fields = ('name', 'code', 'field_of_study__name')
    readonly_fields = ('classes_count', 'prerequisites_count', 'corequisites_count')
    inlines = [CoursePrerequisiteInline, CourseCorequisiteInline, ClassInline]
    ordering = ['field_of_study', 'code']
    
    def classes_count(self, obj):
        """تعداد کلاس‌ها"""
        return obj.classes.count()
    classes_count.short_description = 'تعداد کلاس‌ها'
    
    def prerequisites_count(self, obj):
        """تعداد پیش‌نیازها"""
        return obj.prerequisites.count()
    prerequisites_count.short_description = 'تعداد پیش‌نیازها'
    
    def corequisites_count(self, obj):
        """تعداد هم‌نیازها"""
        return obj.corequisites.count()
    corequisites_count.short_description = 'تعداد هم‌نیازها'


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """پنل ادمین برای کلاس‌ها"""
    list_display = (
        'class_code', 'course', 'term', 'day_of_week', 'time_display',
        'professor_display', 'student_count', 'capacity', 'remaining_capacity_display', 'is_active'
    )
    list_filter = ('term', 'course__field_of_study', 'day_of_week', 'is_active', 'room')
    search_fields = ('class_code', 'course__name', 'term__name', 'room__name')
    readonly_fields = ('student_count', 'remaining_capacity_display', 'professor_display')
    inlines = [ClassStudentInline]
    ordering = ['-term', 'course', 'class_code']
    
    def time_display(self, obj):
        """نمایش زمان کلاس"""
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_display.short_description = 'زمان'
    
    def professor_display(self, obj):
        """نمایش استاد"""
        assignment = obj.professor_assignments.filter(is_primary=True).first()
        if assignment:
            return assignment.professor.full_name
        return '-'
    professor_display.short_description = 'استاد'
    
    def student_count(self, obj):
        """تعداد دانشجویان ثبت‌نام شده"""
        return obj.student_registrations.count()
    student_count.short_description = 'تعداد دانشجو'
    
    def remaining_capacity_display(self, obj):
        """ظرفیت باقیمانده"""
        remaining = obj.remaining_capacity
        color = 'green' if remaining > 10 else 'orange' if remaining > 0 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, remaining)
    remaining_capacity_display.short_description = 'ظرفیت باقیمانده'


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """پنل ادمین برای ترم‌ها"""
    list_display = ('name', 'code', 'start_date', 'end_date', 'classes_count', 'is_current', 'is_registration_open')
    list_filter = ('is_current', 'is_registration_open')
    search_fields = ('name', 'code')
    readonly_fields = ('classes_count',)
    ordering = ['-code']
    
    def classes_count(self, obj):
        """تعداد کلاس‌ها"""
        return obj.classes.count()
    classes_count.short_description = 'تعداد کلاس‌ها'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """پنل ادمین برای اتاق‌ها"""
    list_display = ('name', 'code', 'room_type', 'building', 'floor', 'capacity', 'classes_count', 'is_active')
    list_filter = ('room_type', 'building', 'is_active')
    search_fields = ('name', 'code', 'building')
    readonly_fields = ('classes_count',)
    ordering = ['building', 'name']
    
    def classes_count(self, obj):
        """تعداد کلاس‌ها"""
        return obj.classes.count()
    classes_count.short_description = 'تعداد کلاس‌ها'


# ثبت سایر مدل‌ها
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ['name']


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'cities_count')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')
    readonly_fields = ('cities_count',)
    ordering = ['country', 'name']
    
    def cities_count(self, obj):
        return obj.cities.count()
    cities_count.short_description = 'تعداد شهرها'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'country')
    list_filter = ('province', 'province__country')
    search_fields = ('name', 'province__name')
    ordering = ['province', 'name']
    
    def country(self, obj):
        return obj.province.country.name
    country.short_description = 'کشور'


@admin.register(ContactType)
class ContactTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('person', 'contact_type', 'value', 'is_primary')
    list_filter = ('contact_type', 'is_primary')
    search_fields = ('value',)
    ordering = ['-is_primary', 'contact_type']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'full_name', 'position', 'contract_type', 'is_active')
    list_filter = ('contract_type', 'is_active', 'gender')
    search_fields = ('employee_number', 'first_name', 'last_name', 'national_id')
    ordering = ['employee_number']


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'field_of_study', 'students_count', 'is_active')
    list_filter = ('field_of_study', 'is_active')
    search_fields = ('name', 'code', 'field_of_study__name')
    readonly_fields = ('students_count',)
    ordering = ['field_of_study', 'name']
    
    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'تعداد دانشجویان'


@admin.register(CoursePrerequisite)
class CoursePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'prerequisite_course', 'is_mandatory')
    list_filter = ('is_mandatory',)
    search_fields = ('course__name', 'prerequisite_course__name')
    ordering = ['course', 'prerequisite_course']


@admin.register(CourseCorequisite)
class CourseCorequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'corequisite_course', 'is_mandatory')
    list_filter = ('is_mandatory',)
    search_fields = ('course__name', 'corequisite_course__name')
    ordering = ['course', 'corequisite_course']


@admin.register(StudentClassRegistration)
class StudentClassRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_course', 'grade', 'status', 'registration_date')
    list_filter = ('status', 'class_course__term', 'class_course__course__field_of_study')
    search_fields = ('student__student_number', 'student__first_name', 'student__last_name', 'class_course__class_code')
    readonly_fields = ('registration_date',)
    ordering = ['-registration_date']


@admin.register(ProfessorCourseAssignment)
class ProfessorCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('professor', 'class_course', 'is_primary', 'assignment_date')
    list_filter = ('is_primary', 'class_course__term')
    search_fields = ('professor__professor_code', 'professor__first_name', 'class_course__class_code')
    readonly_fields = ('assignment_date',)
    ordering = ['-assignment_date']


@admin.register(ProfessorSurvey)
class ProfessorSurveyAdmin(admin.ModelAdmin):
    list_display = ('student', 'professor', 'class_course', 'overall_rating', 'average_rating_display', 'survey_date')
    list_filter = ('overall_rating', 'class_course__term')
    search_fields = ('student__student_number', 'professor__professor_code', 'professor__first_name')
    readonly_fields = ('average_rating_display', 'survey_date')
    ordering = ['-survey_date']
    
    def average_rating_display(self, obj):
        """نمایش میانگین امتیازات"""
        avg = obj.average_rating
        return f"{avg:.2f}"
    average_rating_display.short_description = 'میانگین امتیاز'


# تنظیمات پنل ادمین
admin.site.site_header = "پنل مدیریت سیستم آموزشی"
admin.site.site_title = "سیستم آموزشی"
admin.site.index_title = "پنل مدیریت"
