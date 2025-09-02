
import os, json, typing as t
from flask import Blueprint, request, abort, current_app

bp = Blueprint('stripe_webhooks', __name__)

@bp.route('/webhook', methods=['POST'])
def webhook():
    # Lazy import so the app can run without stripe installed in some envs
    try:
        import stripe  # type: ignore
    except Exception:
        current_app.logger.warning("Stripe not installed; skipping verify")
        return ('', 204)

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', '')
    secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    if not secret:
        current_app.logger.warning("STRIPE_WEBHOOK_SECRET missing; ignoring event")
        return ('', 204)

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=secret
        )
    except Exception as e:
        current_app.logger.exception("Stripe signature verification failed")
        abort(400)

    # Minimal routing; extend as you integrate checkout/session events
    typ = event.get('type')
    data = event.get('data', {}).get('object', {})
    current_app.logger.info("Stripe event: %s id=%s", typ, data.get('id'))

    if typ == 'checkout.session.completed':
        # TODO: mark sponsorship as paid, emit VIP event if amount_total >= 250000 (cents)
        pass
    elif typ == 'checkout.session.expired':
        # TODO: restore slots or cleanup holds
        pass

    return ('', 200)
