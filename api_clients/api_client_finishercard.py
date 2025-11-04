import requests
import pandas as pd
import os

# ======================================================
# 🌐 CONFIGURATION
# ======================================================
# Mock server endpoint — must match your mock_server.py route
MOCK_API_URL = "http://localhost:8080/sap/opu/odata/sap/ZFINISHERCARD_API_SRV/FormEntries"

# Fallback CSV in case API call fails
FAILED_PATH = "data/failed_records.csv"

# ======================================================
# 🧠 FUNCTION TO POST DATA TO MOCK SERVER (Flask + MongoDB)
# ======================================================
def post_to_sap_finishercard(payload: dict) -> str:
    """
    Send Finisher Card Sliver Weight data to Flask Mock SAP Server.
    Falls back to saving in failed_records.csv if the connection fails.

    Args:
        payload (dict): Data record to be pushed

    Returns:
        str: 'success' or 'failed'
    """
    try:
        response = requests.post(MOCK_API_URL, json=payload, timeout=10)

        # Handle successful response
        if response.status_code in [200, 201]:
            print("✅ Successfully posted to mock server:", response.json())
            return "success"
        else:
            print(f"⚠️ Server returned status {response.status_code}: {response.text}")
            _save_failed_record(payload)
            return "failed"

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error while posting to mock server: {e}")
        _save_failed_record(payload)
        return "failed"


# ======================================================
# 💾 LOCAL FALLBACK SAVE
# ======================================================
def _save_failed_record(record: dict):
    """Save failed records to a local CSV file."""
    os.makedirs(os.path.dirname(FAILED_PATH), exist_ok=True)
    df = pd.DataFrame([record])

    if os.path.exists(FAILED_PATH) and os.path.getsize(FAILED_PATH) > 0:
        try:
            existing = pd.read_csv(FAILED_PATH)
        except pd.errors.EmptyDataError:
            existing = pd.DataFrame()
    else:
        existing = pd.DataFrame()

    updated = pd.concat([existing, df], ignore_index=True)
    updated.to_csv(FAILED_PATH, index=False)
    print("⚠️ Record saved locally to failed_records.csv")


# ======================================================
# 🔍 SELF TEST
# ======================================================
if __name__ == "__main__":
    # Dummy test record
    sample = {
        "Date": "2025-10-31",
        "Quality": "Hessian",
        "Machine No.": 5,
        "Weight 1 (gm)": 12.5,
        "MR% 1": 10,
        "Actual 1": 13.25,
        "Converted 1": 15.0,
        "Weight 2 (gm)": 12.0,
        "MR% 2": 9.5,
        "Actual 2": 12.70,
        "Converted 2": 14.2,
        "Average Converted": 14.6,
    }

    status = post_to_sap_finishercard(sample)
    print("Post status:", status)
