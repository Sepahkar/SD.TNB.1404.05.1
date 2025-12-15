from rest_framework import serializers
from .models import Student


class StudentFullSerializer(serializers.ModelSerializer):
    """
    Serializer کامل برای مدل Student
    شامل تمام فیلدهای Student و فیلدهای ارث‌بری شده از Person
    """
    
    # فیلدهای محاسبه‌شده (properties)
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    mobile_number = serializers.ReadOnlyField()
    
    # فیلدهای ForeignKey با جزئیات
    birth_place = serializers.StringRelatedField(read_only=True)
    field_of_study = serializers.StringRelatedField(read_only=True)
    specialization = serializers.StringRelatedField(read_only=True)
    
    # نمایش انتخاب‌ها به صورت خوانا
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    military_status_display = serializers.CharField(source='get_military_status_display', read_only=True)
    academic_status_display = serializers.CharField(source='get_academic_status_display', read_only=True)

    class Meta:
        model = Student
        fields = [
            # شناسه‌ها
            'id',
            'student_number',
            'national_id',
            'id_number',
            
            # اطلاعات شخصی
            'first_name',
            'last_name',
            'full_name',
            'birth_date_shamsi',
            'birth_place',
            'age',
            
            # اطلاعات تماس
            'email',
            'mobile_number',
            'address',
            
            # اطلاعات جنسیت و تاهل
            'gender',
            'gender_display',
            'marital_status',
            'marital_status_display',
            'military_status',
            'military_status_display',
            
            # اطلاعات تحصیلی
            'field_of_study',
            'specialization',
            'enrollment_date',
            'academic_status',
            'academic_status_display',
            'is_active',
            
            # تاریخ‌ها
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'enrollment_date',
        ]

