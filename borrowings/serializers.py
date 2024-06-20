from rest_framework import serializers
from .models import Borrowing
from book.serializers import BookSerializer  # Assuming you have a BookSerializer in book app


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id", "user",
            "book", "borrow_date",
            "expected_return_date", "actual_return_date"
        ]
