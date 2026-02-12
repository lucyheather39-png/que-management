from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
import os


class Command(BaseCommand):
    help = 'Creates or updates a superuser account'

    def handle(self, *args, **options):
        try:
            username = os.getenv('ADMIN_USERNAME', 'admin')
            email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            password = os.getenv('ADMIN_PASSWORD', 'admin123')

            # Delete existing admin if it exists and recreate
            User.objects.filter(username=username).delete()
            
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Create or update UserProfile for the admin user
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'citizen_type': 'regular', 'is_verified': True}
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser "{username}" with email "{email}"'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Admin login: username="{username}", password="{password}"'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating admin user: {str(e)}'
                )
            )
