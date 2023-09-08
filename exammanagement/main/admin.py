from .models import Subject, Genre, Chapter
from django.contrib import admin

# Register your models here.


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_genre')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Chapter)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'min_correct_ans',
                    'time_limit', 'num_questions')
