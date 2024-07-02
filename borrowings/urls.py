from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet, PaymentDetailView, PaymentListView, PaymentSuccessView, PaymentCancelView

router = DefaultRouter()
router.register("", BorrowingViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:borrowing_id>/payments/", PaymentListView.as_view(), name="payment-list"),
    path("<int:borrowing_id>/payments/<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("payments/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

app_name = "borrowing"
