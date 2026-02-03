from Vector_setup.payments.registry import get_gateway

@router.get("gateways")
async def list_payment_gateways():
    """List all available payment gateways"""
    return {
        "gateways":[ {
            "id": "stripe",
            "name": "Stripe (Global)",
            "currencies": ["USD", "EUR", "GBP"],
            "cards": True,
            "local": False
        },
        {
            "id": "paystack",
            "name": "Paystack (Nigeria)",
            "currencies": ["NGN"],
            "cards": True,
            "bank_transfer": True,
            "ussd": True
        },

        {
            "id": "flutterwave",
            "name": "Flutterwave (Africa)",
            "currencies": ["NGN", "KES", "GHS"],
            "cards": True,
            "mobile_money": True,
            "bank_transfer": True
        }

     ]

    }

@router.post("/checkout")
async def create_checkout(
    provider: str, # User selected provider ("strip", "paystack", "flutterwave")
    plan_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    gateway: PaymentGateWay = Depends(lambda: get_gateway(provider)) # Dynamic!

):
    plan = await get_plan(plan_id)
    session = await gateway.create_checkout_session(
        tenant_id=tenant_id,
        plan=plan,
        success_url="https://yourappcom/success?provider={provider}",
        cancel_url="https://yourapp.com/cancel?provder={provider}"
    )
    return session


@router.post("/{provider}/webhook")
async def provider_webhook(
    provider: str,
    request: Request,
    gateway: PaymentGateWay = Depends(lambda: get_gateway(provider)) # Dynamic!
):
    payload = await request.body()
    signature = request.headers.get("Webhook-Signature") or \
        request.headers.get("x-paystack-signature") or \
        request.headers.get("verif-hash")  # Flutterwave
    

    response = await gateway.handle_webhook(
        payload=payload,
        signature=signature
    )
    await sync_tenant_subscription(payload, provider)

    return {"status": "ok"}
