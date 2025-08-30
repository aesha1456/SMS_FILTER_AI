from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add src folder to path for importing filter logic
sys.path.append(str(Path(__file__).parent / "src"))

# Import custom filtering module
from filter_engine import sms_filter


# Setup logging
logs_path = Path("logs")
logs_path.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(logs_path / "application.log"),
        logging.StreamHandler()
    ]
)
app_logger = logging.getLogger("A2PSMSFilter")

# Initialize FastAPI app
app = FastAPI(
    title="A2P SMS Safety API",
    description="AI-enhanced SMS filter with whitelist support",
    version="1.0"
)

# Pydantic model for request
class SMSRequest(BaseModel):
    message: str
    sender_id: str | None = None

@app.get("/")
def api_health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "model_ready": True
    }

@app.post("/check_sms")
def check_sms(request: SMSRequest):
    """
    Evaluate SMS for spam, transactional, or promotional classification.
    
    Input: {"message": "Your OTP is 123456"}
    Output: {"verdict": "allowed"|"blocked", "reason": "..."}
    """
    sms_text = request.message.strip()

    if not sms_text:
        app_logger.warning("Rejected empty message")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if len(sms_text) > 1200:
        app_logger.warning(f"Rejected long message ({len(sms_text)} chars)")
        raise HTTPException(status_code=400, detail="Message too long")

    # Run the filtering pipeline
    verdict = sms_filter(sms_text)

    # Log outcome
    app_logger.info(f"{verdict['verdict'].upper()} | '{sms_text[:100]}...' | {verdict['reason']}")
    return verdict

@app.get("/recent_logs")
def view_recent_logs():
    """Retrieve last 50 log entries"""
    try:
        with open(logs_path / "application.log", "r") as log_file:
            lines = log_file.readlines()
        return {"logs": [line.strip() for line in lines[-50:]]}
    except Exception as e:
        return {"error": str(e)}
