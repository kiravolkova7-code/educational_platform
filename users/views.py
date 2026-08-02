from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import User, Payment, Course
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserAvatarUpdateSerializer,
    RegisterSerializer,
    PaymentSerializer,
)
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .services import (
    create_stripe_product,
    create_stripe_price,
    create_checkout_session,
)


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AvatarUpdateView(generics.UpdateAPIView):
    serializer_class = UserAvatarUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserProfileSerializer(instance).data)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Endpoint: /api/payments/
    Метод POST инициирует создание продукта/цены/сессии в Stripe
    и возвращает готовую ссылку на оплату.
    """

    queryset = Payment.objects.select_related("user", "paid_course").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        print("Данные от пользователя:", request.data)

        course_id = request.data.get("paid_course")
        if not course_id:
            return Response(
                {"detail": "Укажите ID курса."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course = get_object_or_404(Course, id=course_id)

            price_rub = getattr(course, "price", 4990)
            amount_cents = int(price_rub * 100)

            with transaction.atomic():
                payment = Payment.objects.create(
                    user=request.user,
                    paid_course=course,
                    amount_rub=price_rub,
                    amount_cents=amount_cents,
                    payment_url="",
                )

                if not course.stripe_product_id:
                    prod_resp = create_stripe_product(course.title)
                    if not prod_resp["success"]:
                        raise Exception(prod_resp["error"])

                    course.stripe_product_id = prod_resp["data"]["id"]
                    course.save()

                price_resp = create_stripe_price(
                    course.stripe_product_id, amount_cents
                )
                if not price_resp["success"]:
                    raise Exception(price_resp["error"])

                price_id = price_resp["data"]["id"]

                domain = "http://127.0.0.1:8000"

                success_url = f"{domain}/payment-success/?session_id={{CHECKOUT_SESSION_ID}}"
                cancel_url = f"{domain}/payment-cancel/"

                session_resp = create_checkout_session(
                    price_id=price_id,
                    success_url=success_url,
                    cancel_url=cancel_url,
                    client_reference_id=str(payment.id),
                )

                if not session_resp["success"]:
                    raise Exception(session_resp["error"])

                payment.payment_url = session_resp["data"]["url"]
                payment.save()

            headers = self.get_success_headers(PaymentSerializer(payment).data)
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        except Exception as e:
            print("Ошибка создания платежа:", str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя с проверкой дубликатов."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if "email" in str(e).lower():
                return Response(
                    {"error": "Пользователь с таким Email уже существует."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update"]:
            return [permissions.IsAuthenticated()]
        if self.action == "destroy":
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CreateStripePaymentView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        amount_rub = 4990
        amount_cents = int(amount_rub * 100)

        with transaction.atomic():
            payment = Payment.objects.create(
                user=request.user,
                paid_course=course,
                amount_rub=amount_rub,
                amount_cents=amount_cents,
                status="pending",
            )

            if not course.stripe_product_id:
                prod_response = create_stripe_product(course.title)
                if not prod_response["success"]:
                    payment.delete()
                    return JsonResponse(
                        {"error": prod_response["error"]}, status=400
                    )

                course.stripe_product_id = prod_response["data"]["id"]
                course.save()

            price_response = create_stripe_price(
                stripe_product_id=course.stripe_product_id,
                amount_cents=amount_cents,
            )
            if not price_response["success"]:
                payment.delete()
                return JsonResponse(
                    {"error": price_response["error"]}, status=400
                )

            price_id = price_response["data"]["id"]

            domain = settings.DOMAIN_NAME
            success_url = domain + reverse("payment-success")
            cancel_url = domain + reverse("payment-cancel")

            session_response = create_checkout_session(
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(payment.id),
            )

            if not session_response["success"]:
                payment.delete()
                return JsonResponse(
                    {"error": session_response["error"]}, status=400
                )

            session_data = session_response["data"]
            payment.payment_url = session_data["url"]
            payment.stripe_session_id = session_data["id"]
            payment.save()

        return JsonResponse({"redirect_url": payment.payment_url})
