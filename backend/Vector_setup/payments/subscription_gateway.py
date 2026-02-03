from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
import asyncio

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_mothly: float
    max_docs: int
    max_queries: int

class PaymentGateWay(ABC):
    """unfied interface for all payment providers"""

    @abstractmethod
    async def create_checkout_session(
        self,
        tenant_id: str,
        plan: SubscriptionPlan,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:  # Returns {url: "...."}
        pass


    @abstractmethod
    async def create_portal_session(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:  # Returns {url: "...."}
        pass
    

    @abstractmethod
    def handle_webhook(self) -> str:
        pass

