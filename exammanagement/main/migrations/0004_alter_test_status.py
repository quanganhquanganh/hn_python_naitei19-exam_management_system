# Generated by Django 3.2.20 on 2023-09-11 09:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0003_alter_enroll_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="test",
            name="status",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Completed"), (0, "Incomplete")],
                default=0,
                max_length=1,
            ),
        ),
    ]
