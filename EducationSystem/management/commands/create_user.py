"""
Django management command برای ایجاد/به‌روزرسانی کاربر ادمین سفارشی
استفاده:
    python manage.py create_user --username sepahkar --password 123 [--email user@example.com]
به صورت پیش‌فرض کاربر به عنوان superuser و staff ساخته/به‌روزرسانی می‌شود.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'ایجاد یا به‌روزرسانی کاربر ادمین با تعیین نام کاربری و رمز عبور'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='نام کاربری')
        parser.add_argument('--password', type=str, required=True, help='رمز عبور')
        parser.add_argument('--email', type=str, default='', help='ایمیل (اختیاری)')
        parser.add_argument(
            '--no-superuser',
            action='store_true',
            help='در صورت اعمال، کاربر به عنوان superuser تنظیم نمی‌شود'
        )
        parser.add_argument(
            '--no-staff',
            action='store_true',
            help='در صورت اعمال، کاربر به عنوان staff تنظیم نمی‌شود'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email'] or f'{username}@example.com'
        make_superuser = not options['no_superuser']
        make_staff = not options['no_staff']

        if not username:
            raise CommandError('گزینه --username الزامی است')
        if not password:
            raise CommandError('گزینه --password الزامی است')

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = make_superuser
            user.is_staff = make_staff
            if email:
                user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(f'کاربر {username} با موفقیت به‌روزرسانی شد.'))
        else:
            if make_superuser:
                User.objects.create_superuser(username=username, email=email, password=password)
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_staff = make_staff
                user.save()
            self.stdout.write(self.style.SUCCESS(f'کاربر {username} با موفقیت ایجاد شد.'))

        self.stdout.write(self.style.SUCCESS(f'نام کاربری: {username}'))
        self.stdout.write(self.style.SUCCESS(f'رمز عبور: {password}'))


