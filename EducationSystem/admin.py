"""
پنل ادمین فارسی برای سیستم آموزشی
"""
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.db.models import Avg, Count, Q, F
from django.utils.safestring import mark_safe
from .models import (
    Country, Province, City, ContactType, ContactInfo,
    Student, Professor, Staff,
    College, FieldOfStudy, Specialization,
    Term, Course, CoursePrerequisite, CourseCorequisite,
    Room, Class, StudentClassRegistration, ProfessorCourseAssignment,
    ProfessorSurvey,
    AttendanceMethod, ClassAttendance,
    PaymentMethod, PaymentStatus, TuitionPayment
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
            student_ids = [s.id for s in queryset if s.gpa and s.gpa > 18]
            return queryset.filter(id__in=student_ids)
        elif self.value() == 'conditional':
            student_ids = [s.id for s in queryset if s.gpa and s.gpa < 12]
            return queryset.filter(id__in=student_ids)
        elif self.value() == 'normal':
            student_ids = [s.id for s in queryset if s.gpa and 12 <= s.gpa <= 18]
            return queryset.filter(id__in=student_ids)
        return queryset


# ============================================
# Inline Admin Classes
# ============================================

class ContactInfoInline(GenericTabularInline):
    """Inline برای نمایش اطلاعات تماس"""
    model = ContactInfo
    extra = 1
    fields = ('contact_type', 'value', 'is_primary')
    ct_field = 'content_type'
    ct_fk_field = 'object_id'


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


# ============================================
# Admin Classes
# ============================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """پنل ادمین برای دانشجویان"""
    list_display = (
        'student_number', 'full_name', 'field_of_study', 'academic_status',
        'email', 'gpa_display', 'credits_passed_display'
    )
    list_filter = (
        StudentGPAFilter,
        'academic_status',
        'field_of_study',
        'specialization',
        'gender',
        'marital_status',
    )
    search_fields = (
        'student_number', 'first_name', 'last_name', 'national_id', 'email'
    )
    readonly_fields = (
        'enrollment_date', 'created_at', 'updated_at',
        'gpa_display', 'credits_passed_display', 'credits_remaining_display'
    )
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_id', 'id_number',
                      'birth_date_shamsi', 'birth_place', 'gender', 'marital_status',
                      'military_status', 'address')
        }),
        ('اطلاعات دانشجویی', {
            'fields': ('student_number', 'email', 'field_of_study', 'specialization',
                      'enrollment_date', 'academic_status')
        }),
        ('وضعیت تحصیلی', {
            'fields': ('gpa_display', 'credits_passed_display', 'credits_remaining_display')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ContactInfoInline, StudentClassRegistrationInline]
    ordering = ['-enrollment_date', 'student_number']

    def gpa_display(self, obj):
        gpa = obj.gpa
        if gpa:
            color = 'green' if gpa >= 17 else 'orange' if gpa >= 12 else 'red'
            return format_html('<span style="color: {}; font-weight: bold;">{:.2f}</span>', color, gpa)
        return '-'
    gpa_display.short_description = 'معدل'

    def credits_passed_display(self, obj):
        credits = obj.total_credits_passed
        return f"{credits} واحد" if credits is not None else '-'
    credits_passed_display.short_description = 'واحدهای گذرانده'

    def credits_remaining_display(self, obj):
        credits = obj.total_credits_remaining
        return f"{credits} واحد" if credits is not None else '-'
    credits_remaining_display.short_description = 'واحدهای باقیمانده'


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor_code', 'full_name', 'contract_type', 'is_active')
    list_filter = ('contract_type', 'is_active', 'gender')
    search_fields = ('professor_code', 'first_name', 'last_name', 'national_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ContactInfoInline]


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'full_name', 'position', 'contract_type', 'is_active')
    list_filter = ('contract_type', 'is_active', 'gender')
    search_fields = ('employee_number', 'first_name', 'last_name', 'national_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ContactInfoInline]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province')
    list_filter = ('province',)
    search_fields = ('name',)


@admin.register(ContactType)
class ContactTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('person', 'contact_type', 'value', 'is_primary')
    list_filter = ('contact_type', 'is_primary')
    search_fields = ('value',)


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(FieldOfStudy)
class FieldOfStudyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'degree_level', 'total_credits', 'is_active')
    list_filter = ('college', 'degree_level', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'field_of_study', 'is_active')
    list_filter = ('field_of_study', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'start_date', 'end_date', 'is_current', 'is_registration_open')
    list_filter = ('is_current', 'is_registration_open')
    search_fields = ('name', 'code')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'field_of_study', 'credits', 'course_type', 'is_active')
    list_filter = ('field_of_study', 'course_type', 'is_active')
    search_fields = ('code', 'name')


@admin.register(CoursePrerequisite)
class CoursePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'prerequisite_course', 'is_mandatory')
    list_filter = ('is_mandatory',)
    search_fields = ('course__name', 'prerequisite_course__name')


@admin.register(CourseCorequisite)
class CourseCorequisiteAdmin(admin.ModelAdmin):
    list_display = ('course', 'corequisite_course', 'is_mandatory')
    list_filter = ('is_mandatory',)
    search_fields = ('course__name', 'corequisite_course__name')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'room_type', 'capacity', 'building', 'is_active')
    list_filter = ('room_type', 'building', 'is_active')
    search_fields = ('code', 'name')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_code', 'course', 'term', 'day_of_week', 'start_time', 'capacity', 'is_active')
    list_filter = ('term', 'day_of_week', 'is_active')
    search_fields = ('class_code', 'course__name')


@admin.register(StudentClassRegistration)
class StudentClassRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_course', 'grade', 'status', 'registration_date')
    list_filter = ('status', 'registration_date')
    search_fields = ('student__student_number', 'class_course__class_code')
    readonly_fields = ('registration_date',)


@admin.register(ProfessorCourseAssignment)
class ProfessorCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('professor', 'class_course', 'is_primary', 'assignment_date')
    list_filter = ('is_primary',)
    search_fields = ('professor__professor_code', 'class_course__class_code')
    readonly_fields = ('assignment_date',)


@admin.register(ProfessorSurvey)
class ProfessorSurveyAdmin(admin.ModelAdmin):
    list_display = ('student', 'professor', 'class_course', 'overall_rating', 'survey_date')
    list_filter = ('overall_rating',)
    search_fields = ('student__student_number', 'professor__professor_code')
    readonly_fields = ('survey_date',)


# ============================================
# Attendance & Payment Admins
# ============================================

@admin.register(AttendanceMethod)
class AttendanceMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ClassAttendance)
class ClassAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_course', 'attendance_time', 'attendance_method', 'is_approved_by_professor')
    list_filter = ('attendance_method', 'is_approved_by_professor', 'attendance_time')
    search_fields = ('student__student_number', 'class_course__class_code')
    readonly_fields = ('created_at',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TuitionPayment)
class TuitionPaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'payment_date', 'payment_method', 'payment_status', 'transaction_code')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('student__student_number', 'transaction_code')
    readonly_fields = ('payment_date', 'created_at', 'updated_at')


# تنظیمات پنل ادمین
admin.site.site_header = "پنل مدیریت سیستم آموزشی"
admin.site.site_title = "سیستم آموزشی"
admin.site.index_title = "پنل مدیریت"