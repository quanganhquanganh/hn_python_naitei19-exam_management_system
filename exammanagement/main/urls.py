from django.urls import path

from . import views

urlpatterns = [
    path("", views.SubjectListView.as_view(), name="index"),
    path("subjects/", views.SubjectListView.as_view(), name="subjects"),
    path(
        "subjects/enrolled/",
        views.EnrolledSubjectListView.as_view(),
        name="enrolled-subjects",
    ),
    path("subject/<int:pk>", views.SubjectDetailView.as_view(), name="subject-detail"),
    path("chapter/<int:pk>", views.ChapterDetailView.as_view(), name="chapter-detail"),
    path(
        "subject/<int:subject_id>/enroll/",
        views.enroll_subject,
        name="subject-registration",
    ),
    path("profile/<int:pk>", views.user_profile, name="user-profile"),
    path("create-exam/chapter/<int:pk>", views.create_exam_view, name="create-exam"),
    path("exam/<int:pk>", views.take_exam_view, name="take-exam"),
    path("edit-profile", views.edit_profile, name="edit-profile"),
    path("mark-read", views.mark_notification_as_read, name="mark-read"),
]
