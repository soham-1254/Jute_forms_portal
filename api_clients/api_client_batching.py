import requests
import json
import os

# =====================================================
# 🔗 API CONFIGURATION
# =====================================================
SAP_BASE_URL = "http://localhost:8080/sap/opu/odata/sap/ZBATCHING_API_SRV/FormEntries"

# Optional: credentials (not needed for local)
SAP_USERNAME = os.getenv("SAP_USER", "test_user")
SAP_PASSWORD = os.getenv("SAP_PASS", "test_pass")

TIMEOUT = 15


# =====================================================
# 🚀 FUNCTION TO POST RECORD TO MOCK SERVER
# =====================================================
def post_to_sap_batching(record):
    """
    Send a record from the Streamlit Batching Entry Form to the Flask + MongoDB mock server.

    Parameters:
        record (dict): A single entry from the batching form.
    Returns:
        "success" → if record is successfully inserted (HTTP 200/201)
        "failed"  → otherwise
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Convert Python dict → JSON
        payload = json.dumps(record, default=str)

        print("\n🔹 Sending data to Batching API Endpoint")
        print("POST →", SAP_BASE_URL)
        print("Payload:", payload)

        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            timeout=TIMEOUT
        )

        # Save logs locally
        os.makedirs("data", exist_ok=True)
        with open("data/batching_api_log.txt", "a", encoding="utf-8") as f:
            f.write("\n--- NEW REQUEST ---\n")
            f.write(f"URL: {SAP_BASE_URL}\n")
            f.write(f"Payload: {json.dumps(record, indent=2)}\n")
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")

        if response.status_code in [200, 201]:
            print("✅ Successfully pushed record to mock server!")
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
