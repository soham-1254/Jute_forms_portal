import requests
import json
import os

# ==============================
# 🔗 API CONFIGURATION
# ==============================

# Flask + MongoDB mock server endpoint for Roll Stock Availability
SAP_BASE_URL = "http://localhost:8080/sap/opu/odata/sap/ZROLLSTOCKAVAIL_API_SRV/FormEntries"

SAP_USERNAME = os.getenv("SAP_USER", "test_user")
SAP_PASSWORD = os.getenv("SAP_PASS", "test_pass")
SAP_BEARER_TOKEN = os.getenv("SAP_BEARER_TOKEN", None)

TIMEOUT = 15


def post_to_sap_rollstockavail(record):
    """
    Push a Roll Stock Availability record (dict) to Flask + MongoDB mock server.
    Returns:
        "success" if 200/201 response
        "failed" otherwise
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Auth setup
        auth = None
        if SAP_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {SAP_BEARER_TOKEN}"
        else:
            auth = (SAP_USERNAME, SAP_PASSWORD)

        # Convert record to JSON
        payload = json.dumps(record, default=str)

        print("\n--- Posting to Roll Stock Availability endpoint ---")
        print("URL:", SAP_BASE_URL)
        print("Payload:", payload)

        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            auth=auth,
            timeout=TIMEOUT
        )

        # Log every request
        os.makedirs("data", exist_ok=True)
        with open("data/rollstockavail_response_log.txt", "a", encoding="utf-8") as f:
            f.write("\n--- NEW REQUEST ---\n")
            f.write(f"Payload: {json.dumps(record, indent=2)}\n")
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")

        # Check for success
        if response.status_code in [200, 201]:
            print("✅ Record successfully sent to Roll Stock Availability API!")
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
