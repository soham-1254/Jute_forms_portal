import requests
import json
import warnings

warnings.filterwarnings("ignore")

# ====================================================
# 🌐 Flask + MongoDB Server URL
# ====================================================
BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZROLLSTOCK_API_SRV/FormEntries"
TIMEOUT = 15

# ====================================================
# 🚀 Function: Post to Roll Stock Carding API
# ====================================================
def post_to_sap_rollstock(record):
    """
    Sends Roll Stock Carding record from Streamlit form
    to Flask + MongoDB mock SAP OData service.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = json.dumps(record, default=str)

        print("\n📤 Sending Roll Stock record to Flask Server...")
        print(f"🔗 Endpoint: {BASE_URL}")
        print("🧾 Payload:", payload)

        response = requests.post(
            BASE_URL,
            headers=headers,
            data=payload,
            timeout=TIMEOUT,
            verify=False
        )

        if response.status_code in [200, 201]:
            print("✅ Roll Stock Carding record successfully inserted into MongoDB!")
            return "success"
        else:
            print(f"❌ Endpoint error {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print("⚠️ Error posting Roll Stock record:", e)
        return "failed"
