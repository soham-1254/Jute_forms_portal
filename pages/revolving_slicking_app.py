import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_revolving import post_to_sap_revolving  # 🔗 Flask + MongoDB Integration

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(page_title="Revolving / Slicking / Mangle Wheel / Idle Record", layout="centered")
st.title("⚙️ Revolving / Slicking / Mangle Wheel / Idle Record")

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

# =====================================================
# 2️⃣ MACHINE DETAILS
# =====================================================
st.subheader("2️⃣ Machine Details")

machine_type = st.selectbox(
    "Select Machine Type",
    ["1st Drawing", "2nd Drawing", "3rd Drawing"]
)

machine_no = st.number_input("Machine Number", min_value=1, step=1)

time_entry = st.text_input("Time (e.g., 5 PM, 6 AM, 10:30 AM)", placeholder="Enter time manually")

remarks = st.text_area("Remarks / Observation", placeholder="e.g., roller jammed, mangle alignment done", height=100)

# =====================================================
# 3️⃣ VALIDATION & SUBMISSION
# =====================================================
if st.button("Submit Record"):
    if not time_entry.strip():
        st.error("⚠️ Please enter the time before submitting.")
    elif not remarks.strip():
        st.error("⚠️ Remarks cannot be empty.")
    else:
        record = {
            "Date": str(record_date),
            "Machine Type": machine_type,
            "Machine No.": machine_no,
            "Time": time_entry.strip(),
            "Remarks": remarks.strip()
        }

        df = pd.DataFrame([record])

        # ✅ Save locally as backup
        try:
            existing = pd.read_csv("revolving_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("revolving_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("revolving_records.csv", index=False)

        # ✅ Push to Flask + MongoDB (mock SAP server)
        success, response = post_to_sap_revolving(record)
        if success:
            st.success("✅ Record successfully pushed to MongoDB (Mock SAP Server)!")
        else:
            st.warning(f"⚠️ Saved locally but not synced — {response}")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Drawing Department — Streamlit Digitization Form (Revolving / Slicking / Mangle Wheel / Idle Record)")
