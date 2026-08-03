from materials.apps import MaterialsConfig
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from materials.views import CourseViewSet, LessonViewSet

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")

urlpatterns = [
    path("", include(router.urls)),
]
