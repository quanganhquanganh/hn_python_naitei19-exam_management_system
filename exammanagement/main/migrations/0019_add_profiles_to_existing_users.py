# Generated by Django 4.2.5 on 2023-09-28 07:59

from django.db import migrations


def forward_func(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("main", "Profile")
    for user in User.objects.all():
        Profile.objects.create(user=user)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0018_auto_20230927_1736"),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
