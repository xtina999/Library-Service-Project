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


class Payment(models.Model):
    def calculate_borrowing_total_price(self):
        FINE_MULTIPLIER = 2
        daily_fee = self.borrowing.book.daily_fee
        borrow_days = (self.borrowing.actual_return_date or date.today()) - self.borrowing.borrow_date
        borrowing_total_price = daily_fee * borrow_days.days

        if self.borrowing.actual_return_date and self.borrowing.actual_return_date > self.borrowing.expected_return_date:
            overdue_days = (self.borrowing.actual_return_date - self.borrowing.expected_return_date).days
            borrowing_total_price += overdue_days * daily_fee * FINE_MULTIPLIER

        return borrowing_total_price

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
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        if not self.money_to_pay:
            self.money_to_pay = self.calculate_borrowing_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type} - {self.status} - ${self.money_to_pay}"
