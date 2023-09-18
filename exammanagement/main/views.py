import datetime
import logging
import random
from random import sample

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import requires_csrf_token
from main.models import Answer, Chapter, Choice, Enroll, Genre, Question, Subject, Test

from .forms import NewUserForm

logger = logging.getLogger('mylogger')

# Create your views here.


class SubjectListView(generic.ListView):
    model = Subject
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        genre_id = self.request.GET.get('genre')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if genre_id:
            queryset = queryset.filter(genres=genre_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            'genres'
        ] = Genre.objects.all()
        return context


class EnrolledSubjectListView(LoginRequiredMixin, generic.ListView):
    model = Subject
    paginate_by = 6
    template_name = 'subject_list.html'

    def get_queryset(self):
        return Subject.objects.filter(enrollers=self.request.user)


def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Registration successful.'))
            return HttpResponseRedirect(reverse('index'))
        messages.error(request, _('Unsuccessful registration. Invalid information.'))
    form = NewUserForm()
    return render(
        request=request,
        template_name='./registration/register.html',
        context={'register_form': form},
    )


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, _('You are now logged in as ') + f'{username}.')
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, _('Invalid username or password.'))
        else:
            messages.error(request, _('Invalid username or password.'))
    form = AuthenticationForm()
    return render(
        request=request,
        template_name='./registration/login.html',
        context={'login_form': form},
    )


def logout_request(request):
    logout(request)
    messages.info(request, _('You have successfully logged out.'))
    return HttpResponseRedirect(reverse('index'))


class SubjectDetailView(generic.DetailView):
    model = Subject

    def get_context_data(self, **kwargs):
        context = super(SubjectDetailView, self).get_context_data(**kwargs)
        context['chapters'] = context['subject'].chapter_set.all()
        context['enrollercount'] = context['subject'].enroll_set.all().count()
        user = self.request.user
        context['is_enrolled'] = (
            context['subject'].enrollers.filter(id=user.id).exists()
        )
        return context


class ChapterDetailView(generic.DetailView):
    model = Chapter

    def get_context_data(self, **kwargs):
        context = super(ChapterDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        context['tests'] = Test.objects.filter(
            user=user, chapter=context['chapter']
        ).order_by('-completed_at')[:3]
        return context


@login_required
def enroll_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    user = request.user

    if request.method == 'POST':
        registration = Enroll(user=user, subject=subject)
        registration.save()
        return JsonResponse({'message': _('Registration successful.')})
    return render(request, 'enroll_form.html', {'subject': subject})


def user_profile(request):
    user = request.user
    enrolled_subjects = Enroll.objects.filter(user=user).order_by('-id')[:3]
    tests = Test.objects.filter(user=user).order_by('-completed_at')[:3]

    context = {
        'user': user,
        'enrolled_subjects': enrolled_subjects,
        'tests': tests,
    }

    return render(request, 'main/user_profile.html', context)


@login_required
def create_exam_view(request, pk):
    chapter = get_object_or_404(Chapter, id=pk)
    user = request.user
    # del request.session['is-examing']
    if request.method == 'POST':
        # kiem tra nguoi dung da dang ky chu de chua
        if not chapter.subject.enrollers.filter(id=user.id).exists():
            messages.error(request, _('You must enroll the test\'s subject first.'))
            return render(
                request, 'main/chapter_detail.html', context={'chapter': chapter}
            )
        if (
            'is-examing' not in request.session
        ):  # neu dang chua lam bai kiem tra nao thi tao bai moi
            request.session.get('is-examing', True)
            test = Test(
                user=user, chapter=chapter, created_at=timezone.now(), total_score=0
            )
            test.save()
            if test:
                return HttpResponseRedirect(reverse('take-exam', args=[str(test.id)]))
            else:
                messages.error(request, _('Some errors have occured'))
        # neu dang lam check xem bai dang lam co thuoc chapter khong, neu thuoc thi tiep tuc bai kiem tra, neu khong thi khong cho tao
        elif request.session['is-examing']:
            examing_test = Test.objects.filter(status__exact=0).last()
            if examing_test.chapter.id == chapter.id:
                test = examing_test
                return HttpResponseRedirect(reverse('take-exam', args=[str(test.id)]))
            else:
                messages.error(
                    request,
                    _(
                        'You have a test still in progress. Please submit that test before creating a new test.'
                    ),
                )
        else:
            test = Test(
                user=user, chapter=chapter, created_at=timezone.now(), total_score=0
            )
            test.save()
            if test:
                return HttpResponseRedirect(reverse('take-exam', args=[str(test.id)]))
            else:
                messages.error(request, _('Some errors have occured'))
    return render(request, 'main/chapter_detail.html', context={'chapter': chapter})


def __random_question(test):
    sample_list = []
    for question in Question.objects.filter(chapter=test.chapter):
        sample_list.append(question)
    questions = random.sample(sample_list, 8)
    return questions


# cac session de luu thong tin dong ho dem nguoc
def __countdown_session(request, test):
    exam_start_time = request.session.get(
        'exam_start_time', test.created_at.timestamp()
    )
    exam_duration_minutes = request.session.get(
        'exam_duration_minutes', test.chapter.time_limit
    )
    current_time = timezone.now().timestamp()
    elapsed_time_seconds = current_time - exam_start_time
    remaining_time_seconds = (exam_duration_minutes * 60) - elapsed_time_seconds
    return remaining_time_seconds


# neu khong co chocie trong session thi tao cau hoi ngau nhien va tao cac choice cho test
def __when_not_had_choice(request, test):
    exam_choice_ids = []
    questions = __random_question(test)
    for question in questions:
        choice = Choice(user=request.user, question=question, test=test)
        choice.save()
        exam_choice_ids.append(choice.id)
    request.session['exam-choice-ids'] = exam_choice_ids
    return exam_choice_ids


def __delete_test_sesstion(request):
    if 'exam-choice-ids' in request.session:
        del request.session['exam-choice-ids']
    if 'exam_start_time' in request.session:
        del request.session['exam_start_time']
    if 'exam_duration_minutes' in request.session:
        del request.session['exam_duration_minutes']


# khi submit thi xoa tat ca cac session cua test va luu trang thai test va choice
def __submit_test(request, test, choices):
    total_score = 0
    for choice in choices:
        answer_key = f'question_{choice.question.id}'
        answer_id = request.POST.get(answer_key)
        choice.answer = Answer.objects.filter(id=answer_id).first()
        choice.save()
        if choice.answer:
            if choice.answer.is_correct:
                total_score += 1
    __delete_test_sesstion(request)
    request.session['is-examing'] = False
    test.status = 1
    test.completed_at = timezone.now()
    test.total_score = total_score
    test.save()
    test1 = test
    choices1 = choices
    return test1, choices1


@login_required
@requires_csrf_token
def take_exam_view(request, pk):
    test = get_object_or_404(Test, id=pk)
    if test.status == 0:
        request.session['is-examing'] = True
        # kiem tra xem da ton tai choice trong session
        if 'exam-choice-ids' not in request.session:
            exam_choice_ids = __when_not_had_choice(request, test)
        else:
            exam_choice_ids = list(request.session['exam-choice-ids'])
        logger.info(exam_choice_ids)
        choices = Choice.objects.filter(id__in=exam_choice_ids)

        if request.method == 'POST':
            # Handle user responses
            test1, choices1 = __submit_test(request, test, choices)
            return render(
                request,
                'main/test_results.html',
                context={
                    'test': test1,
                    'choices': choices1,
                },
            )
        remaining_time_seconds = __countdown_session(request, test)
        context = {
            'test': test,
            'choices': choices,
            'remaining_time_seconds': max(remaining_time_seconds, 0),
        }
        if 'user_responses' in request.session:
            user_responses = dict(request.session['user_responses'])
            context['user_responses'] = user_responses
            logger.info(user_responses)
        return render(request, 'main/take_exam.html', context=context)
    else:
        choices = Choice.objects.filter(test=test)
        logger.info(choices)
        return render(
            request,
            'main/test_results.html',
            context={'test': test, 'choices': choices},
        )
