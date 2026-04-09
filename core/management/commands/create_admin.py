import secrets
import string

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a superuser account if it does not exist'

    def handle(self, *args, **options):
        username = 'admin2026'
        email = 'luonglong290901@gmail.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
            return

        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(16))

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
        self.stdout.write(self.style.SUCCESS(f'Temporary password: {password}'))
        self.stdout.write(self.style.WARNING('Please change this password immediately after first login.'))
