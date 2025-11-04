import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Flask + MongoDB mock SAP endpoint
SAP_BASE_URL = "http://127.0.0.1:8080/sap/opu/odata/sap/ZSPREADER_API_SRV/FormEntries"
TIMEOUT = 15

def post_to_sap_spreader(record):
    """
    Push Spreader Roll Sliver Khata data to Flask + MongoDB mock SAP endpoint.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        clean_record = {
            "FormId": f"SPR-{record.get('Date', 'NA')}-{record.get('Machine No', 'NA')}",
            "Date": record.get("Date", ""),
            "MachineNo": record.get("Machine No", ""),
            "Day": record.get("Day", ""),
            "Shift": record.get("Shift", ""),
            "QualityType": record.get("Quality Type", ""),
            "Weight1": float(record.get("Weight 1 (gm)", 0)),
            "MR1": float(record.get("MR% 1", 0)),
            "ActualWeight1": float(record.get("Actual Weight 1 (kg)", 0)),
            "ConvertedWeight1": float(record.get("Converted Weight 1 (kg)", 0)),
            "Weight2": float(record.get("Weight 2 (gm)", 0)),
            "MR2": float(record.get("MR% 2", 0)),
            "ActualWeight2": float(record.get("Actual Weight 2 (kg)", 0)),
            "ConvertedWeight2": float(record.get("Converted Weight 2 (kg)", 0)),
            "AverageConverted": float(record.get("Average Converted Weight (kg)", 0)),
            "Remarks": record.get("Remarks", ""),
            "FlagStatus": record.get("Flag Status", "")
        }

        print("\n--- Posting Spreader Record to Flask + MongoDB ---")
        print("Payload:", json.dumps(clean_record, indent=2))

        response = requests.post(
            SAP_BASE_URL,
            headers=headers,
            json=clean_record,
            timeout=TIMEOUT,
            verify=False
        )

        if response.status_code in [200, 201]:
            print("✅ Spreader record successfully inserted into MongoDB.")
            print("Response:", response.text)
            return "success"
        else:
            print(f"❌ Endpoint error {response.status_code}: {response.text}")
            return "failed"

    except Exception as e:
        print("⚠️ General Error:", e)
        return "failed"
