# SMS Spam Filter

A robust and production-ready SMS classification system built with **FastAPI** and **Docker**, capable of distinguishing between **Transactional**, **Promotional**, and **Spam** messages. The system combines **machine learning classification** with **rule-based logic** (whitelisting and suspicious domain detection) for maximum accuracy and minimal false positives.

---

## 🏗️ System Architecture / Pipeline Flow

```mermaid
flowchart TD
    A[Incoming SMS Message] --> B[API Endpoint: /check_sms]

    B --> C[Whitelist / Blacklist Check]
    C -->|Whitelisted - Trusted Domains / Phrases| D[Directly Allowed ✅]
    C -->|Suspicious Domain / Blacklisted| E[Blocked ❌]
    C -->|Not Listed| F[AI Classifier - ML Model spam_model.pkl]

    F --> G{Category Prediction}
    G -->|Transactional| H[Allowed with High Priority ⚡]
    G -->|Promotional| I[Allowed/Flagged with Confidence Score 📊]
    G -->|Spam| J[Blocked 🚫]
  
    H --> L[Final Verdict]
    I --> L
    J --> L
    

    L --> M[Response JSON: verdict, category, confidence, reason]



```

---

## What it does

Classifies SMS messages into 3 categories:

* Spam: Malicious/unwanted messages
* Promotional: Marketing content
* Transactional: Service messages (OTPs, receipts)

## 📊 Dataset

* **Size**: 12,060 labeled SMS messages
* **Balance**: 4,020 per category (*Spam*, *Promotional*, *Transactional*)
* **Quality**: Curated to ensure even distribution and reduce bias
* **Result**: Perfect confusion matrix during evaluation (no misclassifications)

---


## 🧪 Model Performance

* **Accuracy**: 100% on test data
* **Cross-validation score**: 99.97%
* **Latency**: \~2.71ms average inference time
* **Reliability**: Zero misclassifications recorded in test runs

---

## ⚡ API Benchmarking

* **Throughput**: 192.6 requests per second sustained under load
* **Response time**: 450ms median (100 concurrent users)
* **Failures**: 0 errors out of 18,561 requests
* **Deployment Footprint**: \~200MB Docker image, \~512MB memory runtime

---
## Technical Details

**ML Model:**

* Algorithm: Logistic Regression
* Features: TF-IDF (5,000 features)
* Vectorized data shape: (9648, 5000)
* Training: 9,648 samples
* Testing: 2,412 samples

**Docker:**

* Base: python:3.11-slim
* Size: \~200MB
* Memory: \~512MB runtime
* Startup: <10 seconds

## 🏗️ Project Structure

```
SMS-FILTER-AI/
├── Dockerfile                 # Container setup
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── test_sms_filter.py         # Unit tests
├── locust_test.py              # Load testing configuration
├── config/
│   └── whitelist.json         # Trusted domains & phrases
|   └── settings.json          # Set spam block threshold
├── data/
│   └── preprocessed_data
|   |   └── labeled_sms_dataset_FINAL.csv
|   |   └── preprocessing.ipynb
|   └── raw
|       └── message_dataset_50k.csv
├── logs/
│   └── application.log
├── models/
│   ├── sms_classifier.pkl     # Trained classifier
│   └── tfidf_vectorizer.pkl   # TF-IDF feature extractor
|   └── preprocessing.ipynb 
└── src/
    └── filter_engine.py       # Core filtering and detection logic
```

---

## 🧩 Core Components

1. **Filter Engine** ([`src/filter_engine.py`](src/filter_engine.py))

   * Extracts domains from messages
   * Compares against trusted whitelist
   * Runs ML-based classification (TF-IDF + Logistic Regression)
   * Detects known malicious domains

2. **API Layer** ([`main.py`](main.py))

   * Exposes `/check-sms` endpoint
   * Handles request validation and error responses
   * Outputs structured JSON verdicts

3. **Configuration**  ([`config/whitelist.json`](config/whitelist.json))

   * Stores safe domains (e.g., *amazon.in, flipkart.com*)
   * Stores safe phrases (e.g., *“your otp is”*)
   * Editable without touching code

---


## 📜 Logging

Logs (`logs/app.log`) capture:

* Timestamp of request
* Message category & confidence score
* Whitelist/blacklist matches
* Processing time

---

## 🔒 Security Highlights

* Input validation prevents malformed requests
* No storage of sensitive SMS data
* Configurable whitelist/blacklist
* Domain-based filtering for known scams
* Ready for rate limiting / middleware protection

---

## ✅ Whitelisting

**Domain-based** and **phrase-based** logic ensures legitimate services are never flagged.

Example entries [`config/whitelist.json`](config/whitelist.json):

```json
{
  "domains": [
    "trip.com",
    "amazon.in",
    "flipkart.com",
    "myntra.com",
    "icicibank.com",
    "airtel.in",
    "bluedart.com",
    "secure.bankportal.in",
    "officialstore.com",
    "paytm.com",
    "zomato.com",
    "ola.in",
    "flipkartpayments.com",
    "swiggy.com",
    "amazonpay.in"
  ],
  
  "phrases": [
    "your otp is",
    "payment successful",
    "thank you for shopping",
    "transaction id",
    "logged into account",
    "tracking id",
    "invoice for order",
    "booking confirmed",
    "shipped",
    "wallet credited",
    "order delivered",
    "promo code applied",
    "subscription activated",
    "payment received",
    "delivery scheduled"
  ],
  
  "senders": [
    "VM-ICICIBK",
    "VK-AMAZON",
    "VM-AXISBK",
    "VK-FLIPKART",
    "VM-PAYTM",
    "VK-SBIOTP",
    "VM-HDFC",
    "VK-PHONEPE",
    "VM-YESBANK",
    "VK-ICICILOAN"
]
}

```

Example messages:

* `"Your OTP is 456789"` → Always Transactional (phrase match)
* `"Check offers at https://amazon.in/deals"` → Always Promotional (domain match)

---

## 🚨 Suspicious Domain Detection

Embedded blacklist inside `filter_engine.py`:

```python
SUSPICIOUS_DOMAINS = [
    "fakewebsite.com",
    "verify-now.online",
    "login-now-security.xyz"
]
```

Messages containing these are **immediately blocked** with high confidence.

---

## 🚀 Quick Start

### Run with Docker (Recommended)

```bash
docker build -t sms-spam-filter .
docker run -d -p 8000:8000 --name sms-filter sms-spam-filter
```

### Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📡 API Usage

**Health Check**

```bash
curl http://localhost:8000/
```

**Check SMS**

```bash
curl -X POST "http://localhost:8000/check-sms" \
  -H "Content-Type: application/json" \
  -d '{"message": "Your OTP is 1234"}'
```

---

## 🔍 Real API Examples

**1. Promotional (Whitelisted Domain):**

```bash
curl -X POST "http://localhost:8000/check-sms" \
  -H "Content-Type: application/json" \
  -d '{"message": "Big sale today at https://amazon.com"}'
```

Response:

```json
{"verdict": "allowed", "reason": "whitelisted"}
```

**2. Spam (Suspicious Domain):**

```bash
curl -X POST "http://localhost:8000/check-sms" \
  -H "Content-Type: application/json" \
  -d '{"message": "Win cash now at https://fakewebsite.com"}'
```

Response:

```json
{"verdict": "blocked", "reason": "suspicious_domain", "matched_domain": "fakewebsite.com"}
```

**3. Transactional (AI Domain):**

```bash
curl -X POST "http://127.0.0.1:8000/check_sms" \
  -H "Content-Type: application/json" \
  -d '{"message\":\"Your order #98765 has been shipped and will arrive tomorrow."}'
```

Response:

```json
{"verdict":"allowed","reason":"ai","category":"Transactional","confidence":1.0}

```

---

**4. Promotional (AI Domain):**

```bash
curl -X POST "http://127.0.0.1:8000/check_sms" \
  -H "Content-Type: application/json" \
  -d '{"message\":\"Big sale! Get 50% off today on all items!."}'
```

Response:

```json
{"verdict":"allowed","reason":"ai","category":"Promotional","confidence":1.0}

```
**5. Spam Message (AI Domain):**

```bash
curl -X POST "http://127.0.0.1:8000/check_sms" \
  -H "Content-Type: application/json" \
  -d '{"message\":"Congratulations! You won $1000. Click http://fakewebsite.com to claim."}'
```

Response:

```json
{"verdict":"allowed","reason":"ai","confidence":1.0}

```

**6. Empty Message:**

```bash
curl -X POST "http://localhost:8000/check-sms" \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

**Response:**

```json
{"detail": "Empty message"}
```

---

## 🔧 Load Testing

Sample Locust script (`locustfile.py`):

```python
from locust import HttpUser, task, between
import random
test_sms_pool = [
    "Your OTP is 1234. Do not share it with anyone.",
    "Check out our sale at https://trip.com ",
    "You've won a prize! Claim now: https://fakewebsite.com ",
    "Thank you for shopping with us!", "Your package with tracking ID 12345 has been shipped.",
    "Urgent: Verify your account at https:
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
```

Run test:

```bash
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10
```

---

## 📌 Future Enhancements

* Live retraining from incoming traffic
* Multilingual SMS support
* Admin panel for whitelist/blacklist management
* Analytics dashboard for spam trends
* Webhook integrations for real-time alerts

---

## 🏁 Summary

This SMS filter system combines **AI classification**, **domain analysis**, and **configurable whitelisting** to deliver **lightning-fast**, **accurate**, and **secure** SMS filtering. Tested on a balanced dataset with perfect accuracy and stress-tested under load, it is ready for deployment in real telecom-grade environments.



