import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')


def create_stripe_product(course_title: str) -> dict:
    try:
        product = stripe.Product.create(
            name=course_title,
        )
        return {'success': True, 'data': product}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': e.user_message or str(e)}


def create_stripe_price(stripe_product_id: str, amount_cents: int, currency: str = 'rub') -> dict:
    if not stripe_product_id:
        return {'success': False, 'error': 'Product ID is required'}

    try:
        price = stripe.Price.create(
            unit_amount=amount_cents,
            currency=currency,
            product=stripe_product_id,
        )
        return {'success': True, 'data': price}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': e.user_message or str(e)}


def create_checkout_session(price_id: str, success_url: str, cancel_url: str, client_reference_id: str = None) -> dict:
    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            client_reference_id=client_reference_id,
        )
        return {'success': True, 'data': session}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': e.user_message or str(e)}
