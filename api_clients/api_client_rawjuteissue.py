import requests
import json
import os

# =====================================================
# API CONFIGURATION (Flask + MongoDB)
# =====================================================
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZRAWJUTE_ISSUE_SRV/FormEntries"

SAP_USERNAME = os.getenv("SAP_USER", "test_user")
SAP_PASSWORD = os.getenv("SAP_PASS", "test_pass")
SAP_BEARER_TOKEN = os.getenv("SAP_BEARER_TOKEN", None)

TIMEOUT = 15


def post_to_sap_rawjuteissue(record):
    """
    Push a single Raw Jute Issue record to the mock SAP/MongoDB server.
    Returns: "success" or "failed"
    """
    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        auth = None

        if SAP_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {SAP_BEARER_TOKEN}"
        else:
            auth = (SAP_USERNAME, SAP_PASSWORD)

        payload = json.dumps(record, default=str)

        print("\n--- Posting Raw Jute Issue Record ---")
        print("URL:", SAP_BASE_URL)
        print("Payload:", payload)

        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            data=payload,
            auth=auth,
            timeout=TIMEOUT,
            verify=False
        )

        # Log every request
        os.makedirs("data", exist_ok=True)
        with open("data/raw_jute_issue_log.txt", "a", encoding="utf-8") as f:
            f.write("\n--- NEW REQUEST ---\n")
            f.write(f"Payload: {json.dumps(record, indent=2)}\n")
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response: {response.text}\n")

        if response.status_code in [200, 201]:
            print("✅ Record successfully sent to Flask + MongoDB!")
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
