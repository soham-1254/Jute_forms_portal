import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_historybook import post_to_sap_historybook   # 🔗 Flask + MongoDB integration

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="History Book Entry", layout="centered")
st.title("📘 History Book — Department-wise Work Log")

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
today = date.today()
min_date = today - timedelta(days=5)

department = st.selectbox(
    "🏭 Select Department",
    ["Batching", "Carding", "Drawing", "Spinning", "Winding"]
)

record_date = st.date_input(
    "📅 Select Date",
    value=today,
    min_value=min_date,
    max_value=today
)

machine_name = st.text_input("⚙️ Machine Name", placeholder="e.g., Finisher Card, 3rd Drawing")
machine_no = st.number_input("🔢 Machine Number", min_value=1, step=1)
work_done = st.text_area("🧰 Work Done / Description", placeholder="e.g., Changed bearings, adjusted roller alignment")

# =====================================================
# 2️⃣ SUBMIT BUTTON
# =====================================================
if st.button("Submit Record", use_container_width=True):
    if not machine_name.strip() or not work_done.strip():
        st.error("⚠️ Machine name and Work done fields cannot be empty.")
    else:
        record = {
            "Date": str(record_date),
            "Department": department,
            "Machine Name": machine_name.strip(),
            "Machine Number": machine_no,
            "Work Done": work_done.strip()
        }

        # Save to CSV
        csv_name = "history_book_records.csv"
        try:
            existing = pd.read_csv(csv_name)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])
        updated.to_csv(csv_name, index=False)

        # Sync with Mock SAP Server
        ok, resp = post_to_sap_historybook(record)
        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            st.warning(f"⚠️ Saved locally — could not sync: {resp}")

        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 3️⃣ VIEW RECORDS
# =====================================================
st.markdown("---")
st.subheader("📋 Recent Entries")

try:
    df = pd.read_csv("history_book_records.csv")
    st.dataframe(df.tail(10), use_container_width=True)
except FileNotFoundError:
    st.info("No records yet. Submit your first entry above!")

st.markdown("---")
st.caption("Developed for Mill Maintenance — Department-wise History Book Register")
