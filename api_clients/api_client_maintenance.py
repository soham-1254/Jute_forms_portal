import requests
import json
import warnings

warnings.filterwarnings("ignore")

# ====================================================
# 🌐 API CONFIGURATION
# ====================================================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZMAINTENANCE_API_SRV/FormEntries"
TIMEOUT = 15

# ====================================================
# 🧩 FUNCTION TO POST DATA
# ====================================================
def post_to_sap_maintenance(record):
    """
    Sends Maintenance Log data to Flask + MongoDB Mock Server.
    Returns: 'success' if posted successfully, else 'failed'.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = json.dumps(record, default=str)

        print("\n📤 Sending Maintenance record to Flask Server...")
        print("Payload:", payload)

        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            timeout=TIMEOUT,
            verify=False
        )

        if response.status_code in [200, 201]:
            print("✅ Maintenance record successfully inserted into MongoDB!")
            return "success"
        else:
            print(f"❌ Endpoint error {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print(f"⚠️ Error while posting Maintenance record: {e}")
        return "failed"
