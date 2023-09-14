import uuid
import jsonfield
from pyexcel_xlsx import get_data
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text=_(
        'Genre of the subject (IT, Japanese, etc)'))

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(
        max_length=200, help_text=_('Title name of the subject'))
    description = models.TextField(
        max_length=1000, help_text=_('Description'), blank=True)
    genres = models.ManyToManyField(
        Genre, help_text=_('Select genre for this subject'))
    enrollers = models.ManyToManyField(User, through='Enroll')

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
    num_questions = models.PositiveIntegerField(default=20)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('chapter-detail', args=[str(self.id)])

    def clean(self):
        if self.min_correct_ans > self.num_questions:
            raise ValidationError(
                _('Minimum correct answers must be less than number of questions'))


class Enroll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)
    SUBJECT_STATUS = (
        (1, 'Completed'),
        (0, 'Incomplete'),
    )
    status = models.IntegerField(
        choices=SUBJECT_STATUS,
        blank=True,
        default=0,
    )

    class Meta:
        unique_together = ('user', 'subject')


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT)
    total_score = models.IntegerField()
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    TEST_STATUS = (
        (1, 'Completed'),
        (0, 'Incomplete'),
    )
    status = models.IntegerField(
        choices=TEST_STATUS,
        blank=True,
        default=0,
    )

    def get_absolute_url(self):
        return reverse('take-exam', args=[str(self.id)])


class Question(models.Model):
    id = models.CharField(primary_key=True,
                          max_length=100, default=uuid.uuid4, editable=False)
    description = models.TextField(
        max_length=1000, help_text=_('Detail of the question'))
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)


class Answer(models.Model):
    content = models.TextField(
        max_length=1000, help_text=_('Content of the answer'))
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)


class Choice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)


class QuestionSetImport(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=512)
    filename = models.FileField(max_length=512, upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        try:
            data = get_data(self.filename.file)
        except Exception as e:
            raise ValidationError(str(e))

        # The data will be in the following format
        # Column A: Subject
        # Column B: Chapter
        # Column C: Question ID
        # Column D: Question Description
        # Column E: Correct Answers (separated by comma) (ex: 1,2,3)
        # Column F onwards: Answers

        for row in data['Sheet1']:
            if len(row) < 5:
                raise ValidationError(_('Not enough columns'))

            subject_name, chapter_name, question_id, question_description, correct_answers = row[
                :5]

            if subject_name == '' or chapter_name == '' or question_id == '' or question_description == '' or correct_answers == '':
                raise ValidationError(_('All fields are required'))

            question = Question.objects.filter(id=question_id).first()
            if question is not None:
                raise ValidationError(_('Question ID already exists'))

            try:
                correct_answers = [int(float(x))
                                   for x in str(correct_answers).split(',')]
            except Exception as e:
                raise ValidationError(
                    _('Correct answers must be a list of numbers separated by comma'))

            for index, answer in enumerate(row[5:]):
                if answer == '':
                    raise ValidationError(_('All answers are required'))

    def save(self, *args, **kwargs):
        data = get_data(self.filename.file)

        for row in data['Sheet1']:
            subject_name, chapter_name, question_id, question_description, correct_answers = row[
                :5]

            subject = Subject.objects.filter(name=subject_name).first()
            if subject is None:
                subject = Subject(name=subject_name)
                subject.save()

            chapter = Chapter.objects.filter(
                name=chapter_name, subject=subject).first()
            if chapter is None:
                chapter = Chapter(name=chapter_name, subject=subject,
                                  num_questions=0, min_correct_ans=0, time_limit=0)
                chapter.save()

            question = Question(
                id=question_id, description=question_description, chapter=chapter)
            question.save()

            correct_answers = [int(float(x))
                               for x in str(correct_answers).split(',')]

            for index, answer in enumerate(row[5:]):
                answer = Answer(content=answer, question=question,
                                is_correct=((index+1) in correct_answers))
                answer.save()

        super(QuestionSetImport, self).save(*args, **kwargs)
