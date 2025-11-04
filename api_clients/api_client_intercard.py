import requests
import json
import os

# ==============================
# 🌐 INTER CARD API CONFIGURATION
# ==============================
# Point to your Flask mock server endpoint or MongoDB-enabled API
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZINTERCARD_API_SRV/FormEntries"

# Optional credentials (for real SAP OData if used later)
SAP_USERNAME = os.getenv("SAP_USER", "test_user")
SAP_PASSWORD = os.getenv("SAP_PASS", "test_pass")

# Optional Bearer Token (for future SAP secure access)
SAP_BEARER_TOKEN = os.getenv("SAP_BEARER_TOKEN", None)

TIMEOUT = 15


# ==============================
# 🚀 FUNCTION: POST TO SAP / MOCK SERVER
# ==============================
def post_to_sap_intercard(record):
    """
    Push a single record (dict) to Flask mock server / SAP OData endpoint.
    Returns:
        "success"  -> if data stored successfully
        "failed"   -> if request failed
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Auth (for SAP if needed)
        auth = None
        if SAP_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {SAP_BEARER_TOKEN}"
        else:
            auth = (SAP_USERNAME, SAP_PASSWORD)

        # Construct payload
        record_with_id = record.copy()
        record_with_id["FormId"] = f"INTER-{record.get('Date', 'NA')}-{record.get('Machine No', 'NA')}"
        payload = json.dumps(record_with_id, default=str)

        print("\n--- Posting to INTER CARD endpoint ---")
        print("URL:", SAP_BASE_URL)
        print("Payload:", payload)

        # POST to mock SAP / MongoDB server
        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            auth=auth,
            timeout=TIMEOUT,
            verify=False  # For local HTTP mock servers
        )

        # Log all responses for debugging
        os.makedirs("data", exist_ok=True)
        with open("data/intercard_response_log.txt", "a", encoding="utf-8") as f:
            f.write("\n--- NEW REQUEST ---\n")
            f.write(f"Payload: {json.dumps(record_with_id, indent=2)}\n")
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")

        # Success check
        if response.status_code in [200, 201]:
            print("✅ Record successfully sent to Inter Card mock server!")
            print("Response:", response.text)
            return "success"
        else:
            print(f"❌ Endpoint error {response.status_code}: {response.text}")
            return "failed"

    except requests.exceptions.RequestException as e:
        print("⚠️ Connection Error:", e)
        return "failed"

    except Exception as e:
        print("⚠️ General Error:", e)
        return "failed"
