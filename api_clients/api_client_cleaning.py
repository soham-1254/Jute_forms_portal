import requests
import json
import warnings

warnings.filterwarnings("ignore")

# ====================================================
# 🌐 API CONFIGURATION
# ====================================================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZCLEANING_API_SRV/FormEntries"
TIMEOUT = 15

# ====================================================
# 🧩 Function to Post Cleaning Data
# ====================================================
def post_to_sap_cleaning(record):
    """
    Sends Cleaning & Gauging form data to Flask + MongoDB Mock Server.
    Returns: "success" if posted successfully, else "failed".
    """
    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Convert to JSON payload
        payload = json.dumps(record, default=str)

        print("\n📤 Sending Cleaning record to Flask Server...")
        print("Payload:", payload)

        # POST request to Flask API
        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            timeout=TIMEOUT,
            verify=False
        )

        if response.status_code in [200, 201]:
            print("✅ Cleaning record successfully inserted into MongoDB!")
            return "success"
        else:
            print(f"❌ Flask endpoint error {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print(f"⚠️ Error while posting Cleaning record: {e}")
        return "failed"
