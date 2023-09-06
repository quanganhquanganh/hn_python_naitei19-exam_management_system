from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubjectListView.as_view(), name='index'),
    path('subjects/', views.SubjectListView.as_view(), name='subjects'),
]
