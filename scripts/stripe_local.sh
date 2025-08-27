#!/usr/bin/env bash
set -euo pipefail
echo "Stripe local helper"
echo "When online:"
echo "  Linux  : curl -fsSL https://cli.stripe.com/install.sh | sudo bash"
echo "  macOS  : brew install stripe/stripe-cli/stripe"
echo "Login   : stripe login"
echo "Listen  : stripe listen --events payment_intent.succeeded,payment_intent.payment_failed \"
echo "          --forward-to http://localhost:5000/webhooks/stripe"
echo "Export  : STRIPE_WEBHOOK_SECRET=whsec_..."
