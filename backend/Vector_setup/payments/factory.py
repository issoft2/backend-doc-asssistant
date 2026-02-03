# Swtich in 1 Line
import os
from .subscription_gateway import PaymentGateWay
from .stripe_gateway import StripeGatway
from .paystack_gateway import PaystackGateway

PROVIDERS = {
    "stripe": StripeGatway,
    "paystack": PaystackGateway,
    "flutterwave": FlutterwaveGateway, # add later
}

async def get_payment_geteway() -> PaymentGateWay:
    provider = os.getenv("PAYMENT_PROVIDER", "stripe")
    return PROVIDERS[provider]()
  