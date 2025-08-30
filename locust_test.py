from locust import HttpUser, task, between
import random

# Pool of sample SMS messages for testing
test_sms_pool = [
    "Your OTP is 1234. Do not share it with anyone.",
    "Check out our sale at https://trip.com ",
    "You've won a prize! Claim now: https://fakewebsite.com ",
    "Your package with tracking ID 12345 has been shipped.",
    "Urgent: Verify your account at https://verify-now.online ",
    "Thank you for shopping with us!",
    "Reset your password now at https://get-rich-fast.biz "
]

class SimulatedSMSUser(HttpUser):

    host = "http://127.0.0.1:8000"  # Update to your FastAPI server URL if needed
    wait_time = between(0.01, 0.1)   # Random pause between requests

    @task
    def submit_sms(self):
        sms_text = random.choice(test_sms_pool)
        self.client.post(
            "/check_sms",
            json={"message": sms_text},
            headers={"Content-Type": "application/json"}
        )
