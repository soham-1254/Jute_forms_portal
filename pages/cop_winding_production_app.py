import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_copwinding import post_to_sap_copwinding  # Flask + MongoDB integration

# =====================================================
# 🧷 PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Cop Winding Production", layout="centered")
st.title("🧵 Cop Winding Production Entry")

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
# 📅 1️⃣ BASIC DETAILS
# =====================================================
today = date.today()
min_date = today - timedelta(days=5)

record_date = st.date_input("📅 Select Date", value=today, min_value=min_date, max_value=today)
shift = st.selectbox("🕒 Shift", ["A", "B", "C"])
frame_no = st.text_input("🔢 Frame Number", placeholder="e.g., B01, A02, etc.")
quality = st.text_input("🎯 Quality", placeholder="e.g., 21lbs Hess Warp, 8.5lbs Sacking Weft")
worker_name = st.text_input("👷 Worker Name", placeholder="e.g., Ranjit, Ashok, Bijoy, etc.")
production = st.number_input("📦 Production (kg)", min_value=0.0, step=0.1)

# =====================================================
# ✅ 2️⃣ VALIDATION & SUBMISSION
# =====================================================
if st.button("Submit Cop Winding Record", use_container_width=True):
    if not frame_no.strip():
        st.error("⚠️ Frame number cannot be empty.")
    elif not quality.strip():
        st.error("⚠️ Quality cannot be empty.")
    elif not worker_name.strip():
        st.error("⚠️ Worker name cannot be empty.")
    elif production <= 0:
        st.error("⚠️ Production value must be greater than 0.")
    else:
        record = {
            "Date": str(record_date),
            "Shift": shift,
            "Frame Number": frame_no.strip(),
            "Quality": quality.strip(),
            "Worker Name": worker_name.strip(),
            "Production (kg)": production,
        }

        csv_name = "cop_winding_records.csv"
        try:
            existing = pd.read_csv(csv_name)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])
        updated.to_csv(csv_name, index=False)

        ok, resp = post_to_sap_copwinding(record)
        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            st.warning(f"⚠️ Saved locally — could not sync: {resp}")

        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 📊 3️⃣ DAILY SUMMARY (SHIFT-WISE)
# =====================================================
st.markdown("---")
st.subheader("📊 Shift-wise Production Summary")

try:
    df_all = pd.read_csv("cop_winding_records.csv")
    df_today = df_all[df_all["Date"] == str(record_date)]

    if not df_today.empty:
        total_prod = df_today["Production (kg)"].sum()
        st.write(f"### 📅 Total Production on {record_date}: **{total_prod:.2f} kg**")

        shift_summary = (
            df_today.groupby("Shift")[["Production (kg)"]]
            .sum()
            .reset_index()
            .rename(columns={"Production (kg)": "Total Production (kg)"})
        )
        st.dataframe(shift_summary, use_container_width=True)

        st.markdown("### 📋 Full Records for the Day")
        st.dataframe(df_today, use_container_width=True)

    else:
        st.info("No records found for the selected date yet.")

except FileNotFoundError:
    st.info("No records found yet. Submit the first entry to see the summary.")

st.markdown("---")
st.caption("Developed for Winding Department — Shift-wise Cop Winding Production Register.")

