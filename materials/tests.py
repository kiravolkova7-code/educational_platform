from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from materials.models import Course, Lesson
from django.contrib.auth.models import Group


class LessonsAPITests(APITestCase):
    """
    Тестирование CRUD операций над уроками.
    """

    @classmethod
    def setUpTestData(cls):
        """Создаём общие объекты один раз для всего набора тестов."""
        cls.user_owner = User.objects.create_user(
            email="owner@example.com", password="pass"
        )
        cls.user_regular = User.objects.create_user(
            email="regular@example.com", password="pass"
        )

        cls.user_moderator = User.objects.create_user(
            email="moderator@example.com", password="pass"
        )
        moderators_group, _ = Group.objects.get_or_create(name="moderators")
        cls.user_moderator.groups.add(moderators_group)

        cls.course_1 = Course.objects.create(
            title="Тестовый курс", owner=cls.user_owner
        )
        cls.course_2 = Course.objects.create(title="Другой курс")

        cls.client = APIClient()

        cls.lesson = Lesson.objects.create(
            title="Тестовый урок",
            course=cls.course_1,
            order=2,
            owner=cls.user_owner,
            video_url="https://www.youtube.com/watch?v=example",
        )

    # Часть 1: Тесты CRUD уроков

    def test_list_lessons_as_owner(self):
        self.client.force_authenticate(user=self.__class__.user_owner)
        response = self.client.get(reverse("materials:lesson-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_lessons_as_regular_user(self):
        self.client.force_authenticate(user=self.__class__.user_regular)
        response = self.client.get(reverse("materials:lesson-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_lessons_as_moderator(self):
        self.client.force_authenticate(user=self.__class__.user_moderator)
        response = self.client.get(reverse("materials:lesson-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson_success(self):
        self.client.force_authenticate(user=self.__class__.user_owner)
        lesson_data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_url": "https://www.youtube.com/watch?v=example",
            "order": 1,
            "course": self.__class__.course_1.id,
        }
        response = self.client.post(
            reverse("materials:lesson-list"), data=lesson_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_forbidden_for_moderator(self):
        self.client.force_authenticate(user=self.__class__.user_moderator)
        lesson_data = {
            "title": "Урок модератора",
            "description": "",
            "video_url": "https://www.youtube.com/watch?v=test",
            "order": 1,
            "course": self.__class__.course_1.id,
        }
        response = self.client.post(
            reverse("materials:lesson-list"), data=lesson_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_lesson(self):
        lesson = Lesson.objects.create(
            title="Мой урок",
            course=self.__class__.course_1,
            order=1,
            owner=self.__class__.user_owner,
        )
        self.client.force_authenticate(user=self.__class__.user_owner)
        update_data = {"title": "Обновлённый урок"}
        response = self.client.patch(
            reverse("materials:lesson-detail", args=[lesson.pk]),
            data=update_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_lesson = Lesson.objects.get(pk=lesson.pk)
        self.assertEqual(updated_lesson.title, "Обновлённый урок")

    def test_delete_own_lesson(self):
        lesson = Lesson.objects.create(
            title="Урок для удаления",
            course=self.__class__.course_1,
            order=1,
            owner=self.__class__.user_owner,
        )

        self.client.force_authenticate(user=self.__class__.user_owner)
        response = self.client.delete(
            reverse("materials:lesson-detail", args=[lesson.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.__class__.user_moderator)
        response = self.client.delete(
            reverse("materials:lesson-detail", args=[lesson.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        admin = User.objects.create_superuser(
            email="admin@example.com", password="pass"
        )
        self.client.force_authenticate(user=admin)
        response = self.client.delete(
            reverse("materials:lesson-detail", args=[lesson.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionsAPITests(APITestCase):
    """
    Тестирование функционала подписок.
    """

    @classmethod
    def setUpTestData(cls):
        """Создаём общие объекты один раз для всего набора тестов."""
        cls.user_regular = User.objects.create_user(
            email="regular@example.com", password="pass"
        )

        cls.course_1 = Course.objects.create(
            title="Тестовый курс", owner=cls.user_regular
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_subscription_flow(self):
        user = self.__class__.user_regular
        course_id = self.__class__.course_1.id

        self.client.force_authenticate(user=user)

        sub_response = self.client.post(
            "/subscription/", data={"course_id": course_id}, format="json"
        )
        self.assertEqual(sub_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sub_response.data["message"], "подписка добавлена")

        detail_response = self.client.get(
            reverse(
                "materials:course-detail", args=[self.__class__.course_1.id]
            )
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertTrue(detail_response.data["is_subscribed"])

        unsub_response = self.client.post(
            "/subscription/", data={"course_id": course_id}, format="json"
        )
        self.assertEqual(unsub_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unsub_response.data["message"], "подписка удалена")

        detail_response_after = self.client.get(
            reverse(
                "materials:course-detail", args=[self.__class__.course_1.id]
            )
        )
        self.assertFalse(detail_response_after.data["is_subscribed"])
