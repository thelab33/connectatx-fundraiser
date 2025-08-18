# tests/test_payments.py
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify

from app.services.payments import PaymentService

@pytest.fixture
def app():
    """Minimal Flask app with config for PaymentService."""
    app = Flask(__name__)
    app.config.update(
        STRIPE_SECRET_KEY="sk_test_mock",
        STRIPE_PUBLIC_KEY="pk_test_mock",
        PAYPAL_ENV="sandbox",
        PAYPAL_CLIENT_ID="paypal_client_id_mock",
        PAYPAL_SECRET="paypal_secret_mock",
    )
    return app

# ─────────────────────────────────────────────────────────────
# Stripe Tests
# ─────────────────────────────────────────────────────────────

@patch("stripe.PaymentIntent.create")
def test_stripe_intent_success(mock_create, app):
    mock_create.return_value = MagicMock(client_secret="pi_secret_123")
    data = {"amount": 25}  # $25

    with app.app_context():
        result = PaymentService.create_stripe_intent(data)

    assert "client_secret" in result
    assert result["client_secret"] == "pi_secret_123"
    mock_create.assert_called_once()

@patch("stripe.PaymentIntent.create")
def test_stripe_invalid_amount(mock_create, app):
    data = {"amount": 0.50}  # 50 cents (invalid)

    with app.app_context():
        with pytest.raises(Exception) as e:
            PaymentService.create_stripe_intent(data)

    assert "Minimum" in str(e.value)
    mock_create.assert_not_called()

# ─────────────────────────────────────────────────────────────
# PayPal Tests
# ─────────────────────────────────────────────────────────────

@patch("requests.post")
def test_paypal_order_success(mock_post, app):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "ORDER123"}
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    with app.app_context():
        data = {"amount": 10}
        result = PaymentService.create_paypal_order(data)

    assert result["order_id"] == "ORDER123"
    mock_post.assert_called()

@patch("requests.post")
def test_paypal_capture_success(mock_post, app):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "status": "COMPLETED",
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {"status": "COMPLETED", "amount": {"value": "15.00"}}
                    ]
                }
            }
        ]
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    with app.app_context():
        result = PaymentService.capture_paypal_order("ORDER123")

    assert result["status"] == "COMPLETED"
    assert result["amount"] == 15.00
    mock_post.assert_called()

def test_paypal_capture_missing_order_id(app):
    with app.app_context():
        with pytest.raises(Exception) as e:
            PaymentService.capture_paypal_order("")
    assert "Missing order_id" in str(e.value)

