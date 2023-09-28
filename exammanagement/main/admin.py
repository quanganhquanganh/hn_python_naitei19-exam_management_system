from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.
from .models import (
    Answer,
    Chapter,
    Choice,
    Genre,
    Profile,
    Question,
    QuestionSetImport,
    Subject,
    Test,
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    fieldsets = ((None, {"fields": ("name",)}),)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("introduction", "date_of_birth", "avatar")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    list_filter = ("genres",)
    search_fields = ("name",)
    ordering = ("name",)
    fieldsets = ((None, {"fields": ("name", "description", "genres")}),)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "min_correct_ans", "time_limit", "num_questions")
    list_filter = ("subject",)
    search_fields = ("name",)
    ordering = ("name", "subject", "min_correct_ans", "time_limit", "num_questions")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "subject",
                    "min_correct_ans",
                    "time_limit",
                    "num_questions",
                )
            },
        ),
    )


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("description", "chapter")
    list_filter = ("chapter",)
    search_fields = ("description",)
    ordering = ("description", "chapter")
    fieldsets = ((None, {"fields": ("description", "chapter")}),)
    inlines = [AnswerInline]


admin.site.register(QuestionSetImport)


# User list view
class TestInline(admin.TabularInline):
    model = Test
    readonly_fields = (
        "chapter",
        "total_score",
        "num_questions",
        "created_at",
        "completed_at",
        "status",
        "passed",
    )
    list_display = (
        "chapter",
        "total_score",
        "num_questions",
        "created_at",
        "completed_at",
        "status",
        "passed",
    )
    extra = 0


# Modify the User admin with inline display of Test
class UserAdmin(admin.ModelAdmin):
    inlines = [TestInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
