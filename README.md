# SD.TNB.1404.05.1

پروژه سیستم آموزشی با Django

## ویژگی‌ها

- Django Framework
- SQLite Database
- REST Framework
- پشتیبانی از تاریخ جلالی

## نصب و راه‌اندازی

1. نصب پکیج‌های مورد نیاز:
```bash
pip install -r requirements.txt
```

2. اجرای migrations:
```bash
python manage.py migrate
```

3. ایجاد superuser:
```bash
python manage.py createsuperuser
```

4. اجرای سرور:
```bash
python manage.py runserver
```

## ساختار پروژه

- `Config/`: تنظیمات اصلی پروژه
- `EducationSystem/`: اپلیکیشن اصلی سیستم آموزشی
- `static/`: فایل‌های استاتیک (CSS, JS, Images)
- `templates/`: قالب‌های HTML

## دیتابیس

این پروژه از SQLite استفاده می‌کند و فایل دیتابیس (`db.sqlite3`) در ریشه پروژه ایجاد می‌شود.

