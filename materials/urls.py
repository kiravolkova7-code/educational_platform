from materials.apps import MaterialsConfig
from rest_framework.routers import DefaultRouter
from django.urls import path
from materials.views import CourseViewSet, LessonList, LessonRetrieve, LessonCreate, LessonUpdate, LessonDestroy

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course')

urlpatterns = [
    path("lessons/", LessonList.as_view(), name='lessons-list'),
    path("lessons/<int:pk>/", LessonRetrieve.as_view(), name='lessons-detail'),
    path("lessons/create/", LessonCreate.as_view(), name='lessons-create'),
    path("lessons/update/<int:pk>/", LessonUpdate.as_view(), name='lessons-update'),
    path("lessons/delete/<int:pk>/", LessonDestroy.as_view(), name='lessons-delete'),
] + router.urls
