from .models import Subject, Genre, Chapter
from django.contrib import admin

# Register your models here.
from .models import Subject, Chapter, Genre, Question, Answer, QuestionSetImport

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('genres',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'genres')
        }),
    )

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'min_correct_ans', 'time_limit', 'num_questions')
    list_filter = ('subject',)
    search_fields = ('name',)
    ordering = ('name', 'subject', 'min_correct_ans', 'time_limit', 'num_questions')
    fieldsets = (
        (None, {
            'fields': ('name', 'subject', 'min_correct_ans', 'time_limit', 'num_questions')
        }),
    )

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('description', 'chapter')
    list_filter = ('chapter',)
    search_fields = ('description',)
    ordering = ('description', 'chapter')
    fieldsets = ((None, {'fields': ('description', 'chapter')}),)
    inlines = [AnswerInline]


admin.site.register(QuestionSetImport)
