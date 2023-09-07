from main.models import Subject

from django.shortcuts import render
from django.views import generic
# Create your views here.


class SubjectListView(generic.ListView):
    model = Subject
    paginate_by = 6
