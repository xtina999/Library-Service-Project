from django.db import models
from django.conf import settings
from book.models import Book


class Borrowing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title}"

    def calculate_borrowing_total_price(self):
        FINE_MULTIPLIER = 2
        daily_fee = self.book.daily_fee
        borrow_days = (self.actual_return_date or timezone.now().date()) - self.borrow_date

        borrow_days = max(borrow_days.days, 1)

        borrowing_total_price = daily_fee * borrow_days

        if self.actual_return_date and self.actual_return_date > self.expected_return_date:
            overdue_days = (self.actual_return_date - self.expected_return_date).days
            borrowing_total_price += overdue_days * daily_fee * FINE_MULTIPLIER

        return borrowing_total_price


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class Type(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Status.PENDING
    )
    borrowing = models.ForeignKey(
        "borrowings.Borrowing",
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(blank=True, null=True)  # Ensure this field is optional
    session_id = models.CharField(max_length=255, blank=True, null=True)  # Ensure this field is optional
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        if not self.money_to_pay:
            self.money_to_pay = self.borrowing.calculate_borrowing_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.type} - {self.status} - ${self.money_to_pay}'
