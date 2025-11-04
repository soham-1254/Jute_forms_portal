import requests
import json
import os

# =====================================================
# 🌐 API CONFIGURATION
# =====================================================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZDRAWING_METER_SRV/FormEntries"

def post_to_sap_drawingmeter(record):
    """
    Sends Drawing Meter Book data to Flask mock server.
    Stored in MongoDB collection: Drawing_meter_book
    """
    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = json.dumps(record, default=str)
        response = requests.post(SAP_BASE_URL, headers=headers, data=payload, timeout=10)

        os.makedirs("data_logs", exist_ok=True)
        with open("data_logs/drawing_meter_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- Drawing Meter Record ---\n{payload}\nResponse: {response.status_code}\n")

        if response.status_code in [200, 201]:
            print("✅ Successfully pushed Drawing Meter record to MongoDB.")
            return "success"
        else:
            print(f"❌ Server returned {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print("⚠️ Error posting Drawing Meter data:", e)
        return "failed"
