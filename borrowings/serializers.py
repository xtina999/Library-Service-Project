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


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ['book', 'expected_return_date']

    def validate_book(self, value):
        if value.inventory == 0:
            raise serializers.ValidationError("This book is not available for borrowing.")
        return value

    def create(self, validated_data):
        book = validated_data['book']
        book.inventory -= 1
        book.save()
        borrowing = Borrowing.objects.create(user=self.context['request'].user, **validated_data)
        return borrowing