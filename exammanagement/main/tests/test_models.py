from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from main.models import Answer, Chapter, Genre, Profile, Question, Subject, Test


class SubjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(name="Subject 1", description="Hello")

    def setUp(self):
        self.genre1 = Genre.objects.create(name="Genre 1")
        self.genre2 = Genre.objects.create(name="Genre 2")
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")

    def test_name_label(self):
        subject = self.subject
        field_label = subject._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_name_max_length(self):
        subject = self.subject
        max_length = subject._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)

    def test_description_label(self):
        subject = self.subject
        field_label = subject._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "description")

    def test_description_max_length(self):
        subject = self.subject
        max_length = subject._meta.get_field("description").max_length
        self.assertEqual(max_length, 1000)

    def test_subject_str_representation(self):
        subject = self.subject
        self.assertEqual(str(subject), subject.name)

    def test_subject_genres_relationship(self):
        subject = self.subject
        subject.genres.add(self.genre1)
        subject.genres.add(self.genre2)

        self.assertEqual(list(subject.genres.all()), [self.genre1, self.genre2])

    def test_subject_enroller_relationship(self):
        subject = self.subject
        subject.enrollers.add(self.user1)
        subject.enrollers.add(self.user2)

        self.assertEqual(list(subject.enrollers.all()), [self.user1, self.user2])

    def test_get_absolute_url(self):
        subject = self.subject
        self.assertEqual(subject.get_absolute_url(), f"/en/main/subject/{subject.pk}")


class ChapterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(name="Subject 1", description="Goodbye")
        cls.chapter = Chapter.objects.create(
            name="Chapter 1",
            min_correct_ans=20,
            subject=cls.subject,
            time_limit=20,
            num_questions=30,
        )

    def test_name_label(self):
        chapter = self.chapter
        field_label = chapter._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_name_max_length(self):
        chapter = self.chapter
        max_length = chapter._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)

    def test_min_correct_ans_label(self):
        chapter = self.chapter
        field_label = chapter._meta.get_field("min_correct_ans").verbose_name
        self.assertEqual(field_label, "min correct ans")

    def test_min_correct_ans_value(self):
        chapter = self.chapter
        self.assertEqual(chapter.min_correct_ans, 20)

    def test_time_limit_label(self):
        chapter = self.chapter
        field_label = chapter._meta.get_field("time_limit").verbose_name
        self.assertEqual(field_label, "time limit")

    def test_time_limit_value(self):
        chapter = self.chapter
        self.assertEqual(chapter.time_limit, 20)

    def test_num_questions_label(self):
        chapter = self.chapter
        field_label = chapter._meta.get_field("num_questions").verbose_name
        self.assertEqual(field_label, "num questions")

    def test_num_questions_value(self):
        chapter = self.chapter
        self.assertEqual(chapter.num_questions, 30)

    def test_chapter_str_representation(self):
        chapter = self.chapter
        self.assertEqual(str(chapter), "Chapter 1")

    def test_chapter_subject_relationship(self):
        chapter = self.chapter
        self.assertEqual(chapter.subject, self.subject)

    def test_get_absolute_url(self):
        chapter = self.chapter
        self.assertEqual(chapter.get_absolute_url(), f"/en/main/chapter/{chapter.pk}")


class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test")
        cls.profile = Profile.objects.create(
            user=cls.user, introduction="Hello", date_of_birth="2023-10-02"
        )

    def test_introduction_label(self):
        profile = self.profile
        field_label = profile._meta.get_field("introduction").verbose_name
        self.assertEqual(field_label, "introduction")

    def test_introduction_max_length(self):
        profile = self.profile
        max_length = profile._meta.get_field("introduction").max_length
        self.assertEqual(max_length, 1000)

    def test_date_of_birth_label(self):
        profile = self.profile
        field_label = profile._meta.get_field("date_of_birth").verbose_name
        self.assertEqual(field_label, "date of birth")

    def test_get_absolute_url(self):
        profile = self.profile
        self.assertEqual(profile.get_absolute_url(), f"/en/main/profile/{profile.pk}")

    def test_profile_user_relationship(self):
        profile = self.profile
        self.assertEqual(profile.user, self.user)


class TestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test 2")
        cls.subject = Subject.objects.create(name="Subject 1", description="Goodbye")
        cls.chapter = Chapter.objects.create(
            name="Chapter 1",
            min_correct_ans=20,
            subject=cls.subject,
            time_limit=20,
            num_questions=30,
        )
        cls.test = Test.objects.create(
            user=cls.user,
            chapter=cls.chapter,
            total_score=0,
            created_at=datetime.now(),
            status=0,
        )

    def test_test_user_relationship(self):
        test = self.test
        self.assertEqual(test.user, self.user)

    def test_test_chapter_relationship(self):
        test = self.test
        self.assertEqual(test.chapter, self.chapter)


class QuestionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(name="Subject 1", description="Goodbye")
        cls.chapter = Chapter.objects.create(
            name="Chapter 1",
            min_correct_ans=20,
            subject=cls.subject,
            time_limit=20,
            num_questions=30,
        )
        cls.question = Question.objects.create(
            description="What is this?", chapter=cls.chapter
        )

    def test_description_label(self):
        question = self.question
        field_label = question._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "description")

    def test_description_max_length(self):
        question = self.question
        max_length = question._meta.get_field("description").max_length
        self.assertEqual(max_length, 1000)

    def test_question_chapter_relationship(self):
        question = self.question
        self.assertEqual(question.chapter, self.chapter)


class AnswerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(name="Subject 1", description="Goodbye")
        cls.chapter = Chapter.objects.create(
            name="Chapter 1",
            min_correct_ans=20,
            subject=cls.subject,
            time_limit=20,
            num_questions=30,
        )
        cls.question = Question.objects.create(
            description="What is this?", chapter=cls.chapter
        )
        cls.answer = Answer.objects.create(question=cls.question, content="Yes")

    def test_content_label(self):
        answer = self.answer
        field_label = answer._meta.get_field("content").verbose_name
        self.assertEqual(field_label, "content")

    def test_content_max_length(self):
        answer = self.answer
        max_length = answer._meta.get_field("content").max_length
        self.assertEqual(max_length, 1000)

    def test_answer_question_relationship(self):
        answer = self.answer
        self.assertEqual(answer.question, self.question)
