from main.models import Subject, Chapter, Enroll
from .forms import NewUserForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

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
        context['enrollercount'] = context['subject'].enroll_set.all().count()
        user = self.request.user
        context['is_enrolled'] = context['subject'].enrollers.filter(
            id=user.id).exists()
        return context


class ChapterDetailView(generic.DetailView):
    model = Chapter


def chapter_detail_view(request, primary_key):
    chapter = get_object_or_404(Chapter, pk=primary_key)
    return render(request, 'main/chapter_detail.html', context={'chapter': chapter})


@login_required
def enroll_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    user = request.user

    if request.method == 'POST':
        registration = Enroll(user=user, subject=subject)
        registration.save()
        return JsonResponse({'message': _("Registration successful.")})
    return render(request, 'enroll_form.html', {'subject': subject})


def user_profile(request):
    user = request.user
    enrolled_subjects = Enroll.objects.filter(
        user=user)

    context = {
        'user': user,
        'enrolled_subjects': enrolled_subjects,
    }

    return render(request, 'main/user_profile.html', context)
