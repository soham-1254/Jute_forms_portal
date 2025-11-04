import requests
import json
import os

# =====================================================
# 🌐 API CONFIGURATION
# =====================================================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZCARDING_REPINNING_SRV/FormEntries"

def post_to_sap_cardingrepinning(record):
    """
    Sends Carding Repinning form data to Flask mock server.
    Stores data in MongoDB collection: Carding_repinnning
    """
    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = json.dumps(record, default=str)

        response = requests.post(SAP_BASE_URL, headers=headers, data=payload, timeout=10, verify=False)

        os.makedirs("data_logs", exist_ok=True)
        with open("data_logs/carding_repinnning_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- Carding Repinning Record ---\n{payload}\nResponse: {response.status_code}\n")

        if response.status_code in [200, 201]:
            print("✅ Successfully pushed Carding Repinning record to MongoDB.")
            return "success"
        else:
            print(f"❌ Server returned {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print("⚠️ Error posting Carding Repinning data:", e)
        return "failed"
