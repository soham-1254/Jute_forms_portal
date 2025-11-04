import requests

# Mock SAP Server Endpoint (matches mock_server.py)
MOCK_SERVER_URL = "http://localhost:8080/sap/opu/odata/sap/ZFINSQC_API_SRV/FormEntries"

def post_to_sap_finsqc(payload: dict):
    """
    Push Finisher Drawing SQC Report data to Flask + MongoDB mock SAP server.
    """
    try:
        response = requests.post(MOCK_SERVER_URL, json=payload)
        if response.status_code in (200, 201):
            print("✅ Finisher SQC data successfully posted to Mock SAP Server.")
            return True, response.json()
        else:
            print(f"⚠️ Server returned {response.status_code}: {response.text}")
            return False, f"Server error {response.status_code}: {response.text}"
    except Exception as e:
        print(f"❌ Error posting to server: {e}")
        return False, str(e)
