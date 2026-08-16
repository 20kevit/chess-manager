from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class PaymentRequestResult:
    authority: str
    payment_url: str

@dataclass
class PaymentVerifyResult:
    is_successful: bool
    ref_id: Optional[str] = None
    card_mask: Optional[str] = None
    error_message: Optional[str] = None

class PaymentGatewayInterface(ABC):
    @abstractmethod
    def request_payment(self, amount: int, description: str, callback_url: str) -> PaymentRequestResult:
        """درخواست توکن از درگاه"""
        pass
        
    @abstractmethod
    def verify_payment(self, authority: str, amount: int) -> PaymentVerifyResult:
        """تأیید پرداخت"""
        pass