from typing import Any

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

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
from .utils import send_notification


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
    list_display = ("description", "right_answers", "chapter")
    list_filter = ("chapter",)
    search_fields = ("description",)
    ordering = ("description", "chapter")
    fieldsets = ((None, {"fields": ("description", "chapter")}),)
    inlines = [AnswerInline]

    def right_answers(self, obj):
        correct_answers = Answer.objects.filter(question=obj, is_correct=True)
        return ", ".join([x.content for x in correct_answers])

    def recalculate_total_score(self, chapter):
        tests = Test.objects.filter(chapter=chapter)
        for test in tests:
            test.total_score = test.calculate_total_score()
            test.save()

    def send_chapter_update_notification(self, chapters):
        notis = set()
        for chapter in chapters:
            for test in Test.objects.filter(chapter=chapter):
                notis.add((test.user, chapter))

        for noti in notis:
            send_notification(
                noti[0],
                f"Your tests of {noti[1].name} has been updated.",
                updated_chapter=noti[1],
            )

    def save_model(
        self, request: HttpRequest, obj: Any, form: Any, change: Any
    ) -> None:
        self.recalculate_total_score(obj.chapter)
        self.send_chapter_update_notification([obj.chapter])

    def save_formset(self, request: Any, form: Any, formset: Any, change: Any) -> None:
        chapters = set()
        if formset.model == Answer:
            for form in formset.forms:
                self.recalculate_total_score(form.instance.question.chapter)
                chapters.add(form.instance.question.chapter)

        return super().save_formset(request, form, formset, change)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        chapters = set()
        for question in queryset:
            chapters.add(question.chapter)
        super().delete_queryset(request, queryset)
        for chapter in chapters:
            self.recalculate_total_score(chapter)
        self.send_chapter_update_notification(chapters)

    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        chapter = obj.chapter
        super().delete_model(request, obj)
        self.recalculate_total_score(chapter)
        self.send_chapter_update_notification([chapter])


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
