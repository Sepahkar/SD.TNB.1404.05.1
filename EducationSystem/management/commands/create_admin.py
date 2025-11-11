"""
Django management command برای ایجاد superuser با نام admin و رمز admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'ایجاد superuser با نام admin و رمز admin'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin'
        email = 'admin@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'کاربر {username} از قبل وجود دارد. در حال به‌روزرسانی...'))
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'کاربر {username} با موفقیت به‌روزرسانی شد.'))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} با موفقیت ایجاد شد.'))
        
        self.stdout.write(self.style.SUCCESS(f'نام کاربری: {username}'))
        self.stdout.write(self.style.SUCCESS(f'رمز عبور: {password}'))

