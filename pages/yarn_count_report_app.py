import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_yarncount import post_to_sap_yarncount  # Flask + MongoDB integration

# =====================================================
# 🧷 PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Yarn Count Report", layout="centered")
st.title("🧶 Yarn Count Report Entry")

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
quality = st.text_input("🎯 Quality", placeholder="e.g., Hess Warp 8.10(G), Sacking Warp 9.50(R)")
frame_no = st.text_input("🧾 Frame Number", placeholder="e.g., A45, B39, etc.")

# =====================================================
# 📊 2️⃣ MEASUREMENT INPUTS
# =====================================================
st.subheader("Measurement Details")

col1, col2, col3 = st.columns(3)
with col1:
    dp = st.number_input("DP (Draft)", min_value=0.0, step=0.1)
with col2:
    tp = st.number_input("TP (Twist)", min_value=0.0, step=0.1)
with col3:
    wt = st.number_input("Weight (g)", min_value=0.0, step=0.1)

mr_percent = st.number_input("MR%", min_value=0.0, step=0.1)

# =====================================================
# 🧮 3️⃣ CALCULATION SECTION
# =====================================================
st.subheader("Calculated Fields")

CONSTANT = 0.069
actual_wt = round(CONSTANT * wt, 2)

# Determine formula type based on Quality
if any(keyword.lower() in quality.lower() for keyword in ["sacking", "skg", "special sacking"]):
    conv_const = 120
else:
    conv_const = 116

# Apply conversion formula only if MR% > 0
if mr_percent > 0:
    converted_wt = round(actual_wt * (conv_const / (mr_percent + 100)), 2)
else:
    converted_wt = 0.0

col1, col2 = st.columns(2)
col1.metric(label="Actual Weight (g)", value=actual_wt)
col2.metric(label="Converted Weight (g)", value=converted_wt)

# =====================================================
# ✅ 4️⃣ SUBMIT DATA
# =====================================================
if st.button("Submit Yarn Count Record", use_container_width=True):
    if not quality.strip():
        st.error("⚠️ Quality cannot be empty.")
    elif not frame_no.strip():
        st.error("⚠️ Frame number cannot be empty.")
    elif wt <= 0 or mr_percent <= 0:
        st.error("⚠️ Weight and MR% must be greater than 0.")
    else:
        record = {
            "Date": str(record_date),
            "Quality": quality.strip(),
            "Frame Number": frame_no.strip(),
            "DP": dp,
            "TP": tp,
            "Weight (g)": wt,
            "MR%": mr_percent,
            "Actual Weight (g)": actual_wt,
            "Converted Weight (g)": converted_wt,
        }

        csv_name = "yarn_count_records.csv"
        try:
            existing = pd.read_csv(csv_name)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])
        updated.to_csv(csv_name, index=False)

        ok, resp = post_to_sap_yarncount(record)
        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            st.warning(f"⚠️ Saved locally — could not sync: {resp}")

        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 📈 5️⃣ DAILY SUMMARY
# =====================================================
st.markdown("---")
st.subheader("📊 Daily Summary")

try:
    df_all = pd.read_csv("yarn_count_records.csv")
    df_today = df_all[df_all["Date"] == str(record_date)]

    if not df_today.empty:
        avg_actual = df_today["Actual Weight (g)"].mean()
        avg_conv = df_today["Converted Weight (g)"].mean()
        st.write(f"**Average Actual Weight (g):** {avg_actual:.2f}")
        st.write(f"**Average Converted Weight (g):** {avg_conv:.2f}")
        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No records found for the selected date yet.")
except FileNotFoundError:
    st.info("No records found yet. Submit the first entry to see the summary.")

st.markdown("---")
st.caption("Developed for Yarn Department — Frame-wise Yarn Count Tracking.")
