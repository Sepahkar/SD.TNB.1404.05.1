"""
Django management command برای تولید داده‌های تستی سیستم آموزشی
"""
import random
import jdatetime
import sys
import io
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from EducationSystem.models import (
    Country, Province, City, ContactType, ContactInfo,
    Student, Professor, Staff,
    College, FieldOfStudy, Specialization,
    Term, Course, CoursePrerequisite, CourseCorequisite,
    Room, Class, StudentClassRegistration, ProfessorCourseAssignment,
    ProfessorSurvey
)
from datetime import time, timedelta

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class Command(BaseCommand):
    help = 'تولید داده‌های تستی برای سیستم آموزشی'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='پاک کردن داده‌های قبلی قبل از ایجاد داده‌های جدید',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('در حال پاک کردن داده‌های قبلی...'))
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('شروع تولید داده‌های تستی...'))
        
        try:
            with transaction.atomic():
                # ایجاد داده‌های مرجع
                self.create_reference_data()
                
                # ایجاد دانشکده‌ها و رشته‌ها
                colleges = self.create_colleges_and_fields()
                
                # ایجاد ترم‌ها
                terms = self.create_terms()
                
                # ایجاد دروس
                courses = self.create_courses(colleges)
                
                # ایجاد اتاق‌ها
                rooms = self.create_rooms()
                
                # ایجاد اساتید
                professors = self.create_professors()
                
                # ایجاد دانشجویان
                students = self.create_students(colleges)
                
                # ایجاد کلاس‌ها
                classes = self.create_classes(courses, terms, rooms, professors)
                
                # ایجاد ثبت‌نام‌ها
                self.create_registrations(students, classes, terms)
                
                # ایجاد اطلاعات تماس
                self.create_contact_info(students, professors)
                
                # ایجاد نظرسنجی‌ها
                self.create_surveys(students, professors, classes)
                
                self.stdout.write(self.style.SUCCESS('داده‌های تستی با موفقیت ایجاد شدند!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطا در ایجاد داده‌ها: {str(e)}'))
            raise

    def clear_data(self):
        """پاک کردن داده‌های قبلی"""
        ProfessorSurvey.objects.all().delete()
        StudentClassRegistration.objects.all().delete()
        ProfessorCourseAssignment.objects.all().delete()
        Class.objects.all().delete()
        CourseCorequisite.objects.all().delete()
        CoursePrerequisite.objects.all().delete()
        Course.objects.all().delete()
        Term.objects.all().delete()
        Room.objects.all().delete()
        Student.objects.all().delete()
        Professor.objects.all().delete()
        Staff.objects.all().delete()
        ContactInfo.objects.all().delete()
        Specialization.objects.all().delete()
        FieldOfStudy.objects.all().delete()
        College.objects.all().delete()
        City.objects.all().delete()
        Province.objects.all().delete()
        Country.objects.all().delete()
        ContactType.objects.all().delete()

    def generate_national_id(self):
        """تولید کد ملی معتبر با الگوریتم چک دیجیت"""
        while True:
            # تولید 9 رقم اول
            digits = [random.randint(0, 9) for _ in range(9)]
            
            # محاسبه چک دیجیت
            s = sum(digits[i] * (10 - i) for i in range(9)) % 11
            if s < 2:
                check = s
            else:
                check = 11 - s
            
            digits.append(check)
            national_id = ''.join(map(str, digits))
            
            # بررسی یکتایی (باید در دیتابیس بررسی شود اما برای تست ساده می‌کنیم)
            return national_id

    def generate_student_number(self, year, college_code, field_code, serial):
        """تولید شماره دانشجویی"""
        return f"{year}{college_code}{field_code}{serial:04d}"

    def create_reference_data(self):
        """ایجاد داده‌های مرجع (کشور، استان، شهر، نوع تماس)"""
        self.stdout.write('در حال ایجاد داده‌های مرجع...')
        
        # ایجاد کشور
        country, _ = Country.objects.get_or_create(
            name='ایران',
            defaults={'code': 'IRN'}
        )
        
        # لیست استان‌های ایران
        provinces_data = [
            'آذربایجان شرقی', 'آذربایجان غربی', 'اردبیل', 'اصفهان', 'البرز',
            'ایلام', 'بوشهر', 'تهران', 'چهارمحال و بختیاری', 'خراسان جنوبی',
            'خراسان رضوی', 'خراسان شمالی', 'خوزستان', 'زنجان', 'سمنان',
            'سیستان و بلوچستان', 'فارس', 'قزوین', 'قم', 'کردستان',
            'کرمان', 'کرمانشاه', 'کهگیلویه و بویراحمد', 'گلستان', 'گیلان',
            'لرستان', 'مازندران', 'مرکزی', 'هرمزگان', 'همدان', 'یزد'
        ]
        
        provinces = {}
        for prov_name in provinces_data:
            province, _ = Province.objects.get_or_create(
                name=prov_name,
                defaults={'country': country}
            )
            provinces[prov_name] = province
        
        # لیست شهرهای اصلی ایران
        cities_data = {
            'تهران': ['تهران', 'شهریار', 'ورامین', 'اسلامشهر', 'کرج'],
            'اصفهان': ['اصفهان', 'کاشان', 'نجف‌آباد', 'خمینی‌شهر'],
            'فارس': ['شیراز', 'مرودشت', 'جهرم'],
            'خراسان رضوی': ['مشهد', 'نیشابور', 'سبزوار'],
            'آذربایجان شرقی': ['تبریز', 'مراغه'],
            'گلستان': ['گرگان', 'گنبد کاووس'],
            'مازندران': ['ساری', 'بابل', 'آمل'],
            'گیلان': ['رشت', 'انزلی'],
            'خوزستان': ['اهواز', 'آبادان', 'دزفول'],
            'کرمان': ['کرمان', 'رفسنجان'],
            'یزد': ['یزد'],
            'مرکزی': ['اراک'],
            'همدان': ['همدان'],
            'لرستان': ['خرم‌آباد'],
            'کردستان': ['سنندج'],
            'آذربایجان غربی': ['ارومیه'],
            'کرمانشاه': ['کرمانشاه'],
            'قم': ['قم'],
            'البرز': ['کرج', 'هشتگرد'],
        }
        
        for prov_name, city_names in cities_data.items():
            if prov_name in provinces:
                for city_name in city_names:
                    City.objects.get_or_create(
                        name=city_name,
                        defaults={'province': provinces[prov_name]}
                    )
        
        # ایجاد انواع تماس
        contact_types = ['تلفن ثابت', 'موبایل', 'ایمیل', 'فکس']
        for ct_name in contact_types:
            ContactType.objects.get_or_create(name=ct_name)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(provinces)} استان و {City.objects.count()} شهر ایجاد شد'))

    def create_colleges_and_fields(self):
        """ایجاد دانشکده‌ها و رشته‌ها"""
        self.stdout.write('در حال ایجاد دانشکده‌ها و رشته‌ها...')
        
        colleges_data = [
            {'name': 'دانشکده کامپیوتر', 'code': 'COMP'},
            {'name': 'دانشکده مدیریت', 'code': 'MGT'},
        ]
        
        colleges = {}
        for college_data in colleges_data:
            college, _ = College.objects.get_or_create(
                code=college_data['code'],
                defaults={'name': college_data['name']}
            )
            colleges[college_data['code']] = college
        
        # رشته‌های کامپیوتر
        comp_fields = [
            {'name': 'مهندسی نرم‌افزار', 'code': 'SW', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مهندسی هوش مصنوعی', 'code': 'AI', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مهندسی کامپیوتر - نرم‌افزار', 'code': 'CS-SW', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مهندسی کامپیوتر - سخت‌افزار', 'code': 'CS-HW', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'علوم کامپیوتر', 'code': 'CS', 'credits': 140, 'level': 'کارشناسی'},
        ]
        
        # رشته‌های مدیریت
        mgt_fields = [
            {'name': 'مدیریت بازرگانی', 'code': 'MBA', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مدیریت صنعتی', 'code': 'MIM', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مدیریت مالی', 'code': 'MF', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مدیریت دولتی', 'code': 'MPA', 'credits': 140, 'level': 'کارشناسی'},
            {'name': 'مدیریت فناوری اطلاعات', 'code': 'MIT', 'credits': 140, 'level': 'کارشناسی'},
        ]
        
        fields = {}
        for field_data in comp_fields:
            field, _ = FieldOfStudy.objects.get_or_create(
                code=field_data['code'],
                college=colleges['COMP'],
                defaults={
                    'name': field_data['name'],
                    'degree_level': field_data['level'],
                    'total_credits': field_data['credits']
                }
            )
            fields[field_data['code']] = field
            
            # ایجاد گرایش‌ها
            if field_data['code'] == 'SW':
                Specialization.objects.get_or_create(
                    code='SW-ENG',
                    field_of_study=field,
                    defaults={'name': 'مهندسی نرم‌افزار'}
                )
            elif field_data['code'] == 'AI':
                Specialization.objects.get_or_create(
                    code='AI-ML',
                    field_of_study=field,
                    defaults={'name': 'یادگیری ماشین'}
                )
        
        for field_data in mgt_fields:
            field, _ = FieldOfStudy.objects.get_or_create(
                code=field_data['code'],
                college=colleges['MGT'],
                defaults={
                    'name': field_data['name'],
                    'degree_level': field_data['level'],
                    'total_credits': field_data['credits']
                }
            )
            fields[field_data['code']] = field
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(colleges)} دانشکده و {len(fields)} رشته ایجاد شد'))
        return colleges

    def create_terms(self):
        """ایجاد ترم‌ها (از 1398 تا 1403)"""
        self.stdout.write('در حال ایجاد ترم‌ها...')
        
        terms = []
        for year in range(1398, 1404):
            # ترم پاییز
            fall_code = f"{year}1"
            fall_name = f"پاییز {year}"
            fall_term, _ = Term.objects.get_or_create(
                code=fall_code,
                defaults={
                    'name': fall_name,
                    'start_date': f"{year}/07/01",
                    'end_date': f"{year}/12/20",
                    'is_current': (year == 1403),
                    'is_registration_open': (year == 1403)
                }
            )
            terms.append(fall_term)
            
            # ترم بهار
            spring_code = f"{year}2"
            spring_name = f"بهار {year}"
            spring_term, _ = Term.objects.get_or_create(
                code=spring_code,
                defaults={
                    'name': spring_name,
                    'start_date': f"{year+1}/01/10",
                    'end_date': f"{year+1}/06/30",
                    'is_current': False,
                    'is_registration_open': False
                }
            )
            terms.append(spring_term)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(terms)} ترم ایجاد شد'))
        return terms

    def create_courses(self, colleges):
        """ایجاد دروس از سرفصل وزارت علوم"""
        self.stdout.write('در حال ایجاد دروس...')
        
        # دروس رشته نرم‌افزار
        sw_courses = [
            {'name': 'برنامه‌نویسی مقدماتی', 'code': 'SW101', 'credits': 3, 'type': 'اصلی'},
            {'name': 'برنامه‌نویسی پیشرفته', 'code': 'SW102', 'credits': 3, 'type': 'اصلی'},
            {'name': 'ساختمان داده', 'code': 'SW201', 'credits': 3, 'type': 'اصلی'},
            {'name': 'الگوریتم‌ها', 'code': 'SW202', 'credits': 3, 'type': 'اصلی'},
            {'name': 'طراحی الگوریتم', 'code': 'SW203', 'credits': 3, 'type': 'اصلی'},
            {'name': 'پایگاه داده', 'code': 'SW301', 'credits': 3, 'type': 'اصلی'},
            {'name': 'شبکه‌های کامپیوتری', 'code': 'SW302', 'credits': 3, 'type': 'اصلی'},
            {'name': 'سیستم‌عامل', 'code': 'SW303', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مهندسی نرم‌افزار', 'code': 'SW401', 'credits': 3, 'type': 'اصلی'},
            {'name': 'تحلیل و طراحی سیستم', 'code': 'SW402', 'credits': 3, 'type': 'اصلی'},
            {'name': 'معماری نرم‌افزار', 'code': 'SW403', 'credits': 3, 'type': 'اصلی'},
            {'name': 'تست نرم‌افزار', 'code': 'SW404', 'credits': 2, 'type': 'اصلی'},
            {'name': 'پروژه نرم‌افزار', 'code': 'SW405', 'credits': 3, 'type': 'اصلی'},
            {'name': 'زبان‌های برنامه‌نویسی', 'code': 'SW501', 'credits': 3, 'type': 'اصلی'},
            {'name': 'هوش مصنوعی', 'code': 'SW502', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'گرافیک کامپیوتری', 'code': 'SW503', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'امنیت اطلاعات', 'code': 'SW504', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'محاسبات موازی', 'code': 'SW505', 'credits': 3, 'type': 'اختیاری'},
        ]
        
        # دروس رشته هوش مصنوعی
        ai_courses = [
            {'name': 'مبانی هوش مصنوعی', 'code': 'AI101', 'credits': 3, 'type': 'اصلی'},
            {'name': 'یادگیری ماشین', 'code': 'AI201', 'credits': 3, 'type': 'اصلی'},
            {'name': 'شبکه‌های عصبی', 'code': 'AI202', 'credits': 3, 'type': 'اصلی'},
            {'name': 'پردازش زبان طبیعی', 'code': 'AI301', 'credits': 3, 'type': 'اصلی'},
            {'name': 'بینایی کامپیوتر', 'code': 'AI302', 'credits': 3, 'type': 'اصلی'},
            {'name': 'یادگیری عمیق', 'code': 'AI401', 'credits': 3, 'type': 'اصلی'},
            {'name': 'الگوریتم‌های ژنتیک', 'code': 'AI402', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'سیستم‌های خبره', 'code': 'AI403', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'رباتیک', 'code': 'AI404', 'credits': 3, 'type': 'اختیاری'},
        ]
        
        # دروس رشته مدیریت
        mgt_courses = [
            {'name': 'مبانی مدیریت', 'code': 'MGT101', 'credits': 3, 'type': 'اصلی'},
            {'name': 'اصول اقتصاد', 'code': 'MGT102', 'credits': 3, 'type': 'اصلی'},
            {'name': 'حسابداری مقدماتی', 'code': 'MGT201', 'credits': 3, 'type': 'اصلی'},
            {'name': 'بازاریابی', 'code': 'MGT202', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مدیریت منابع انسانی', 'code': 'MGT301', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مدیریت مالی', 'code': 'MGT302', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مدیریت استراتژیک', 'code': 'MGT401', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مدیریت عملیات', 'code': 'MGT402', 'credits': 3, 'type': 'اصلی'},
            {'name': 'رفتار سازمانی', 'code': 'MGT403', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مدیریت پروژه', 'code': 'MGT404', 'credits': 3, 'type': 'اصلی'},
            {'name': 'مدیریت کیفیت', 'code': 'MGT501', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'مدیریت تغییر', 'code': 'MGT502', 'credits': 3, 'type': 'اختیاری'},
            {'name': 'کارآفرینی', 'code': 'MGT503', 'credits': 3, 'type': 'اختیاری'},
        ]
        
        courses = []
        
        # ایجاد دروس نرم‌افزار
        sw_field = FieldOfStudy.objects.filter(code='SW').first()
        if sw_field:
            for course_data in sw_courses:
                course, _ = Course.objects.get_or_create(
                    code=course_data['code'],
                    field_of_study=sw_field,
                    defaults={
                        'name': course_data['name'],
                        'credits': course_data['credits'],
                        'course_type': course_data['type']
                    }
                )
                courses.append(course)
        
        # ایجاد دروس هوش مصنوعی
        ai_field = FieldOfStudy.objects.filter(code='AI').first()
        if ai_field:
            for course_data in ai_courses:
                course, _ = Course.objects.get_or_create(
                    code=course_data['code'],
                    field_of_study=ai_field,
                    defaults={
                        'name': course_data['name'],
                        'credits': int(course_data['credits']),
                        'course_type': course_data['type']
                    }
                )
                courses.append(course)
        
        # ایجاد دروس مدیریت - فقط برای اولین رشته مدیریت
        mgt_field = FieldOfStudy.objects.filter(college__code='MGT').first()
        if mgt_field:
            for course_data in mgt_courses:
                course, _ = Course.objects.get_or_create(
                    code=course_data['code'],
                    field_of_study=mgt_field,
                    defaults={
                        'name': course_data['name'],
                        'credits': course_data['credits'],
                        'course_type': course_data['type']
                    }
                )
                courses.append(course)
        
        # افزودن دروس بیشتر برای رسیدن به 50 درس
        # دروس عمومی و اختیاری بیشتر
        additional_courses = [
            {'name': 'ریاضی عمومی 1', 'code': 'MATH101', 'credits': 3, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'ریاضی عمومی 2', 'code': 'MATH102', 'credits': 3, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'معادلات دیفرانسیل', 'code': 'MATH201', 'credits': 3, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'احتمال و آمار', 'code': 'STAT201', 'credits': 3, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'فیزیک 1', 'code': 'PHY101', 'credits': 3, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'فیزیک 2', 'code': 'PHY102', 'credits': 3, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'زبان انگلیسی عمومی', 'code': 'ENG101', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'زبان انگلیسی تخصصی', 'code': 'ENG201', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'معارف اسلامی 1', 'code': 'REL101', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'معارف اسلامی 2', 'code': 'REL102', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'اندیشه اسلامی', 'code': 'REL201', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'انقلاب اسلامی', 'code': 'HIS101', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'تاریخ ایران', 'code': 'HIS201', 'credits': 2, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'ورزش 1', 'code': 'SPT101', 'credits': 1, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'ورزش 2', 'code': 'SPT102', 'credits': 1, 'type': 'عمومی', 'field_code': 'SW'},
            {'name': 'مدارهای منطقی', 'code': 'SW204', 'credits': 3, 'type': 'اصلی', 'field_code': 'SW'},
            {'name': 'معماری کامپیوتر', 'code': 'SW304', 'credits': 3, 'type': 'اصلی', 'field_code': 'SW'},
            {'name': 'کامپایلر', 'code': 'SW406', 'credits': 3, 'type': 'اصلی', 'field_code': 'SW'},
            {'name': 'برنامه‌نویسی وب', 'code': 'SW506', 'credits': 3, 'type': 'اختیاری', 'field_code': 'SW'},
            {'name': 'برنامه‌نویسی موبایل', 'code': 'SW507', 'credits': 3, 'type': 'اختیاری', 'field_code': 'SW'},
            {'name': 'مهندسی اینترنت', 'code': 'SW508', 'credits': 3, 'type': 'اختیاری', 'field_code': 'SW'},
            {'name': 'رایانش ابری', 'code': 'SW509', 'credits': 3, 'type': 'اختیاری', 'field_code': 'SW'},
        ]
        
        for course_data in additional_courses:
            field_code = course_data.pop('field_code')
            course_type = course_data.pop('type')
            field = FieldOfStudy.objects.filter(code=field_code).first()
            if field:
                course, _ = Course.objects.get_or_create(
                    code=course_data['code'],
                    field_of_study=field,
                    defaults={
                        'name': course_data['name'],
                        'credits': course_data['credits'],
                        'course_type': course_type
                    }
                )
                if course not in courses:
                    courses.append(course)
        
        # ایجاد پیش‌نیازها
        if sw_field:
            sw_courses_list = Course.objects.filter(field_of_study=sw_field)
            sw101 = sw_courses_list.filter(code='SW101').first()
            sw102 = sw_courses_list.filter(code='SW102').first()
            sw201 = sw_courses_list.filter(code='SW201').first()
            
            if sw101 and sw102:
                CoursePrerequisite.objects.get_or_create(
                    course=sw102,
                    prerequisite_course=sw101
                )
            if sw102 and sw201:
                CoursePrerequisite.objects.get_or_create(
                    course=sw201,
                    prerequisite_course=sw102
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(courses)} درس ایجاد شد'))
        return courses

    def create_rooms(self):
        """ایجاد اتاق‌ها"""
        self.stdout.write('در حال ایجاد اتاق‌ها...')
        
        rooms = []
        room_types = ['C', 'L', 'O', 'A']  # کلاس، آزمایشگاه، سمینار، آمفی‌تئاتر
        buildings = ['ساختمان A', 'ساختمان B', 'ساختمان C']
        
        for building in buildings:
            for floor in range(1, 5):
                for room_num in range(1, 6):
                    room_code = f"{building[:1]}{floor}{room_num:02d}"
                    room_type = random.choice(room_types)
                    capacity = random.choice([30, 40, 50, 60, 100, 150])
                    
                    room, _ = Room.objects.get_or_create(
                        code=room_code,
                        defaults={
                            'name': f'اتاق {room_num}',
                            'room_type': room_type,
                            'capacity': capacity,
                            'building': building,
                            'floor': floor
                        }
                    )
                    rooms.append(room)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(rooms)} اتاق ایجاد شد'))
        return rooms

    def create_professors(self):
        """ایجاد اساتید"""
        self.stdout.write('در حال ایجاد اساتید...')
        
        # لیست اسامی فارسی
        first_names_male = [
            'علی', 'محمد', 'حسن', 'حسین', 'رضا', 'احمد', 'مرتضی', 'مهدی',
            'امیر', 'سعید', 'کاظم', 'عباس', 'محمود', 'محسن', 'هادی', 'جواد'
        ]
        first_names_female = [
            'فاطمه', 'مریم', 'زهرا', 'عاطفه', 'سمیرا', 'نیلوفر', 'سارا',
            'نرگس', 'طاهره', 'معصومه', 'لیلا', 'مهسا', 'زینب', 'ریحانه'
        ]
        last_names = [
            'محمدی', 'احمدی', 'حسینی', 'رضایی', 'کریمی', 'موسوی', 'عباسی',
            'نوری', 'صادقی', 'جعفری', 'طاهری', 'کاظمی', 'مهدوی', 'زمانی',
            'رستمی', 'نظری', 'صالحی', 'رحیمی', 'ایزدی', 'فرهادی'
        ]
        
        professors = []
        contract_types = ['F', 'P', 'V']  # تمام وقت، پاره وقت، مهمان
        
        for i in range(20):
            # انتخاب جنسیت
            is_male = random.choice([True, False])
            first_name = random.choice(first_names_male if is_male else first_names_female)
            last_name = random.choice(last_names)
            
            # تولید کد ملی
            national_id = self.generate_national_id()
            while Professor.objects.filter(national_id=national_id).exists():
                national_id = self.generate_national_id()
            
            # تولید شماره شناسنامه
            id_number = str(random.randint(100000, 999999))
            while Professor.objects.filter(id_number=id_number).exists():
                id_number = str(random.randint(100000, 999999))
            
            # تولید تاریخ تولد (بین 1330 تا 1360)
            birth_year = random.randint(1330, 1360)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_date = f"{birth_year}/{birth_month:02d}/{birth_day:02d}"
            
            # انتخاب شهر
            city = City.objects.order_by('?').first()
            
            # تولید کد استادی
            professor_code = f"P{1000 + i:04d}"
            while Professor.objects.filter(professor_code=professor_code).exists():
                professor_code = f"P{1000 + i:04d}"
            
            # تاریخ استخدام (بین 1380 تا 1400)
            hire_year = random.randint(1380, 1400)
            hire_month = random.randint(1, 12)
            hire_date = f"{hire_year}/{hire_month:02d}/01"
            
            professor = Professor.objects.create(
                first_name=first_name,
                last_name=last_name,
                national_id=national_id,
                id_number=id_number,
                birth_date_shamsi=birth_date,
                birth_place=city,
                gender='M' if is_male else 'F',
                marital_status=random.choice(['S', 'M', 'D', 'W']),
                military_status=random.choice(['E', 'C', 'D', 'N']) if is_male else None,
                address=f"تهران، خیابان ولیعصر، پلاک {random.randint(1, 500)}",
                professor_code=professor_code,
                employee_number=f"EMP{1000 + i:04d}",
                contract_type=random.choice(contract_types),
                hire_date=hire_date,
                expertise=f"تخصص در حوزه {random.choice(['نرم‌افزار', 'هوش مصنوعی', 'شبکه', 'پایگاه داده'])}",
                is_active=True
            )
            professors.append(professor)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(professors)} استاد ایجاد شد'))
        return professors

    def create_students(self, colleges):
        """ایجاد دانشجویان"""
        self.stdout.write('در حال ایجاد دانشجویان...')
        
        first_names_male = [
            'علی', 'محمد', 'حسن', 'حسین', 'رضا', 'احمد', 'مرتضی', 'مهدی',
            'امیر', 'سعید', 'کاظم', 'عباس', 'محمود', 'محسن', 'هادی', 'جواد',
            'امیرحسین', 'محمدعلی', 'حسینعلی', 'علی‌رضا', 'محمدرضا', 'امیرمحمد'
        ]
        first_names_female = [
            'فاطمه', 'مریم', 'زهرا', 'عاطفه', 'سمیرا', 'نیلوفر', 'سارا',
            'نرگس', 'طاهره', 'معصومه', 'لیلا', 'مهسا', 'زینب', 'ریحانه',
            'فاطمه‌زهرا', 'مریم‌سادات', 'زهراسادات', 'معصومه‌سادات'
        ]
        last_names = [
            'محمدی', 'احمدی', 'حسینی', 'رضایی', 'کریمی', 'موسوی', 'عباسی',
            'نوری', 'صادقی', 'جعفری', 'طاهری', 'کاظمی', 'مهدوی', 'زمانی',
            'رستمی', 'نظری', 'صالحی', 'رحیمی', 'ایزدی', 'فرهادی', 'جعفریان',
            'محمدزاده', 'احمدزاده', 'حسین‌زاده', 'رضازاده'
        ]
        
        students = []
        fields = FieldOfStudy.objects.all()
        
        # توزیع دانشجویان بین رشته‌ها
        field_distribution = {}
        for field in fields:
            field_distribution[field.id] = 500 // fields.count()
        remaining = 500 % fields.count()
        for i, field_id in enumerate(field_distribution.keys()):
            if i < remaining:
                field_distribution[field_id] += 1
        
        # شمارنده جداگانه برای هر رشته
        field_counters = {}
        for field in fields:
            field_counters[field.id] = 1
        
        for field in fields:
            count = field_distribution[field.id]
            college = field.college
            specializations = Specialization.objects.filter(field_of_study=field)
            
            for i in range(count):
                is_male = random.choice([True, False])
                first_name = random.choice(first_names_male if is_male else first_names_female)
                last_name = random.choice(last_names)
                
                # تولید کد ملی
                national_id = self.generate_national_id()
                max_attempts = 100
                attempts = 0
                while (Student.objects.filter(national_id=national_id).exists() or 
                       Professor.objects.filter(national_id=national_id).exists() or
                       Staff.objects.filter(national_id=national_id).exists()) and attempts < max_attempts:
                    national_id = self.generate_national_id()
                    attempts += 1
                
                if attempts >= max_attempts:
                    self.stdout.write(self.style.WARNING(f'نمی‌توان کد ملی یکتا تولید کرد برای {first_name} {last_name}'))
                    continue
                
                # تولید شماره شناسنامه
                id_number = str(random.randint(100000, 999999))
                max_attempts = 100
                attempts = 0
                while (Student.objects.filter(id_number=id_number).exists() or
                       Professor.objects.filter(id_number=id_number).exists() or
                       Staff.objects.filter(id_number=id_number).exists()) and attempts < max_attempts:
                    id_number = str(random.randint(100000, 999999))
                    attempts += 1
                
                if attempts >= max_attempts:
                    self.stdout.write(self.style.WARNING(f'نمی‌توان شماره شناسنامه یکتا تولید کرد برای {first_name} {last_name}'))
                    continue
                
                # تاریخ تولد (بین 1375 تا 1385)
                birth_year = random.randint(1375, 1385)
                birth_month = random.randint(1, 12)
                birth_day = random.randint(1, 28)
                birth_date = f"{birth_year}/{birth_month:02d}/{birth_day:02d}"
                
                # انتخاب شهر
                city = City.objects.order_by('?').first()
                
                # سال ورود (بین 1398 تا 1403)
                enrollment_year = random.randint(1398, 1403)
                enrollment_date = f"{enrollment_year}/07/01"
                
                # تولید شماره دانشجویی
                college_code = college.code
                field_code = field.code
                serial = field_counters[field.id]
                student_number = self.generate_student_number(enrollment_year, college_code, field_code, serial)
                
                # بررسی یکتایی شماره دانشجویی
                max_attempts = 1000
                attempts = 0
                while Student.objects.filter(student_number=student_number).exists() and attempts < max_attempts:
                    field_counters[field.id] += 1
                    serial = field_counters[field.id]
                    student_number = self.generate_student_number(enrollment_year, college_code, field_code, serial)
                    attempts += 1
                
                if attempts >= max_attempts:
                    self.stdout.write(self.style.WARNING(f'نمی‌توان شماره دانشجویی یکتا تولید کرد برای {first_name} {last_name}'))
                    continue
                
                field_counters[field.id] += 1
                
                specialization = random.choice(specializations) if specializations.exists() else None
                
                # تعیین وضعیت فعال بودن (برخی فارغ‌التحصیل شده‌اند)
                is_active = enrollment_year < 1401 or random.choice([True, False])
                
                student = Student.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    national_id=national_id,
                    id_number=id_number,
                    birth_date_shamsi=birth_date,
                    birth_place=city,
                    gender='M' if is_male else 'F',
                    marital_status=random.choice(['S', 'M']),
                    military_status=random.choice(['E', 'C', 'D', 'N']) if is_male else None,
                    address=f"تهران، خیابان {random.choice(['ولیعصر', 'انقلاب', 'آزادی', 'جمهوری'])}, پلاک {random.randint(1, 500)}",
                    student_number=student_number,
                    field_of_study=field,
                    specialization=specialization,
                    enrollment_date=enrollment_date,
                    is_active=is_active
                )
                students.append(student)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(students)} دانشجو ایجاد شد'))
        return students

    def create_classes(self, courses, terms, rooms, professors):
        """ایجاد کلاس‌ها"""
        self.stdout.write('در حال ایجاد کلاس‌ها...')
        
        classes = []
        days = ['SA', 'SU', 'MO', 'TU', 'WE', 'TH']  # شنبه تا پنج‌شنبه
        time_slots = [
            (time(8, 0), time(9, 30)),
            (time(10, 0), time(11, 30)),
            (time(12, 0), time(13, 30)),
            (time(14, 0), time(15, 30)),
            (time(16, 0), time(17, 30)),
        ]
        
        # انتخاب ترم‌های اخیر برای ایجاد کلاس
        recent_terms = terms[-6:]  # آخرین 6 ترم
        
        class_counter = 1
        used_slots = {}  # برای جلوگیری از تداخل زمانی
        
        for term in recent_terms:
            # انتخاب چند درس برای این ترم
            term_courses = random.sample(list(courses), min(10, len(courses)))
            
            for course in term_courses:
                # انتخاب استاد
                professor = random.choice(professors)
                
                # انتخاب اتاق
                room = random.choice(rooms)
                
                # انتخاب زمان بدون تداخل
                day = random.choice(days)
                time_slot = random.choice(time_slots)
                start_time, end_time = time_slot
                
                # بررسی تداخل
                slot_key = (term.id, room.id, day, start_time, end_time)
                if slot_key in used_slots:
                    continue
                used_slots[slot_key] = True
                
                # تولید کد کلاس
                class_code = f"{course.code}-{term.code}-{class_counter:02d}"
                while Class.objects.filter(class_code=class_code).exists():
                    class_counter += 1
                    class_code = f"{course.code}-{term.code}-{class_counter:02d}"
                
                # ظرفیت کلاس
                capacity = random.choice([30, 40, 50])
                
                class_obj = Class.objects.create(
                    class_code=class_code,
                    course=course,
                    term=term,
                    room=room,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    capacity=capacity,
                    is_active=True
                )
                
                # تخصیص استاد
                ProfessorCourseAssignment.objects.create(
                    professor=professor,
                    class_course=class_obj,
                    is_primary=True
                )
                
                classes.append(class_obj)
                class_counter += 1
                
                if len(classes) >= 15:
                    break
            
            if len(classes) >= 15:
                break
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(classes)} کلاس ایجاد شد'))
        return classes

    def create_registrations(self, students, classes, terms):
        """ایجاد ثبت‌نام‌های دانشجویان"""
        self.stdout.write('در حال ایجاد ثبت‌نام‌ها...')
        
        status_choices = ['R', 'P', 'F', 'W', 'I']  # ثبت‌نام شده، قبول، مردود، حذف، ناقص
        
        registrations_count = 0
        
        # توزیع ثبت‌نام‌ها بین دانشجویان
        for student in students:
            # تعداد کلاس‌هایی که دانشجو در آن‌ها ثبت‌نام کرده (بین 5 تا 15)
            num_registrations = random.randint(5, 15)
            
            # انتخاب کلاس‌های تصادفی
            student_classes = random.sample(classes, min(num_registrations, len(classes)))
            
            for class_obj in student_classes:
                # تعیین وضعیت بر اساس ترم
                term = class_obj.term
                enrollment_year = int(student.enrollment_date.split('/')[0])
                term_year = int(term.code[:4])
                
                # اگر ترم قبل از ورود دانشجو باشد، رد می‌کنیم
                if term_year < enrollment_year:
                    continue
                
                # اگر ترم خیلی قدیمی باشد، نمره دارد
                if term_year < 1402:
                    status = random.choice(['P', 'F'])  # قبول یا مردود
                    grade = random.uniform(10, 20) if status == 'P' else random.uniform(0, 9.99)
                elif term_year == 1402:
                    # ترم گذشته - ممکن است نمره داشته باشد یا نداشته باشد
                    status = random.choice(['P', 'F', 'I'])
                    grade = random.uniform(10, 20) if status == 'P' else (random.uniform(0, 9.99) if status == 'F' else None)
                else:
                    # ترم جاری یا آینده
                    status = 'R'  # ثبت‌نام شده
                    grade = None
                
                # بررسی عدم تکراری بودن
                if not StudentClassRegistration.objects.filter(
                    student=student,
                    class_course=class_obj
                ).exists():
                    StudentClassRegistration.objects.create(
                        student=student,
                        class_course=class_obj,
                        grade=round(grade, 2) if grade else None,
                        status=status
                    )
                    registrations_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {registrations_count} ثبت‌نام ایجاد شد'))

    def create_contact_info(self, students, professors):
        """ایجاد اطلاعات تماس"""
        self.stdout.write('در حال ایجاد اطلاعات تماس...')
        
        contact_types = {
            'تلفن ثابت': ContactType.objects.filter(name='تلفن ثابت').first(),
            'موبایل': ContactType.objects.filter(name='موبایل').first(),
            'ایمیل': ContactType.objects.filter(name='ایمیل').first(),
        }
        
        contact_count = 0
        
        # ایجاد اطلاعات تماس برای دانشجویان
        for student in students:
            student_content_type = ContentType.objects.get_for_model(Student)
            
            # موبایل
            if contact_types['موبایل']:
                mobile = f"09{random.randint(100000000, 999999999)}"
                ContactInfo.objects.create(
                    content_type=student_content_type,
                    object_id=student.id,
                    contact_type=contact_types['موبایل'],
                    value=mobile,
                    is_primary=True
                )
                contact_count += 1
            
            # ایمیل
            if contact_types['ایمیل']:
                email = f"{student.first_name.lower()}.{student.last_name.lower()}@student.university.ac.ir"
                ContactInfo.objects.create(
                    content_type=student_content_type,
                    object_id=student.id,
                    contact_type=contact_types['ایمیل'],
                    value=email,
                    is_primary=False
                )
                contact_count += 1
        
        # ایجاد اطلاعات تماس برای اساتید
        for professor in professors:
            professor_content_type = ContentType.objects.get_for_model(Professor)
            
            # موبایل
            if contact_types['موبایل']:
                mobile = f"09{random.randint(100000000, 999999999)}"
                ContactInfo.objects.create(
                    content_type=professor_content_type,
                    object_id=professor.id,
                    contact_type=contact_types['موبایل'],
                    value=mobile,
                    is_primary=True
                )
                contact_count += 1
            
            # ایمیل
            if contact_types['ایمیل']:
                email = f"{professor.first_name.lower()}.{professor.last_name.lower()}@prof.university.ac.ir"
                ContactInfo.objects.create(
                    content_type=professor_content_type,
                    object_id=professor.id,
                    contact_type=contact_types['ایمیل'],
                    value=email,
                    is_primary=False
                )
                contact_count += 1
            
            # تلفن ثابت
            if contact_types['تلفن ثابت']:
                phone = f"021{random.randint(10000000, 99999999)}"
                ContactInfo.objects.create(
                    content_type=professor_content_type,
                    object_id=professor.id,
                    contact_type=contact_types['تلفن ثابت'],
                    value=phone,
                    is_primary=False
                )
                contact_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {contact_count} اطلاعات تماس ایجاد شد'))

    def create_surveys(self, students, professors, classes):
        """ایجاد نظرسنجی‌های اساتید"""
        self.stdout.write('در حال ایجاد نظرسنجی‌ها...')
        
        rating_choices = [1, 2, 3, 4, 5]
        survey_count = 0
        
        # ایجاد نظرسنجی برای کلاس‌های گذشته
        past_classes = [c for c in classes if int(c.term.code[:4]) < 1403]
        
        for class_obj in past_classes[:20]:  # حداکثر 20 نظرسنجی
            # انتخاب دانشجویانی که در این کلاس ثبت‌نام کرده‌اند
            registrations = StudentClassRegistration.objects.filter(
                class_course=class_obj,
                status__in=['P', 'F']
            )
            
            # انتخاب استاد کلاس
            professor_assignment = ProfessorCourseAssignment.objects.filter(
                class_course=class_obj,
                is_primary=True
            ).first()
            
            if not professor_assignment:
                continue
            
            professor = professor_assignment.professor
            
            # انتخاب چند دانشجو برای نظرسنجی
            survey_students = random.sample(
                list(registrations.values_list('student', flat=True)),
                min(5, registrations.count())
            )
            
            for student_id in survey_students:
                student = Student.objects.get(id=student_id)
                
                # بررسی عدم تکراری بودن
                if not ProfessorSurvey.objects.filter(
                    student=student,
                    professor=professor,
                    class_course=class_obj
                ).exists():
                    ProfessorSurvey.objects.create(
                        student=student,
                        professor=professor,
                        class_course=class_obj,
                        teaching_quality=random.choice(rating_choices),
                        communication=random.choice(rating_choices),
                        punctuality=random.choice(rating_choices),
                        overall_rating=random.choice(rating_choices),
                        comments=random.choice([
                            'استاد خوبی بود',
                            'تدریس عالی',
                            'می‌توانست بهتر باشد',
                            'نظری ندارم',
                            ''
                        ])
                    )
                    survey_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {survey_count} نظرسنجی ایجاد شد'))

