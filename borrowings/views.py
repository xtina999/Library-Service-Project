from datetime import date

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Borrowing
from .serializers import BorrowingSerializer, BorrowingCreateSerializer
from .utils import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if user_id:
            if self.request.user.is_staff:
                queryset = queryset.filter(user_id=user_id)
            else:
                queryset = queryset.filter(user=self.request.user, user_id=user_id)

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            borrowing = serializer.save(user=self.request.user)
        else:
            user = serializer.validated_data.get('user', self.request.user)
            borrowing = serializer.save(user=user)

        message = f"New borrowing created:\nUser: {borrowing.user.first_name}{borrowing.user.last_name}({borrowing.user.email})\nBook: {borrowing.book.title}\nExpected Return Date: {borrowing.expected_return_date}"
        send_telegram_message(message)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post", "get"], url_path='return_book')
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if not request.user.is_staff and borrowing.user != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if borrowing.actual_return_date is not None:
            return Response({"detail": "Book already returned"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "POST":
            borrowing.actual_return_date = date.today()
            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data)
