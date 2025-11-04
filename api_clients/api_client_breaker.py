import requests
import json
import os
import warnings

# Disable SSL warnings (for local Flask testing)
warnings.filterwarnings("ignore")

# ==============================
# 🌐 Breaker Card API CONFIGURATION
# ==============================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZBREAKER_API_SRV/FormEntries"

# Optional dummy credentials (for local mock server)
SAP_USERNAME = os.getenv("SAP_USER", "test_user")
SAP_PASSWORD = os.getenv("SAP_PASS", "test_pass")
SAP_BEARER_TOKEN = os.getenv("SAP_BEARER_TOKEN", None)

TIMEOUT = 15


# ==============================
# 📤 POST FUNCTION
# ==============================
def post_to_sap_breaker(record):
    """
    Push record from Streamlit form to Flask + MongoDB mock SAP OData endpoint.
    """

    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        auth = None
        if SAP_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {SAP_BEARER_TOKEN}"
        else:
            auth = (SAP_USERNAME, SAP_PASSWORD)

        # Add unique form ID
        record_with_id = record.copy()
        record_with_id["FormID"] = f"BREAKER-{record.get('Date', 'NA')}-{record.get('Machine No', 'NA')}"

        payload = json.dumps(record_with_id, default=str)

        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            auth=auth,
            timeout=TIMEOUT,
            verify=False
        )

        # --- Handle Response ---
        if response.status_code in [200, 201]:
            print("✅ Breaker record sent successfully!")
            return "success"
        else:
            print(f"❌ Endpoint error {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print(f"⚠️ Error sending record: {e}")
        return "failed"
