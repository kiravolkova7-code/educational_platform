from subscriptions.apps import SubscriptionsConfig
from subscriptions.views import UserCourseSubscriptionView
from django.urls import path

app_name = SubscriptionsConfig.name

urlpatterns = [
    path(
        "",
        UserCourseSubscriptionView.as_view(),
        name="user-course-subscription",
    ),
]
