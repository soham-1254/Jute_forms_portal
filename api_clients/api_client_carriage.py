import requests

# Mock SAP Server Endpoint
MOCK_SERVER_URL = "http://localhost:8080/sap/opu/odata/sap/ZCARRIAGE_API_SRV/FormEntries"

def post_to_sap_carriage(payload: dict):
    """
    Push the Carriage Report form data to the Flask + MongoDB mock server.
    Returns (True, response_json) on success, (False, error_message) on failure.
    """
    try:
        response = requests.post(MOCK_SERVER_URL, json=payload)
        if response.status_code in (200, 201):
            print("✅ Carriage Report data successfully posted to Mock SAP Server.")
            return True, response.json()
        else:
            print(f"⚠️ Server returned {response.status_code}: {response.text}")
            return False, f"Server error {response.status_code}: {response.text}"
    except Exception as e:
        print(f"❌ Error posting to server: {e}")
        return False, str(e)
