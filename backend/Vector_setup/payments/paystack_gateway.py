import paystack # pip install paystack-python

from .subscription_gateway import PaymentGateWay, SubscriptionPlan

class PaystackGateway(PaymentGateWay):

    def __init__(self):
        paystack.api_key = self.get_config()["secret_key"]

    async def create_checkout_session(
            self,
            tenant_id: str,
            plan: SubscriptionPlan,
            success_url: str,
            cancel_url: str,
            
            ):
        # Paystack uses transaction.create() -> redirect_url
        transaction = paystack.transaction.initialize(
            amount=init(plan.price_monthly * 100), # kobo
            email="tenant@example.com",
            callback_url=success_url,
            metadata={"tenant_id": tenant_id, "plan": plan.id}
            
        )
        return {"url": transaction["data"]["authorization_url"]}
    
    async def hanlde_webhook(
            self,
            payload: dict,
            signature: str,
    ):
        # Verify paystack signature
        if not paystack.util.verify_signature(payload, signature):
            raise ValueError("Invalid signature")
        
    def get_webhook_secret(self) -> str:
        return self.get_config()["secret_key"] # Paystack uses API key
        
         