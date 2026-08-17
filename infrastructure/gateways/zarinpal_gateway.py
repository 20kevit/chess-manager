import os
import requests
from typing import Optional
from application.payment_gateway_interface import (
    PaymentGatewayInterface, PaymentRequestResult, PaymentVerifyResult
)

class ZarinpalGateway(PaymentGatewayInterface):
    def __init__(self):
        self.merchant_id = os.environ.get("ZARINPAL_MERCHANT_ID", "00000000-0000-0000-0000-000000000000")
        self.is_sandbox = os.environ.get("ZARINPAL_SANDBOX", "true").lower() == "true"
        
        if self.is_sandbox:
            self.base_api_url = "https://sandbox.zarinpal.com/pg/v4/payment"
            self.base_pay_url = "https://sandbox.zarinpal.com/pg/StartPay"
        else:
            self.base_api_url = "https://api.zarinpal.com/pg/v4/payment"
            self.base_pay_url = "https://www.zarinpal.com/pg/StartPay"

    def request_payment(self, amount: int, description: str, callback_url: str) -> PaymentRequestResult:
        url = f"{self.base_api_url}/request.json"
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10,  # Convert Toman to Rial for Zarinpal API
            "description": description,
            "callback_url": callback_url
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and data["data"].get("authority"):
                authority = data["data"]["authority"]
                payment_url = f"{self.base_pay_url}/{authority}"
                return PaymentRequestResult(authority=authority, payment_url=payment_url)
            else:
                errors = data.get("errors", {})
                raise ValueError(f"Zarinpal request failed: {errors}")
                
        except requests.RequestException as e:
            raise ValueError(f"Network error connecting to Zarinpal: {str(e)}")

    def verify_payment(self, authority: str, amount: int) -> PaymentVerifyResult:
        url = f"{self.base_api_url}/verify.json"
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10,
            "authority": authority
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and data["data"].get("code") == 100:
                return PaymentVerifyResult(
                    is_successful=True,
                    ref_id=str(data["data"].get("ref_id", "")),
                    card_mask=data["data"].get("card_pan", "")
                )
            else:
                errors = data.get("errors", {})
                return PaymentVerifyResult(
                    is_successful=False,
                    error_message=f"Verification failed: {errors}"
                )
                
        except requests.RequestException as e:
            return PaymentVerifyResult(
                is_successful=False,
                error_message=f"Network error during verify: {str(e)}"
            )