import requests
from .subscription_gateway import PaymentGateWay, SubscriptionPlan
import time

class FlutterwaveGateway(PaymentGateWay):
    def __init__(self):
        self.base_url = "https://api.flutterwave.com/v3"
        self.secret_key = self.get_config()["secret_key"]
        self.public_key = self.get_config()["public_key"]

    async def create_checkout_session(
            self,
            tenant_id: str,
            plan: SubscriptionPlan,
            success_url: str,
            cancel_url: str,
    ):
        headers = {"Authorization": f"Bearer {self.secret_key}"}

        payload = {
            "tx_ref": f"tenant_{tenant_id}_{int(time.time())}",
            "amount": plan.price_monthly,
            "currency": "NGN", # Flutterwave Africa default
            "redirect_url": success_url,
            "payment_options": "card, ussd, mobilemoney, transfer",
            "meta": {
                "tenant_id": tenant_id,
                "plan": plan.id,
            },
            "customer": {
                "email": f"billing@{tenant_id}.com",
                "name": tenant_id.replace("_", " ").title()
            },
            "customizations" : {
                "title": "Intelligent Document Assistant Subscription",
                "description": f"{plan.name} Plan = ₦{plan.price_monthly:,.2f}"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/payments",
            json=payload,
            headers=headers
        )
        data = response.json()

        return {
            "url": data["data"]["link"],
            "tx_ref": data["data"]["tx_ref"]
        }
    
    async def handle_webhook(
            self, 
            payload: dict,
            signature: str,
    ):
        # Verify Flutterwave webhook (check tx_ref + hash)
        if payload.get("tx_ref") and self.verify_flutterware_signature_payload(payload):
            return {"status": "handled", "tx_ref": payload["tx_ref"]}
        
        raise ValueError("Invalid Flutterwave webhook")
    
    def get_webhook_secret(self) -> str:
        return self.get_config()["secret_key"]
    
    def get_config(self) -> dict:
        return {
            "public_key":  os.getenv("FLUTTERWAVE_PUBLIC_KEY", ""),
            "secret_key": os.getenv("FLUTTERWAVE_SECRET_KEY", "")
        }