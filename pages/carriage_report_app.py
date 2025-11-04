import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_carriage import post_to_sap_carriage  # 🔗 Flask + MongoDB Integration

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Carriage Report Entry", layout="centered")
st.title("🚋 Carriage Report Entry Form")

# --- Navigation Buttons ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔙 Back to Dashboard", use_container_width=True):
        st.switch_page("main_app.py")

with col2:
    if st.button("🚪 Logout / Back to Login", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.success("👋 You’ve been logged out successfully.")
        st.switch_page("main_app.py")

# =====================================================
# 1️⃣ BASIC DETAILS
# =====================================================
st.subheader("1️⃣ Basic Information")

today = date.today()
min_date = today - timedelta(days=5)

record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

worker_name = st.text_input("Worker Name", placeholder="Enter worker name")

# =====================================================
# 2️⃣ MACHINE DETAILS
# =====================================================
st.subheader("2️⃣ Machine Details")

machine_type = st.selectbox(
    "Select Machine Type",
    ["1st Drawing", "2nd Drawing", "3rd Drawing"]
)

# ✅ Carriage No. now accepts text with special characters (e.g., 25/02, C/12-A)
carriage_no = st.text_input("Carriage No.", placeholder="e.g., 25/02, C/12-A")

time_slot = st.selectbox(
    "Select Time Slot",
    ["6–11 AM", "11 AM–2 PM", "2–5 PM", "5–10 PM"]
)

reason = st.text_area("Reason / Remarks", placeholder="e.g., Routine check, vibration issue, repair work", height=100)

# =====================================================
# 3️⃣ VALIDATION & SUBMISSION
# =====================================================
if st.button("Submit Carriage Report"):
    # Basic validation
    if not worker_name.strip():
        st.error("⚠️ Worker Name cannot be empty.")
    elif not carriage_no.strip():
        st.error("⚠️ Carriage No. cannot be empty.")
    elif not reason.strip():
        st.error("⚠️ Please enter the reason/remarks.")
    else:
        record = {
            "Date": str(record_date),
            "Worker Name": worker_name.strip(),
            "Machine Type": machine_type,
            "Carriage No.": carriage_no.strip(),
            "Time Slot": time_slot,
            "Reason": reason.strip(),
        }

        df = pd.DataFrame([record])

        # ✅ Save locally as backup
        try:
            existing = pd.read_csv("carriage_report_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("carriage_report_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("carriage_report_records.csv", index=False)

        # ✅ Push to Flask + MongoDB (mock SAP server)
        success, response = post_to_sap_carriage(record)
        if success:
            st.success("✅ Record successfully pushed to MongoDB (Mock SAP Server)!")
        else:
            st.warning(f"⚠️ Saved locally but not synced — {response}")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Drawing Department — Streamlit Digitization Form (Carriage Report)")
