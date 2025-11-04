import requests
import json
import os

# =====================================================
# 🌐 API CONFIGURATION
# =====================================================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZBUNDLE_STRENGTH_SRV/FormEntries"

def post_to_sap_bundle_strength(record):
    """
    Sends Raw Jute Bundle Strength Report data to Flask mock server.
    Stores data in MongoDB collection: Raw_jute_bundle_strength
    """
    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = json.dumps(record, default=str)
        response = requests.post(SAP_BASE_URL, headers=headers, data=payload, timeout=10, verify=False)

        os.makedirs("data_logs", exist_ok=True)
        with open("data_logs/bundle_strength_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- Bundle Strength Submission ---\n{payload}\nResponse: {response.status_code}\n")

        if response.status_code in [200, 201]:
            print("✅ Successfully pushed Bundle Strength Report to MongoDB.")
            return "success"
        else:
            print(f"❌ Server returned {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print("⚠️ Error posting Bundle Strength data:", e)
        return "failed"
