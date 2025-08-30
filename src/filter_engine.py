# src/filter_engine.py
import re
import json
import joblib
from pathlib import Path

#  Paths 
WHITELIST_PATH = Path(__file__).parent.parent / "config" / "whitelist.json"
MODEL_PATH = Path(__file__).parent.parent / "models" / "sms_classifier.pkl"
VECTORIZER_PATH = Path(__file__).parent.parent / "models" / "tfidf_vectorizer.pkl"

# Load Whitelist 
with open(WHITELIST_PATH, 'r') as file:
    WHITELIST_DATA = json.load(file)

# Suspicious Domains 
BLOCKED_DOMAINS = [
    "secure-update.cards",
    "winfreecash.com",
    "get-rich-fast.biz",
    "confirm-payee.click",
    "iphone14winner.com",
    "fakewebsite.com",
    "login-now-security.xyz",
    "netflix-support.com",
    "urgentupdate.co",
    "verify-now.online"
]
# Load Trained Model & Vectorizer 
sms_model = joblib.load(MODEL_PATH)
tfidf_vectorizer = joblib.load(VECTORIZER_PATH)

# Load settings
SETTINGS_PATH = Path(__file__).parent.parent / "config" / "settings.json"
try:
    SETTINGS = json.loads(SETTINGS_PATH.read_text())
except FileNotFoundError:
    SETTINGS = {"spam_block_threshold": 0.80}


# Helper Functions 
def get_domains_from_text(text):
    """Extract all domains from URLs present in the message."""
    found_urls = re.findall(r'https?://([^\s/]+)', text)
    return [url.strip('www.') for url in found_urls]


def check_whitelist(text, sender_id=None):
    """Return True if the message matches any whitelisted phrase or domain."""
    text_lower = text.lower()

    # Check phrases
    for phrase in WHITELIST_DATA.get("phrases", []):
        if phrase in text_lower:
            return True

    # Check domains
    domains_in_text = get_domains_from_text(text)
    for domain in domains_in_text:
        if any(allowed in domain for allowed in WHITELIST_DATA.get("domains", [])):
            return True
        
    # Check whitelisted sender
    if sender_id and sender_id in WHITELIST_DATA.get("senders", []):
        return True

    return False


def ai_predict_category(text):
    """Predict message category using the trained ML model."""
    cleaned_text = re.sub(r'\s+', ' ', text.lower().strip())
    vectorized = tfidf_vectorizer.transform([cleaned_text])
    predicted_class = sms_model.predict(vectorized)[0]
    probabilities = sms_model.predict_proba(vectorized)[0]
    max_confidence = max(probabilities)
    return predicted_class, max_confidence


# Main Filtering Function 
def sms_filter(message, sender_id=None):
    """Filter SMS using whitelist, suspicious domains, and AI classification."""
    if not message or not message.strip():
        return {"verdict": "blocked", "reason": "empty_message"}

    message = message.strip()

    # STEP 1: Check whitelist
    if check_whitelist(message, sender_id):
        return {"verdict": "allowed", "reason": "whitelisted"}

    # STEP 2: Check known suspicious domains
    message_domains = get_domains_from_text(message)
    for dom in message_domains:
        if any(blocked in dom for blocked in BLOCKED_DOMAINS):
            return {
                "verdict": "blocked",
                "reason": "suspicious_domain",
                "matched_domain": dom
            }

    # STEP 3: AI classification
    category, confidence = ai_predict_category(message)
    confidence = round(confidence, 2)

    if category.lower() == "spam":
        if confidence >= SETTINGS["spam_block_threshold"]:
            return {"verdict": "blocked", "reason": "ai", "confidence": confidence}
        else:
            return {"verdict": "allowed", "reason": "ai_low_confidence", "confidence": confidence}
    else:
        return {
            "verdict": "allowed",
            "reason": "ai",
            "category": category,
            "confidence": confidence
        }
