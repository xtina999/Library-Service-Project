import stripe
from django.conf import settings

from borrowings.models import Borrowing

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing):
    try:
        payment = borrowing.payments.first()  # Assuming there's only one payment per borrowing

        if payment:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": 'usd',
                        "product_data": {
                            "name": borrowing.book.title,
                        },
                        "unit_amount": int(payment.money_to_pay * 100),  # Convert to cents
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
            payment.session_url = session.url
            payment.session_id = session.id
            payment.save()

            return session.url, session.id
        return None, None
    except Exception as e:
        print(f"Error creating Stripe session: {e}")
        return None, None
