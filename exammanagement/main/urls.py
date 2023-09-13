from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='index'),
    path('subjects/', views.SubjectListView.as_view(), name='subjects'),
    path('subject/<int:pk>', views.SubjectDetailView.as_view(),
         name='subject-detail'),
    path('chapter/<int:pk>', views.ChapterDetailView.as_view(),
         name='chapter-detail'),
    path('subject/<int:subject_id>/enroll/',
         views.enroll_subject, name='subject-registration'),
    path('profile/', views.user_profile, name='user-profile'),
]
