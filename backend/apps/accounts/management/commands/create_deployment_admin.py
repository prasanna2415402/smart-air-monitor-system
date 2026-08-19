import os

from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from apps.accounts.models import User

load_dotenv()


class Command(BaseCommand):
    help = "Create or update the deployment admin user"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        password = os.environ.get("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_PASSWORD environment variable is not set."
                )
            )
            return

        full_name = os.environ.get(
            "ADMIN_FULL_NAME",
            "System Administrator"
        )
        mobile_number = os.environ.get(
            "ADMIN_MOBILE",
            "9999999999"
        )

        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "full_name": full_name,
                    "mobile_number": mobile_number,
                },
            )

            user.email = email
            user.full_name = full_name
            user.mobile_number = mobile_number
            user.role = User.Role.ADMIN
            user.account_status = User.AccountStatus.APPROVED
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True

            user.set_password(password)
            user.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deployment admin '{username}' created successfully."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deployment admin '{username}' updated successfully."
                    )
                )

        except IntegrityError as exc:
            self.stdout.write(
                self.style.ERROR(
                    f"Could not create/update deployment admin: {exc}"
                )
            )