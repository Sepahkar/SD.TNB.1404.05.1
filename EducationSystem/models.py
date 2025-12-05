from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import jdatetime
from datetime import datetime, date


# ============================================
# مدل‌های پایه - جداول مرجع
# ============================================

class Country(models.Model):
    """
    جدول کشورها
    برای ذخیره اطلاعات کشورها استفاده می‌شود
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام کشور",
        help_text="نام کشور به فارسی"
    )
    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name="کد کشور",
        help_text="کد سه حرفی کشور (مثل IRN)"
    )

    class Meta:
        verbose_name = "کشور"
        verbose_name_plural = "کشورها"
        ordering = ['name']

    def __str__(self):
        return self.name


class Province(models.Model):
    """
    جدول استان‌ها
    برای ذخیره اطلاعات استان‌های کشور استفاده می‌شود
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام استان",
        help_text="نام استان به فارسی"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='provinces',
        verbose_name="کشور",
        help_text="کشوری که این استان به آن تعلق دارد"
    )

    class Meta:
        verbose_name = "استان"
        verbose_name_plural = "استان‌ها"
        ordering = ['name']
        unique_together = ['name', 'country']

    def __str__(self):
        return f"{self.name} - {self.country.name}"


class City(models.Model):
    """
    جدول شهرها
    برای ذخیره اطلاعات شهرها استفاده می‌شود
    """
    name = models.CharField(
        max_length=100,
        verbose_name="نام شهر",
        help_text="نام شهر به فارسی"
    )
    province = models.ForeignKey(
        to=Province,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name="استان",
        help_text="استانی که این شهر به آن تعلق دارد"
    )

    class Meta:
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"
        ordering = ['name']
        unique_together = ['name', 'province']

    def __str__(self):
        return f"{self.name} - {self.province.name}"


class ContactType(models.Model):
    """
    جدول انواع تماس
    برای تعریف انواع روش‌های تماس (تلفن، ایمیل، موبایل و ...)
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="نوع تماس",
        help_text="نوع تماس (مثل تلفن ثابت، موبایل، ایمیل)"
    )

    class Meta:
        verbose_name = "نوع تماس"
        verbose_name_plural = "انواع تماس"
        ordering = ['name']

    def __str__(self):
        return self.name


# ============================================
# مدل Person - مدل پایه برای افراد
# ============================================

class Person(models.Model):
    """
    مدل پایه برای اطلاعات مشترک افراد
    این مدل abstract است و برای Student، Professor و Staff استفاده می‌شود
    """
    # Choices برای جنسیت
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]

    # Choices برای وضعیت تاهل
    MARITAL_STATUS_CHOICES = [
        ('S', 'مجرد'),
        ('M', 'متاهل'),
        ('D', 'مطلقه'),
        ('W', 'بیوه'),
    ]

    # Choices برای وضعیت نظام وظیفه
    MILITARY_STATUS_CHOICES = [
        ('E', 'معاف'),
        ('C', 'مشمول'),
        ('D', 'دارای کارت پایان خدمت'),
        ('N', 'غیرمشمول'),
    ]

    first_name = models.CharField(
        max_length=100,
        verbose_name="نام",
        help_text="نام فرد"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="نام خانوادگی",
        help_text="نام خانوادگی فرد"
    )
    national_id = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="کد ملی",
        help_text="کد ملی ۱۰ رقمی",
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='کد ملی باید دقیقاً ۱۰ رقم باشد'
            )
        ]
    )
    id_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="شماره شناسنامه",
        help_text="شماره شناسنامه"
    )
    birth_date_shamsi = models.CharField(
        max_length=10,
        verbose_name="تاریخ تولد (شمسی)",
        help_text="تاریخ تولد به صورت شمسی (YYYY/MM/DD)"
    )
    birth_place = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_born_people',
        related_query_name='%(class)s_born',
        verbose_name="محل تولد",
        help_text="شهر محل تولد"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="جنسیت",
        help_text="جنسیت فرد"
    )
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        verbose_name="وضعیت تاهل",
        help_text="وضعیت تاهل فرد"
    )
    military_status = models.CharField(
        max_length=1,
        choices=MILITARY_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="وضعیت نظام وظیفه",
        help_text="وضعیت نظام وظیفه (فقط برای آقایان)"
    )
    address = models.TextField(
        verbose_name="آدرس",
        help_text="آدرس کامل محل سکونت",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
        help_text="تاریخ و زمان ایجاد رکورد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
        help_text="تاریخ و زمان آخرین بروزرسانی"
    )

    class Meta:
        abstract = True
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """اعتبارسنجی مدل"""
        super().clean()
        # اعتبارسنجی کد ملی
        if self.national_id:
            if len(self.national_id) != 10:
                raise ValidationError({'national_id': 'کد ملی باید دقیقاً ۱۰ رقم باشد'})
            # بررسی صحت کد ملی (الگوریتم چک دیجیت)
            if not self._validate_national_id(self.national_id):
                raise ValidationError({'national_id': 'کد ملی معتبر نیست'})
        
        # اعتبارسنجی تاریخ تولد شمسی
        if self.birth_date_shamsi:
            try:
                parts = self.birth_date_shamsi.split('/')
                if len(parts) != 3:
                    raise ValidationError({'birth_date_shamsi': 'فرمت تاریخ باید YYYY/MM/DD باشد'})
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                jdatetime.date(year, month, day)
            except (ValueError, AttributeError):
                raise ValidationError({'birth_date_shamsi': 'تاریخ تولد شمسی معتبر نیست'})

    def _validate_national_id(self, national_id):
        """اعتبارسنجی کد ملی با الگوریتم چک دیجیت"""
        if len(national_id) != 10:
            return False
        try:
            check = int(national_id[9])
            s = sum(int(national_id[i]) * (10 - i) for i in range(9)) % 11
            return (s < 2 and check == s) or (s >= 2 and check == 11 - s)
        except ValueError:
            return False

    @property
    def full_name(self):
        """نام کامل فرد"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """محاسبه سن فرد بر اساس تاریخ تولد شمسی"""
        try:
            parts = self.birth_date_shamsi.split('/')
            if len(parts) != 3:
                return None
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            birth_date = jdatetime.date(year, month, day)
            today = jdatetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except (ValueError, AttributeError):
            return None


class ContactInfo(models.Model):
    """
    جدول اطلاعات تماس
    برای ذخیره اطلاعات تماس افراد (تلفن، ایمیل و ...)
    از GenericForeignKey برای ارتباط با Person استفاده می‌شود
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="نوع محتوا",
        help_text="نوع مدلی که این تماس به آن تعلق دارد"
    )
    object_id = models.PositiveIntegerField(
        verbose_name="شناسه شی",
        help_text="شناسه شی مورد نظر"
    )
    person = GenericForeignKey('content_type', 'object_id')
    
    contact_type = models.ForeignKey(
        ContactType,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name="نوع تماس",
        help_text="نوع تماس (تلفن، موبایل، ایمیل و ...)"
    )
    value = models.CharField(
        max_length=255,
        verbose_name="مقدار",
        help_text="مقدار تماس (شماره تلفن، آدرس ایمیل و ...)"
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="تماس اصلی",
        help_text="آیا این تماس اصلی است؟"
    )

    class Meta:
        verbose_name = "اطلاعات تماس"
        verbose_name_plural = "اطلاعات تماس‌ها"
        ordering = ['-is_primary', 'contact_type']
        unique_together = ['content_type', 'object_id', 'contact_type', 'value']

    def __str__(self):
        return f"{self.person} - {self.contact_type}: {self.value}"

    def clean(self):
        """اعتبارسنجی اطلاعات تماس"""
        super().clean()
        # اعتبارسنجی ایمیل
        if 'email' in self.contact_type.name.lower() or 'ایمیل' in self.contact_type.name:
            if '@' not in self.value:
                raise ValidationError({'value': 'آدرس ایمیل معتبر نیست'})


# ============================================
# مدل‌های Student, Professor, Staff
# ============================================

class Student(Person):
    """
    مدل دانشجو
    از مدل Person ارث می‌برد و اطلاعات خاص دانشجو را شامل می‌شود

    توجه: فیلدهای زیر از Person به ارث می‌رسند:
    - first_name, last_name (برای نام و نام خانوادگی)
    - national_id (برای کد ملی)
    - address (برای آدرس)
    - gender, marital_status, military_status
    - birth_date_shamsi, birth_place
    - created_at, updated_at
    """

    # وضعیت تحصیلی
    ACADEMIC_STATUS_CHOICES = [
        ('A', 'فعال'),
        ('G', 'فارغ‌التحصیل'),
        ('W', 'انصراف‌داده'),
        ('S', 'معلق'),
    ]

    student_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="شماره دانشجویی",
        help_text="شماره دانشجویی منحصر به فرد - باید بزرگتر از 0 باشد",
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='شماره دانشجویی باید فقط شامل اعداد باشد'
            )
        ]
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="ایمیل",
        help_text="آدرس ایمیل دانشجو (example@domain.com)"
    )

    field_of_study = models.ForeignKey(
        'FieldOfStudy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="رشته تحصیلی",
        help_text="رشته تحصیلی دانشجو"
    )

    specialization = models.ForeignKey(
        'Specialization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="گرایش",
        help_text="گرایش تحصیلی دانشجو"
    )

    enrollment_date = models.DateField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت‌نام",
        help_text="تاریخ ثبت‌نام در دانشگاه (مقدار پیش‌فرض = زمان فعلی)"
    )

    academic_status = models.CharField(
        max_length=1,
        choices=ACADEMIC_STATUS_CHOICES,
        default='A',
        verbose_name="وضعیت تحصیلی",
        help_text="وضعیت تحصیلی دانشجو (فعال، فارغ‌التحصیل، انصراف‌داده)"
    )

    # برای دسترسی به شماره موبایل از ContactInfo استفاده کنید
    # این فیلد اینجا نیست چون در جدول ContactInfo ذخیره می‌شود

    class Meta:
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"
        ordering = ['student_number']

    def __str__(self):
        return f"{self.student_number} - {self.full_name}"

    def clean(self):
        """اعتبارسنجی مدل دانشجو"""
        super().clean()

        # بررسی شماره دانشجویی باید بزرگتر از 0 باشد
        if self.student_number:
            if not self.student_number.isdigit():
                raise ValidationError({
                    'student_number': 'شماره دانشجویی باید فقط شامل اعداد باشد'
                })
            if int(self.student_number) <= 0:
                raise ValidationError({
                    'student_number': 'شماره دانشجویی باید بزرگ‌تر از 0 باشد'
                })

    @property
    def is_active(self):
        """آیا دانشجو فعال است؟"""
        return self.academic_status == 'A'

    @property
    def mobile_number(self):
        """دریافت شماره موبایل از جدول ContactInfo"""
        from django.contrib.contenttypes.models import ContentType
        try:
            contact = ContactInfo.objects.get(
                content_type=ContentType.objects.get_for_model(Student),
                object_id=self.id,
                contact_type__name='موبایل',
                is_primary=True
            )
            return contact.value
        except ContactInfo.DoesNotExist:
            return None

    @property
    def total_credits_passed(self):
        """محاسبه تعداد واحدهای گذرانده شده"""
        registrations = StudentClassRegistration.objects.filter(
            student=self,
            status='P'  # Passed
        )
        return sum(reg.class_course.course.credits for reg in registrations)

    @property
    def total_credits_remaining(self):
        """محاسبه تعداد واحدهای باقیمانده"""
        field = self.field_of_study
        if not field:
            return None
        total_required = field.total_credits
        passed = self.total_credits_passed
        return max(0, total_required - passed) if total_required else None

    @property
    def gpa(self):
        """محاسبه معدل کل دانشجو"""
        registrations = StudentClassRegistration.objects.filter(
            student=self,
            grade__isnull=False
        )
        if not registrations.exists():
            return None

        total_points = 0
        total_credits = 0
        for reg in registrations:
            credits = reg.class_course.course.credits
            grade = reg.grade
            if grade is not None:
                total_points += grade * credits
                total_credits += credits

        return round(total_points / total_credits, 2) if total_credits > 0 else None


# ============================================
# نحوه استفاده صحیح
# ============================================

"""
# 1. ابتدا ContactType برای موبایل ایجاد کنید (یکبار)
ContactType.objects.get_or_create(name='موبایل')

# 2. ایجاد دانشجو
from django.contrib.contenttypes.models import ContentType

student = Student.objects.create(
    # فیلدهای از Person
    first_name="مهرشاد",
    last_name="شاکری بقا",
    national_id="1234567890",  # کد ملی 10 رقمی
    id_number="123",
    birth_date_shamsi="1380/05/15",
    birth_place=city_object,
    gender="M",
    marital_status="S",
    address="تهران، خیابان ولیعصر",

    # فیلدهای خاص Student
    student_number="4001234567",  # عدد صحیح به صورت string
    email="mehershad@example.com",
    field_of_study=field_object,
    specialization=specialization_object,
    academic_status="A"  # فعال
    # enrollment_date خودکار ست می‌شود
)

# 3. اضافه کردن شماره موبایل
mobile_type = ContactType.objects.get(name='موبایل')
ContactInfo.objects.create(
    content_type=ContentType.objects.get_for_model(Student),
    object_id=student.id,
    contact_type=mobile_type,
    value="09123456789",  # باید با 09 شروع شود و 11 رقم باشد
    is_primary=True
)

# 4. دسترسی به اطلاعات
print(student.full_name)  # مهرشاد شاکری بقا
print(student.national_id)  # 1234567890
print(student.mobile_number)  # 09123456789
print(student.email)  # mehershad@example.com
print(student.is_active)  # True
print(student.gpa)  # معدل
"""


# ============================================
# مدل‌های اضافی - حضور و غیاب و پرداخت
# ============================================

class AttendanceMethod(models.Model):
    """
    جدول روش‌های ثبت حضور
    برای تعریف روش‌های مختلف ثبت حضور (QR، NFC، دستی)
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="روش ثبت حضور",
        help_text="روش ثبت حضور (QR، NFC، دستی)"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به روش ثبت حضور",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا این روش فعال است؟"
    )

    class Meta:
        verbose_name = "روش ثبت حضور"
        verbose_name_plural = "روش‌های ثبت حضور"
        ordering = ['name']

    def __str__(self):
        return self.name


class ClassAttendance(models.Model):
    """
    جدول حضور و غیاب در کلاس
    برای ثبت حضور دانشجویان در جلسات کلاس
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="دانشجو",
        help_text="دانشجویی که حضور او ثبت می‌شود"
    )
    class_course = models.ForeignKey(
        'Class',  # Use string reference
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="کلاس",
        help_text="کلاسی که حضور در آن ثبت می‌شود"
    )
    attendance_time = models.DateTimeField(
        verbose_name="زمان حضور",
        help_text="تاریخ و زمان دقیق حضور دانشجو"
    )
    attendance_method = models.ForeignKey(
        AttendanceMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances',
        verbose_name="روش ثبت حضور",
        help_text="روش ثبت حضور (QR، NFC، دستی)"
    )
    is_approved_by_professor = models.BooleanField(
        default=False,
        verbose_name="تایید استاد",
        help_text="آیا حضور توسط استاد تایید شده است؟"
    )
    notes = models.TextField(
        verbose_name="یادداشت",
        help_text="یادداشت‌های اضافی",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
        help_text="تاریخ و زمان ثبت رکورد"
    )

    class Meta:
        verbose_name = "حضور در کلاس"
        verbose_name_plural = "حضور و غیاب کلاس‌ها"
        ordering = ['-attendance_time']
        unique_together = ['student', 'class_course', 'attendance_time']

    def __str__(self):
        return f"{self.student.student_number} - {self.class_course.class_code} - {self.attendance_time}"

    def clean(self):
        """اعتبارسنجی حضور"""
        super().clean()

        # بررسی اینکه زمان حضور در بازه زمانی کلاس باشد
        if self.attendance_time and self.class_course:
            attendance_date = self.attendance_time.date()
            attendance_time = self.attendance_time.time()

            # بررسی اینکه زمان حضور در محدوده زمان کلاس باشد
            if not (self.class_course.start_time <= attendance_time <= self.class_course.end_time):
                raise ValidationError({
                    'attendance_time': f'زمان حضور باید بین {self.class_course.start_time} تا {self.class_course.end_time} باشد'
                })


class PaymentMethod(models.Model):
    """
    جدول روش‌های پرداخت
    برای تعریف روش‌های مختلف پرداخت (درگاه بانکی، کیف پول، وام)
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="روش پرداخت",
        help_text="روش پرداخت (درگاه بانکی، کیف پول، وام)"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به روش پرداخت",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا این روش فعال است؟"
    )

    class Meta:
        verbose_name = "روش پرداخت"
        verbose_name_plural = "روش‌های پرداخت"
        ordering = ['name']

    def __str__(self):
        return self.name


class PaymentStatus(models.Model):
    """
    جدول وضعیت‌های پرداخت
    برای تعریف وضعیت‌های مختلف پرداخت (موفق، ناموفق، در حال پردازش)
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="وضعیت پرداخت",
        help_text="وضعیت پرداخت (موفق، ناموفق، در حال پردازش)"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به وضعیت پرداخت",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "وضعیت پرداخت"
        verbose_name_plural = "وضعیت‌های پرداخت"
        ordering = ['name']

    def __str__(self):
        return self.name


class TuitionPayment(models.Model):
    """
    جدول پرداخت شهریه
    برای ثبت اطلاعات پرداخت‌های شهریه دانشجویان
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='tuition_payments',
        verbose_name="دانشجو",
        help_text="دانشجویی که شهریه پرداخت کرده"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="مبلغ",
        help_text="مبلغ پرداختی (تومان)",
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ پرداخت",
        help_text="تاریخ و زمان پرداخت (مقدار پیش‌فرض = زمان فعلی)"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name="روش پرداخت",
        help_text="روش پرداخت (درگاه بانکی، کیف پول، وام)"
    )
    payment_status = models.ForeignKey(
        PaymentStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name="وضعیت پرداخت",
        help_text="وضعیت پرداخت (موفق، ناموفق، در حال پردازش)"
    )
    transaction_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تراکنش",
        help_text="کد منحصر به فرد تراکنش (مثل PAY202510190001)"
    )
    term = models.ForeignKey(
        "Term",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tuition_payments',
        verbose_name="ترم",
        help_text="ترمی که این پرداخت برای آن است"
    )
    notes = models.TextField(
        verbose_name="یادداشت",
        help_text="یادداشت‌های اضافی",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
        help_text="تاریخ و زمان ایجاد رکورد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
        help_text="تاریخ و زمان آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "پرداخت شهریه"
        verbose_name_plural = "پرداخت‌های شهریه"
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.student.student_number} - {self.amount} - {self.transaction_code}"

    def clean(self):
        """اعتبارسنجی پرداخت"""
        super().clean()

        # بررسی مبلغ
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'مبلغ باید بزرگ‌تر از 0 باشد'})

        # بررسی فرمت کد تراکنش
        if self.transaction_code:
            # مثال: PAY202510190001
            if not self.transaction_code.startswith('PAY'):
                raise ValidationError({
                    'transaction_code': 'کد تراکنش باید با PAY شروع شود'
                })

    @property
    def is_successful(self):
        """آیا پرداخت موفق بوده است؟"""
        if self.payment_status:
            return self.payment_status.name == 'موفق'
        return False


# ============================================
# نحوه استفاده
# ============================================

"""
# 1. ایجاد داده‌های پایه (یکبار اجرا شود)

# روش‌های ثبت حضور
AttendanceMethod.objects.get_or_create(name='QR')
AttendanceMethod.objects.get_or_create(name='NFC')
AttendanceMethod.objects.get_or_create(name='دستی')

# روش‌های پرداخت
PaymentMethod.objects.get_or_create(name='درگاه بانکی')
PaymentMethod.objects.get_or_create(name='کیف پول')
PaymentMethod.objects.get_or_create(name='وام')

# وضعیت‌های پرداخت
PaymentStatus.objects.get_or_create(name='موفق')
PaymentStatus.objects.get_or_create(name='ناموفق')
PaymentStatus.objects.get_or_create(name='در حال پردازش')


# 2. ثبت حضور دانشجو
from django.utils import timezone

qr_method = AttendanceMethod.objects.get(name='QR')
attendance = ClassAttendance.objects.create(
    student=student_obj,
    class_course=class_obj,
    attendance_time=timezone.now(),
    attendance_method=qr_method,
    is_approved_by_professor=False,
    notes="حضور با موفقیت ثبت شد"
)


# 3. ثبت پرداخت شهریه
bank_method = PaymentMethod.objects.get(name='درگاه بانکی')
success_status = PaymentStatus.objects.get(name='موفق')

payment = TuitionPayment.objects.create(
    student=student_obj,
    amount=5000000,  # 5 میلیون تومان
    payment_method=bank_method,
    payment_status=success_status,
    transaction_code='PAY202510190001',
    term=term_obj,
    notes="پرداخت شهریه ترم اول"
)


# 4. بررسی حضور دانشجو در یک کلاس
student_attendances = ClassAttendance.objects.filter(
    student=student_obj,
    class_course=class_obj
)
print(f"تعداد حضور: {student_attendances.count()}")


# 5. محاسبه مجموع پرداخت‌های موفق یک دانشجو
from django.db.models import Sum

total_paid = TuitionPayment.objects.filter(
    student=student_obj,
    payment_status__name='موفق'
).aggregate(total=Sum('amount'))['total']

print(f"مجموع پرداخت‌ها: {total_paid} تومان")


# 6. دریافت لیست دانشجویان غایب در یک کلاس
from django.db.models import Q

# دانشجویان ثبت‌نام شده
registered_students = StudentClassRegistration.objects.filter(
    class_course=class_obj,
    status__in=['R', 'P']
).values_list('student_id', flat=True)

# دانشجویان حاضر
attended_students = ClassAttendance.objects.filter(
    class_course=class_obj,
    attendance_time__date=timezone.now().date()
).values_list('student_id', flat=True)

# دانشجویان غایب
absent_students = Student.objects.filter(
    id__in=registered_students
).exclude(id__in=attended_students)


# 7. تایید حضور توسط استاد
attendance = ClassAttendance.objects.get(id=1)
attendance.is_approved_by_professor = True
attendance.save()


# 8. جستجوی پرداخت با کد تراکنش
payment = TuitionPayment.objects.get(transaction_code='PAY202510190001')
print(f"وضعیت: {payment.payment_status.name}")
print(f"موفق؟ {payment.is_successful}")
"""
class Professor(Person):
    """
    مدل استاد
    از مدل Person ارث می‌برد و اطلاعات خاص استاد را شامل می‌شود
    """
    # Choices برای نوع قرارداد
    CONTRACT_TYPE_CHOICES = [
        ('F', 'تمام وقت'),
        ('P', 'پاره وقت'),
        ('V', 'مهمان'),
    ]

    professor_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد استادی",
        help_text="کد منحصر به فرد استاد"
    )
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="شماره پرسنلی",
        help_text="شماره پرسنلی استاد"
    )
    contract_type = models.CharField(
        max_length=1,
        choices=CONTRACT_TYPE_CHOICES,
        verbose_name="نوع قرارداد",
        help_text="نوع قرارداد استخدامی"
    )
    hire_date = models.CharField(
        max_length=10,
        verbose_name="تاریخ استخدام (شمسی)",
        help_text="تاریخ شروع به کار به صورت شمسی"
    )
    expertise = models.TextField(
        verbose_name="تخصص",
        help_text="حوزه‌های تخصصی استاد",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا استاد فعال است؟"
    )

    class Meta:
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"
        ordering = ['professor_code']

    def __str__(self):
        return f"{self.professor_code} - {self.full_name}"

    @property
    def teaching_experience_years(self):
        """محاسبه سابقه تدریس به سال"""
        try:
            parts = self.hire_date.split('/')
            if len(parts) != 3:
                return None
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            hire_date = jdatetime.date(year, month, day)
            today = jdatetime.date.today()
            years = today.year - hire_date.year - ((today.month, today.day) < (hire_date.month, hire_date.day))
            return max(0, years)
        except (ValueError, AttributeError):
            return None

    @property
    def current_term_courses_count(self):
        """تعداد درس‌های تدریس شده در ترم جاری"""
        current_term = Term.objects.filter(is_current=True).first()
        if not current_term:
            return 0
        return ProfessorCourseAssignment.objects.filter(
            professor=self,
            class_course__term=current_term
        ).count()


class Staff(Person):
    """
    مدل کارمند
    از مدل Person ارث می‌برد و اطلاعات خاص کارمند را شامل می‌شود
    """
    # Choices برای نوع قرارداد کارمند
    CONTRACT_TYPE_CHOICES = [
        ('F', 'تمام وقت'),
        ('P', 'پاره وقت'),
        ('C', 'قراردادی'),
    ]

    employee_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="شماره پرسنلی",
        help_text="شماره پرسنلی کارمند"
    )
    contract_type = models.CharField(
        max_length=1,
        choices=CONTRACT_TYPE_CHOICES,
        verbose_name="نوع قرارداد",
        help_text="نوع قرارداد استخدامی"
    )
    hire_date = models.CharField(
        max_length=10,
        verbose_name="تاریخ استخدام (شمسی)",
        help_text="تاریخ شروع به کار به صورت شمسی"
    )
    position = models.CharField(
        max_length=100,
        verbose_name="سمت",
        help_text="سمت شغلی کارمند"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا کارمند فعال است؟"
    )

    class Meta:
        verbose_name = "کارمند"
        verbose_name_plural = "کارمندان"
        ordering = ['employee_number']

    def __str__(self):
        return f"{self.employee_number} - {self.full_name}"


# ============================================
# مدل‌های ساختار آموزشی
# ============================================

class College(models.Model):
    """
    جدول دانشکده‌ها
    برای ذخیره اطلاعات دانشکده‌های دانشگاه
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="نام دانشکده",
        help_text="نام دانشکده"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد دانشکده",
        help_text="کد منحصر به فرد دانشکده"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به دانشکده",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا دانشکده فعال است؟"
    )

    class Meta:
        verbose_name = "دانشکده"
        verbose_name_plural = "دانشکده‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name


class FieldOfStudy(models.Model):
    """
    جدول رشته‌های تحصیلی
    برای ذخیره اطلاعات رشته‌های تحصیلی
    """
    name = models.CharField(
        max_length=200,
        verbose_name="نام رشته",
        help_text="نام رشته تحصیلی"
    )
    code = models.CharField(
        max_length=20,
        verbose_name="کد رشته",
        help_text="کد منحصر به فرد رشته"
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='fields_of_study',
        verbose_name="دانشکده",
        help_text="دانشکده مربوط به این رشته"
    )
    degree_level = models.CharField(
        max_length=50,
        verbose_name="مقطع تحصیلی",
        help_text="مقطع تحصیلی (کارشناسی، کارشناسی ارشد، دکتری و ...)"
    )
    total_credits = models.PositiveIntegerField(
        verbose_name="تعداد واحد کل",
        help_text="تعداد واحدهای مورد نیاز برای فارغ‌التحصیلی"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به رشته",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا رشته فعال است؟"
    )

    class Meta:
        verbose_name = "رشته تحصیلی"
        verbose_name_plural = "رشته‌های تحصیلی"
        ordering = ['college', 'name']
        unique_together = ['code', 'college']

    def __str__(self):
        return f"{self.name} - {self.college.name}"


class Specialization(models.Model):
    """
    جدول گرایش‌های تحصیلی
    برای ذخیره اطلاعات گرایش‌های مختلف هر رشته
    """
    name = models.CharField(
        max_length=200,
        verbose_name="نام گرایش",
        help_text="نام گرایش تحصیلی"
    )
    code = models.CharField(
        max_length=20,
        verbose_name="کد گرایش",
        help_text="کد منحصر به فرد گرایش"
    )
    field_of_study = models.ForeignKey(
        FieldOfStudy,
        on_delete=models.CASCADE,
        related_name='specializations',
        verbose_name="رشته",
        help_text="رشته مربوط به این گرایش"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به گرایش",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا گرایش فعال است؟"
    )

    class Meta:
        verbose_name = "گرایش"
        verbose_name_plural = "گرایش‌ها"
        ordering = ['field_of_study', 'name']
        unique_together = ['code', 'field_of_study']

    def __str__(self):
        return f"{self.name} - {self.field_of_study.name}"


class Term(models.Model):
    """
    جدول ترم‌های تحصیلی
    برای ذخیره اطلاعات ترم‌های دانشگاه
    """
    name = models.CharField(
        max_length=100,
        verbose_name="نام ترم",
        help_text="نام ترم (مثل ترم اول ۱۴۰۳-۱۴۰۴)"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد ترم",
        help_text="کد منحصر به فرد ترم"
    )
    start_date = models.CharField(
        max_length=10,
        verbose_name="تاریخ شروع (شمسی)",
        help_text="تاریخ شروع ترم به صورت شمسی"
    )
    end_date = models.CharField(
        max_length=10,
        verbose_name="تاریخ پایان (شمسی)",
        help_text="تاریخ پایان ترم به صورت شمسی"
    )
    is_current = models.BooleanField(
        default=False,
        verbose_name="ترم جاری",
        help_text="آیا این ترم جاری است؟"
    )
    is_registration_open = models.BooleanField(
        default=False,
        verbose_name="ثبت‌نام باز است",
        help_text="آیا ثبت‌نام برای این ترم باز است؟"
    )

    class Meta:
        verbose_name = "ترم"
        verbose_name_plural = "ترم‌ها"
        ordering = ['-code']

    def __str__(self):
        return self.name

    def clean(self):
        """اعتبارسنجی تاریخ‌های ترم"""
        super().clean()
        if self.start_date and self.end_date:
            try:
                start_parts = self.start_date.split('/')
                end_parts = self.end_date.split('/')
                if len(start_parts) != 3 or len(end_parts) != 3:
                    raise ValidationError('فرمت تاریخ باید YYYY/MM/DD باشد')
                start_date = jdatetime.date(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
                end_date = jdatetime.date(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
                if start_date >= end_date:
                    raise ValidationError('تاریخ شروع باید قبل از تاریخ پایان باشد')
            except (ValueError, AttributeError):
                raise ValidationError('تاریخ‌های وارد شده معتبر نیستند')


class Course(models.Model):
    """
    جدول دروس
    برای ذخیره اطلاعات دروس دانشگاه
    """
    name = models.CharField(
        max_length=200,
        verbose_name="نام درس",
        help_text="نام درس"
    )
    code = models.CharField(
        max_length=20,
        verbose_name="کد درس",
        help_text="کد منحصر به فرد درس"
    )
    field_of_study = models.ForeignKey(
        FieldOfStudy,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="رشته",
        help_text="رشته مربوط به این درس"
    )
    credits = models.PositiveIntegerField(
        verbose_name="تعداد واحد",
        help_text="تعداد واحدهای درس",
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    course_type = models.CharField(
        max_length=50,
        verbose_name="نوع درس",
        help_text="نوع درس (اصلی، اختیاری، عمومی و ...)"
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به درس",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا درس فعال است؟"
    )

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "دروس"
        ordering = ['field_of_study', 'code']
        unique_together = ['code', 'field_of_study']

    def __str__(self):
        return f"{self.code} - {self.name}"


class CoursePrerequisite(models.Model):
    """
    جدول پیش‌نیازهای دروس
    برای تعریف دروسی که باید قبل از یک درس خاص گذرانده شوند
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='prerequisites',
        verbose_name="درس",
        help_text="درسی که پیش‌نیاز دارد"
    )
    prerequisite_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='required_for',
        verbose_name="پیش‌نیاز",
        help_text="درسی که باید قبل از این درس گذرانده شود"
    )
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name="اجباری",
        help_text="آیا این پیش‌نیاز اجباری است؟"
    )

    class Meta:
        verbose_name = "پیش‌نیاز درس"
        verbose_name_plural = "پیش‌نیازهای دروس"
        unique_together = ['course', 'prerequisite_course']

    def __str__(self):
        return f"{self.course} نیاز به {self.prerequisite_course}"

    def clean(self):
        """اعتبارسنجی پیش‌نیاز"""
        super().clean()
        if self.course == self.prerequisite_course:
            raise ValidationError('یک درس نمی‌تواند پیش‌نیاز خودش باشد')


class CourseCorequisite(models.Model):
    """
    جدول هم‌نیازهای دروس
    برای تعریف دروسی که باید همزمان با یک درس خاص اخذ شوند
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='corequisites',
        verbose_name="درس",
        help_text="درسی که هم‌نیاز دارد"
    )
    corequisite_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='corequired_with',
        verbose_name="هم‌نیاز",
        help_text="درسی که باید همزمان با این درس اخذ شود"
    )
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name="اجباری",
        help_text="آیا این هم‌نیاز اجباری است؟"
    )

    class Meta:
        verbose_name = "هم‌نیاز درس"
        verbose_name_plural = "هم‌نیازهای دروس"
        unique_together = ['course', 'corequisite_course']

    def __str__(self):
        return f"{self.course} هم‌نیاز با {self.corequisite_course}"

    def clean(self):
        """اعتبارسنجی هم‌نیاز"""
        super().clean()
        if self.course == self.corequisite_course:
            raise ValidationError('یک درس نمی‌تواند هم‌نیاز خودش باشد')


class Room(models.Model):
    """
    جدول اتاق‌ها
    برای ذخیره اطلاعات اتاق‌های دانشگاه
    """
    # Choices برای نوع اتاق
    ROOM_TYPE_CHOICES = [
        ('C', 'کلاس'),
        ('L', 'آزمایشگاه'),
        ('O', 'سمینار'),
        ('A', 'آمفی‌تئاتر'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="نام اتاق",
        help_text="نام یا شماره اتاق"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد اتاق",
        help_text="کد منحصر به فرد اتاق"
    )
    room_type = models.CharField(
        max_length=1,
        choices=ROOM_TYPE_CHOICES,
        verbose_name="نوع اتاق",
        help_text="نوع اتاق"
    )
    capacity = models.PositiveIntegerField(
        verbose_name="ظرفیت",
        help_text="ظرفیت اتاق",
        validators=[MinValueValidator(1)]
    )
    building = models.CharField(
        max_length=100,
        verbose_name="ساختمان",
        help_text="نام ساختمان",
        null=True,
        blank=True
    )
    floor = models.IntegerField(
        verbose_name="طبقه",
        help_text="طبقه اتاق",
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name="توضیحات",
        help_text="توضیحات مربوط به اتاق",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا اتاق فعال است؟"
    )

    class Meta:
        verbose_name = "اتاق"
        verbose_name_plural = "اتاق‌ها"
        ordering = ['building', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Class(models.Model):
    """
    جدول کلاس‌ها
    برای ذخیره اطلاعات کلاس‌های درسی که در یک ترم خاص برگزار می‌شوند
    """
    # Choices برای روزهای هفته
    DAY_CHOICES = [
        ('SA', 'شنبه'),
        ('SU', 'یکشنبه'),
        ('MO', 'دوشنبه'),
        ('TU', 'سه‌شنبه'),
        ('WE', 'چهارشنبه'),
        ('TH', 'پنج‌شنبه'),
        ('FR', 'جمعه'),
    ]

    class_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد کلاس",
        help_text="کد منحصر به فرد کلاس"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name="درس",
        help_text="درسی که این کلاس برای آن برگزار می‌شود"
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name="ترم",
        help_text="ترمی که این کلاس در آن برگزار می‌شود"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes',
        verbose_name="اتاق",
        help_text="اتاقی که کلاس در آن برگزار می‌شود"
    )
    day_of_week = models.CharField(
        max_length=2,
        choices=DAY_CHOICES,
        verbose_name="روز هفته",
        help_text="روز هفته برگزاری کلاس"
    )
    start_time = models.TimeField(
        verbose_name="ساعت شروع",
        help_text="ساعت شروع کلاس"
    )
    end_time = models.TimeField(
        verbose_name="ساعت پایان",
        help_text="ساعت پایان کلاس"
    )
    capacity = models.PositiveIntegerField(
        verbose_name="ظرفیت",
        help_text="ظرفیت کلاس",
        validators=[MinValueValidator(1)]
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا کلاس فعال است؟"
    )

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"
        ordering = ['term', 'course', 'class_code']
        unique_together = ['class_code', 'term']

    def __str__(self):
        return f"{self.class_code} - {self.course.name} - {self.term.name}"

    def clean(self):
        """اعتبارسنجی زمان کلاس"""
        super().clean()
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('ساعت شروع باید قبل از ساعت پایان باشد')
            
            # بررسی تداخل زمانی با کلاس‌های دیگر در همان اتاق و روز
            if self.room and self.day_of_week:
                conflicting_classes = Class.objects.filter(
                    room=self.room,
                    day_of_week=self.day_of_week,
                    term=self.term,
                    is_active=True
                ).exclude(pk=self.pk)
                
                for cls in conflicting_classes:
                    if not (self.end_time <= cls.start_time or self.start_time >= cls.end_time):
                        raise ValidationError(
                            f'تداخل زمانی با کلاس {cls.class_code} در اتاق {self.room.name}'
                        )

    @property
    def remaining_capacity(self):
        """محاسبه ظرفیت باقیمانده کلاس"""
        registered_count = StudentClassRegistration.objects.filter(
            class_course=self,
            status__in=['R', 'P', 'F']  # Registered, Passed, Failed
        ).count()
        return max(0, self.capacity - registered_count)

    @property
    def registered_students_list(self):
        """لیست دانشجویان ثبت‌نام شده در کلاس"""
        registrations = StudentClassRegistration.objects.filter(
            class_course=self,
            status__in=['R', 'P', 'F']
        ).select_related('student')
        return [reg.student for reg in registrations]


# ============================================
# جداول رابطه‌ای
# ============================================

class StudentClassRegistration(models.Model):
    """
    جدول ثبت‌نام دانشجویان در کلاس‌ها
    برای ذخیره اطلاعات ثبت‌نام دانشجو در کلاس و نمره وی
    """
    # Choices برای وضعیت ثبت‌نام
    STATUS_CHOICES = [
        ('R', 'ثبت‌نام شده'),
        ('P', 'قبول'),
        ('F', 'مردود'),
        ('W', 'حذف'),
        ('I', 'ناقص'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='class_registrations',
        verbose_name="دانشجو",
        help_text="دانشجویی که در کلاس ثبت‌نام کرده"
    )
    class_course = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='student_registrations',
        verbose_name="کلاس",
        help_text="کلاسی که دانشجو در آن ثبت‌نام کرده"
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت‌نام",
        help_text="تاریخ و زمان ثبت‌نام"
    )
    grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="نمره",
        help_text="نمره دانشجو در این کلاس",
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='R',
        verbose_name="وضعیت",
        help_text="وضعیت ثبت‌نام و نمره دانشجو"
    )
    notes = models.TextField(
        verbose_name="یادداشت",
        help_text="یادداشت‌های اضافی",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "ثبت‌نام دانشجو در کلاس"
        verbose_name_plural = "ثبت‌نام‌های دانشجویان"
        ordering = ['-registration_date']
        unique_together = ['student', 'class_course']

    def __str__(self):
        return f"{self.student.student_number} - {self.class_course.class_code}"

    def clean(self):
        """اعتبارسنجی ثبت‌نام"""
        super().clean()
        # بررسی ظرفیت کلاس
        if self.class_course:
            registered_count = StudentClassRegistration.objects.filter(
                class_course=self.class_course,
                status__in=['R', 'P', 'F']
            ).exclude(pk=self.pk).count()
            if registered_count >= self.class_course.capacity:
                raise ValidationError('ظرفیت کلاس تکمیل شده است')
        
        # بررسی نمره
        if self.grade is not None:
            if self.grade < 0 or self.grade > 20:
                raise ValidationError('نمره باید بین 0 تا 20 باشد')


class ProfessorCourseAssignment(models.Model):
    """
    جدول تخصیص استاد به درس یا کلاس
    برای تعیین استادی که یک درس یا کلاس را تدریس می‌کند
    """
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='course_assignments',
        verbose_name="استاد",
        help_text="استادی که درس را تدریس می‌کند"
    )
    class_course = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='professor_assignments',
        verbose_name="کلاس",
        help_text="کلاسی که استاد آن را تدریس می‌کند"
    )
    assignment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ تخصیص",
        help_text="تاریخ و زمان تخصیص استاد به کلاس"
    )
    is_primary = models.BooleanField(
        default=True,
        verbose_name="استاد اصلی",
        help_text="آیا این استاد استاد اصلی کلاس است؟"
    )
    notes = models.TextField(
        verbose_name="یادداشت",
        help_text="یادداشت‌های اضافی",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "تخصیص استاد به کلاس"
        verbose_name_plural = "تخصیص‌های اساتید"
        ordering = ['-assignment_date']
        unique_together = ['professor', 'class_course']

    def __str__(self):
        return f"{self.professor.professor_code} - {self.class_course.class_code}"

    def clean(self):
        """اعتبارسنجی تخصیص استاد"""
        super().clean()
        # بررسی اینکه فقط یک استاد اصلی برای هر کلاس وجود داشته باشد
        if self.is_primary and self.class_course:
            primary_assignments = ProfessorCourseAssignment.objects.filter(
                class_course=self.class_course,
                is_primary=True
            ).exclude(pk=self.pk)
            if primary_assignments.exists():
                raise ValidationError('فقط یک استاد اصلی برای هر کلاس می‌تواند وجود داشته باشد')


# ============================================
# مدل‌های تکمیلی
# ============================================

class ProfessorSurvey(models.Model):
    """
    جدول نظرسنجی اساتید
    برای ذخیره نظرات دانشجویان درباره اساتید
    """
    # Choices برای رتبه‌بندی
    RATING_CHOICES = [
        (1, 'خیلی ضعیف'),
        (2, 'ضعیف'),
        (3, 'متوسط'),
        (4, 'خوب'),
        (5, 'عالی'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='professor_surveys',
        verbose_name="دانشجو",
        help_text="دانشجویی که نظرسنجی را تکمیل کرده"
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name="استاد",
        help_text="استادی که درباره او نظرسنجی شده"
    )
    class_course = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name="کلاس",
        help_text="کلاسی که نظرسنجی برای آن انجام شده"
    )
    teaching_quality = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name="کیفیت تدریس",
        help_text="رتبه کیفیت تدریس استاد"
    )
    communication = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name="ارتباط",
        help_text="رتبه ارتباط استاد با دانشجویان"
    )
    punctuality = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name="انضباط زمانی",
        help_text="رتبه انضباط زمانی استاد"
    )
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name="امتیاز کلی",
        help_text="امتیاز کلی استاد"
    )
    comments = models.TextField(
        verbose_name="نظرات",
        help_text="نظرات و پیشنهادات دانشجو",
        null=True,
        blank=True
    )
    survey_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ نظرسنجی",
        help_text="تاریخ و زمان تکمیل نظرسنجی"
    )

    class Meta:
        verbose_name = "نظرسنجی استاد"
        verbose_name_plural = "نظرسنجی‌های اساتید"
        ordering = ['-survey_date']
        unique_together = ['student', 'professor', 'class_course']

    def __str__(self):
        return f"{self.student.student_number} - {self.professor.professor_code} - {self.class_course.class_code}"

    @property
    def average_rating(self):
        """محاسبه میانگین امتیازات"""
        ratings = [
            self.teaching_quality,
            self.communication,
            self.punctuality,
            self.overall_rating
        ]
        return round(sum(ratings) / len(ratings), 2)
