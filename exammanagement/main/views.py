from main.models import Subject
from .forms import NewUserForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

# Create your views here.


class SubjectListView(generic.ListView):
    model = Subject
    paginate_by = 6


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful."))
            return HttpResponseRedirect(reverse('index'))
        messages.error(
            request, _("Unsuccessful registration. Invalid information."))
    form = NewUserForm()
    return render(request=request, template_name="./registration/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, _(
                    "You are now logged in as ") + f"{username}.")
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            messages.error(request, _("Invalid username or password."))
    form = AuthenticationForm()
    return render(request=request, template_name="./registration/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, _("You have successfully logged out."))
    return HttpResponseRedirect(reverse('index'))


class SubjectDetailView(generic.DetailView):
    model = Subject

    def get_context_data(self, **kwargs):
        context = super(SubjectDetailView, self).get_context_data(**kwargs)
        context['chapters'] = context['subject'].chapter_set.all()
        return context


def subject_detail_view(request, primary_key):
    subject = get_object_or_404(Subject, pk=primary_key)
    return render(request, 'main/subject_detail.html', context={'subject': subject})
