import requests
import json

SAP_URL = "http://localhost:8080/sap/opu/odata/sap/ZRAWJUTE_API_SRV/FormEntries"

def post_to_sap_rawjute(record):
    try:
        headers = {"Content-Type": "application/json"}
        payload = json.dumps(record, default=str)
        response = requests.post(SAP_URL, data=payload, headers=headers, timeout=15)

        if response.status_code in [200, 201]:
            print("✅ Data successfully inserted into Mock SAP Server.")
            return "success"
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return "failed"
    except Exception as e:
        print("⚠️ Error connecting to API:", e)
        return "failed"
