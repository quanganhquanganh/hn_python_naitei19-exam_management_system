# Generated by Django 4.2.5 on 2023-10-03 10:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0021_alter_questionsetimport_filename_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="url",
            field=models.CharField(
                help_text="URL of the notification", max_length=1000, null=True
            ),
        ),
    ]
