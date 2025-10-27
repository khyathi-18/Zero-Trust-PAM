import logging
import os
from datetime import datetime

# Create logs folder if not exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
logging.basicConfig(
    filename="logs/access.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def detect_anomaly(event_line):
    """
    Simple anomaly detection: prints alert if event contains 'denied'
    """
    if "denied" in event_line.lower():
        print(f"[ALERT] Suspicious activity detected: {event_line}")

def log_event(username, endpoint, action, status):
    """
    Log an access event and detect anomalies
    """
    msg = f"User: {username}, Endpoint: {endpoint}, Action: {action}, Status: {status}"
    logging.info(msg)
    
    # <-- This is where we call anomaly detection -->
    detect_anomaly(msg)
