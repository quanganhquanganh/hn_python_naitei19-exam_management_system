import uuid
import jsonfield
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text=_(
        'Genre of the subject (IT, Japanese, etc)'))

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(
        max_length=200, help_text=_('Title name of the subject'))
    description = models.TextField(max_length=1000, help_text=_('Description'))
    genres = models.ManyToManyField(
        Genre, help_text=_('Select genre for this subject'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('subject-detail', args=[str(self.id)])

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genres.all())

    display_genre.short_description = 'Genre'


class Chapter(models.Model):
    name = models.CharField(
        max_length=200, help_text=_('Title name of the chapter'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    min_correct_ans = models.PositiveIntegerField(
        help_text=_('Minimum correct answers to pass the test'))
    time_limit = models.PositiveIntegerField(
        help_text=_('Time limit for the test'))
    num_questions = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('chapter-detail', args=[str(self.id)])


class Enroll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField()
    SUBJECT_STATUS = (
        (1, 'Completed'),
        (0, 'Incomplete'),
    )
    status = models.IntegerField(
        max_length=1,
        choices=SUBJECT_STATUS,
        blank=True,
        default='i',
    )


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT)
    total_score = models.IntegerField()
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    TEST_STATUS = (
        (1, 'Completed'),
        (0, 'Incomplete'),
    )
    status = models.IntegerField(
        max_length=1,
        choices=TEST_STATUS,
        blank=True,
        default='i',
    )


class Question(models.Model):
    description = models.TextField(
        max_length=1000, help_text=_('Detail of the question'))
    chapter_id = models.ForeignKey(Chapter, on_delete=models.CASCADE)


class Answer(models.Model):
    content = models.TextField(
        max_length=1000, help_text=_('Content of the answer'))
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField()


class Choice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
