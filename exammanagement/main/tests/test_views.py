from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from main.models import Chapter, Profile, Subject, Test


class SubjectListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        num_of_subjects = 9

        for subject_id in range(num_of_subjects):
            Subject.objects.create(
                name=f"Subject {subject_id}", description=f"Description {subject_id}"
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/main/subjects/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_acessible_by_name(self):
        response = self.client.get(reverse("subjects"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("subjects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/subject_list.html")

    def test_pagination_is_six(self):
        response = self.client.get(reverse("subjects"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["subject_list"]) == 6)

    def test_lists_all_subjects(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse("subjects") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["subject_list"]) == 3)


class SubjectDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(
            name="Subject test", description="Description test"
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f"/main/subject/{self.subject.pk}")
        self.assertEqual(response.status_code, 200)

    def test_view_url_acessible_by_name(self):
        response = self.client.get(
            reverse(
                "subject-detail",
                kwargs={"pk": self.subject.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse(
                "subject-detail",
                kwargs={"pk": self.subject.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/subject_detail.html")


class ChapterDetailViewTest(TestCase):
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
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(f"/main/chapter/{self.chapter.pk}")
        self.assertEqual(response.status_code, 200)

    def test_view_url_acessible_by_name(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse(
                "chapter-detail",
                kwargs={"pk": self.chapter.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse(
                "chapter-detail",
                kwargs={"pk": self.chapter.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/chapter_detail.html")


class ProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test")
        cls.profile = Profile.objects.create(
            user=cls.user, introduction="Hello", date_of_birth="2023-10-02"
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f"/main/profile/{self.profile.pk}")
        self.assertEqual(response.status_code, 200)

    def test_view_url_acessible_by_name(self):
        response = self.client.get(
            reverse(
                "user-profile",
                kwargs={"pk": self.profile.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse(
                "user-profile",
                kwargs={"pk": self.profile.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/user_profile.html")
