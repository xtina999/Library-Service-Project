import logging

from celery import shared_task
from django.utils import timezone
from .models import Borrowing
from .utils import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_borrowings():
    logger.info("Starting check_overdue_borrowings task.")
    now = timezone.now().date()
    logger.info(f"Current date: {now}")

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=now,
        actual_return_date__isnull=True
    )
    logger.info(f"Found {overdue_borrowings.count()} overdue borrowings.")

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue borrowing:\n"
                f"Book: {borrowing.book.title}\n"
                f"Borrower: {borrowing.user.email}\n"
                f"Expected return date: {borrowing.expected_return_date.strftime('%Y-%m-%d')}"
            )
            logger.info(f"Sending message: {message}")
            send_telegram_message(message)
    else:
        logger.info("No borrowings overdue today.")
        send_telegram_message("No borrowings overdue today!")

    logger.info("Finished check_overdue_borrowings task.")
