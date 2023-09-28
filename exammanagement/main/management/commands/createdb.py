import MySQLdb as mysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Creates database"

    def add_arguments(self, parser):
        parser.add_argument("db_name")
        parser.add_argument("--exist_ok", action="store_true")

    def handle(self, *args, **options):
        db_name = options["db_name"]

        try:
            connection = mysql.connect(
                user=settings.DATABASES["default"]["USER"],
                passwd=settings.DATABASES["default"]["PASSWORD"],
                host=settings.DATABASES["default"]["HOST"],
                port=int(settings.DATABASES["default"]["PORT"]),
            )

            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            cursor.close()
            connection.close()
        except mysql.Error as e:
            if not options["exist_ok"]:
                raise CommandError(f'Error creating database "{db_name}": {e}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'Database "{db_name}" already exists')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created database "{db_name}"')
            )
