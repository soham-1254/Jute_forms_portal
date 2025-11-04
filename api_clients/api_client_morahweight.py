import requests

MOCK_SERVER_URL = "http://localhost:8080/sap/opu/odata/sap/ZMORAHWEIGHT_API_SRV/FormEntries"

def post_to_sap_morahweight(payload: dict):
    """Send Morah Weight data to Mock SAP Flask server."""
    try:
        resp = requests.post(MOCK_SERVER_URL, json=payload)
        if resp.status_code in (200, 201):
            print("✅ Morah Weight record posted successfully.")
            return True, resp.json()
        else:
            print(f"⚠️ Server returned {resp.status_code}: {resp.text}")
            return False, resp.text
    except Exception as e:
        print(f"❌ Error posting to Mock SAP: {e}")
        return False, str(e)
