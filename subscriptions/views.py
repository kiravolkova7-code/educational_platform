from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from materials.models import Course
from subscriptions.models import Subscription


class UserCourseSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course_item = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        subs_queryset = Subscription.objects.filter(
            user=user, course=course_item
        )

        if subs_queryset.exists():
            subs_queryset.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
