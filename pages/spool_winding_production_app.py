import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_spoolwinding import post_to_sap_spoolwinding   # 🔗 Flask + MongoDB link

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Spool Winding Production", layout="centered")
st.title("🧵 Spool Winding Production Entry Form")

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

record_date = st.date_input("📅 Select Date", value=today, min_value=min_date, max_value=today)
frame_no = st.number_input("🧾 Frame Number", min_value=1, step=1)
quality = st.text_input("🎯 Quality", placeholder="e.g., 21lbs Hess Warp, 15lbs Sacking Weft")
production = st.number_input("📦 Production (kg)", min_value=0.0, step=0.1)
no_of_fera = st.number_input("🔁 Number of Fera", min_value=0, step=1)
net_weight = st.number_input("⚖️ Net Weight (kg)", min_value=0.0, step=0.1)

# =====================================================
# 2️⃣ VALIDATION & SUBMIT
# =====================================================
if st.button("Submit Spool Winding Record", use_container_width=True):
    if not quality.strip():
        st.error("⚠️ Quality cannot be empty.")
    elif production <= 0 or no_of_fera <= 0 or net_weight <= 0:
        st.error("⚠️ Numeric values must be greater than 0.")
    else:
        record = {
            "Date": str(record_date),
            "Frame Number": frame_no,
            "Quality": quality.strip(),
            "Production (kg)": production,
            "Number of Fera": no_of_fera,
            "Net Weight (kg)": net_weight,
        }

        csv_name = "spool_winding_records.csv"
        try:
            existing = pd.read_csv(csv_name)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])
        updated.to_csv(csv_name, index=False)

        ok, resp = post_to_sap_spoolwinding(record)
        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            st.warning(f"⚠️ Saved locally — could not sync: {resp}")

        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 3️⃣ DAILY SUMMARY
# =====================================================
st.markdown("---")
st.subheader("📊 Daily Production Summary")

try:
    df_all = pd.read_csv("spool_winding_records.csv")
    df_today = df_all[df_all["Date"] == str(record_date)]

    if not df_today.empty:
        total_prod = df_today["Production (kg)"].sum()
        total_fera = df_today["Number of Fera"].sum()
        total_net = df_today["Net Weight (kg)"].sum()

        st.write(f"### 📦 Total Production: **{total_prod:.2f} kg**")
        st.write(f"### 🔁 Total Fera: **{total_fera}**")
        st.write(f"### ⚖️ Total Net Weight: **{total_net:.2f} kg**")

        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No records found for the selected date yet.")
except FileNotFoundError:
    st.info("No records yet. Submit the first entry to start tracking.")

st.markdown("---")
st.caption("Developed for Winding Department — Spool Winding Production Register.")
