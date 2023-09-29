from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a superuser"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Superuser username")
        parser.add_argument("--email", type=str, help="Superuser email")
        parser.add_argument("--password", type=str, help="Superuser password")
        parser.add_argument(
            "--from-env",
            action="store_true",
            help="Get username, email and password from environment variables",
        )

    def handle(self, *args, **kwargs):
        from_env = kwargs["from_env"]
        username = kwargs["username"]
        email = kwargs["email"]
        password = kwargs["password"]
        if from_env:
            from os import getenv

            username = getenv("DJANGO_SUPERUSER_USERNAME")
            email = getenv("DJANGO_SUPERUSER_EMAIL")
            password = getenv("DJANGO_SUPERUSER_PASSWORD")

        # Check if the user already exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created.'))
        else:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" updated.'))
