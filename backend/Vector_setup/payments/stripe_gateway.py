import stripe
import os

from .subscription_gateway import  PaymentGateWay, SubscriptionPlan

class StripeGatway(PaymentGateWay):
    def __init__(self):
        stripe.api_key = self.get_config()["secret_key"]

    async def create_checkout_session(
            self, 
            tenant_id: str,
            plan: SubscriptionPlan,
            success_url: str,
            cancel_url: str):
        
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{
                "price": self.get_price_id(plan.id), #prod_starter_mnthly
                "quantity": 1,
                                        
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"tenant_id": tenant_id}
        )
        return {"url": success_url, "session_id": session.id}
    
    def get_webhook_secret(self) -> str:
        return {
            "secret_key": os.getenv("STRIPE_SECRETE_KEY", ""),
            "wehook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", "")
        }
    
    