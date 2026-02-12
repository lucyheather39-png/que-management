from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Creates a superuser account if it does not exist'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD', 'admin123')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser "{username}"'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Superuser "{username}" already exists'
                )
            )
