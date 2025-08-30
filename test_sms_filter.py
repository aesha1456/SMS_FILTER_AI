from src.filter_engine import filter_message as run_filter

# Sample messages to test filter logic
sample_sms = [
    "Your OTP is 123456. Do not share it with anyone.",       # Should be whitelisted
    "Check out our sale at https://trip.com ",                # Whitelisted domain
    "You've won! Claim prize at https://fakewebsite.com ",   # Spam
    "Your package has been shipped.",                         # Whitelisted phrase
    "Urgent: Verify now at https://verify-now.online ",       # Spam
    ""                                                        # Empty → blocked
]

# Iterate and test
for sms_text in sample_sms:
    verdict = run_filter(sms_text)
    print(f"Message: '{sms_text}'")
    print(f"Filter Output: {verdict}\n")
