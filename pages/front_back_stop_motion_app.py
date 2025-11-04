import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_stopmotion import post_to_sap_stopmotion  # 🔗 Flask + MongoDB integration

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="Front & Back Stop Motion Report", layout="centered")
st.title("🛠️ Front & Back Stop Motion Report")

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

# ----------------------------------
# 1️⃣ BASIC INFORMATION
# ----------------------------------
st.subheader("1️⃣ Basic Information")

today = date.today()
min_date = today - timedelta(days=5)

record_date = st.date_input(
    "Select Date",
    value=today,
    min_value=min_date,
    max_value=today
)

# ----------------------------------
# 2️⃣ MACHINE DETAILS
# ----------------------------------
st.subheader("2️⃣ Machine Details")

machine_name = st.selectbox(
    "Select Machine Name",
    ["1st Drawing", "2nd Drawing", "3rd Drawing"]
)

machine_number = st.number_input("Enter Machine Number", min_value=1, step=1)

parts_repaired = st.text_input(
    "Parts Repaired / Description",
    placeholder="e.g., Front Stop Motion repaired, Back Stop Motion adjusted"
)

# ----------------------------------
# 3️⃣ SUBMIT DATA
# ----------------------------------
if st.button("Submit Stop Motion Record"):
    if not parts_repaired.strip():
        st.error("⚠️ Please enter 'Parts Repaired' before submitting.")
    else:
        record = {
            "Date": str(record_date),
            "Machine Name": machine_name,
            "Machine Number": machine_number,
            "Parts Repaired": parts_repaired.strip(),
        }

        # Save locally
        df = pd.DataFrame([record])
        try:
            existing = pd.read_csv("front_back_stop_motion_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("front_back_stop_motion_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("front_back_stop_motion_records.csv", index=False)

        # Send to mock SAP server (MongoDB)
        success, response = post_to_sap_stopmotion(record)
        if success:
            st.success("✅ Record successfully pushed to MongoDB (Mock SAP Server)!")
        else:
            st.warning(f"⚠️ Saved locally but not synced — {response}")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Drawing Department — Streamlit Digitization Form (Front & Back Stop Motion)")
