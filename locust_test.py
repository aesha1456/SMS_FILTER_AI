from locust import HttpUser, task, between
import random

# Pool of sample SMS messages for testing
test_sms_pool = [
    "Your OTP is 1234. Do not share it with anyone.",
    "Check out our sale at https://trip.com",
    "You've won a prize! Claim now: https://fakewebsite.com",
    "Your package with tracking ID 12345 has been shipped.",
    "Urgent: Verify your account at https://verify-now.online",
    "Thank you for shopping with us!",
    "Reset your password now at https://get-rich-fast.biz"
]

# Optional senders corresponding to whitelist
senders_pool = [
    "VM-ICICIBK",
    "VK-AMAZON",
    "VM-AXISBK",
    "VK-FLIPKART",
    "VM-PAYTM"
]

class SimulatedSMSUser(HttpUser):
    host = "http://127.0.0.1:8000"  # FastAPI server URL
    wait_time = between(0.5, 2)     # Slightly longer pause

    @task
    def submit_sms(self):
        sms_text = random.choice(test_sms_pool)
        sender_id = random.choice(senders_pool)  # Optional sender_id
        response = self.client.post(
            "/check_sms",
            json={"message": sms_text, "sender_id": sender_id},
            headers={"Content-Type": "application/json"}
        )
        # Log status for debugging
        print(f"Sent: {sms_text[:50]}... | Status: {response.status_code} | Response: {response.json()}")
