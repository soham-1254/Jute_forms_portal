import requests

# Mock SAP Server URL — must match the route in your mock_server.py
MOCK_SERVER_URL = "http://localhost:8080/sap/opu/odata/sap/ZSTOPMOTION_API_SRV/FormEntries"

def post_to_sap_stopmotion(payload: dict):
    """
    Push the Front & Back Stop Motion data to the Flask + MongoDB mock server.
    Returns (True, response_json) on success, (False, error_message) on failure.
    """
    try:
        response = requests.post(MOCK_SERVER_URL, json=payload)
        if response.status_code in (200, 201):
            print(f"✅ Successfully posted Stop Motion data to server.")
            return True, response.json()
        else:
            print(f"⚠️ Server returned {response.status_code}: {response.text}")
            return False, f"Server error {response.status_code}: {response.text}"
    except Exception as e:
        print(f"❌ Error posting to mock server: {e}")
        return False, str(e)
