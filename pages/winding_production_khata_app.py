import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_winding import post_to_sap_winding  # Flask + MongoDB integration

# =====================================================
# 🧷 PAGE CONFIGURATION
# =====================================================
st.set_page_config(page_title="Winding Production Khata", layout="centered")
st.title("🧵 Winding Production Khata Register")

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

shift = st.selectbox("🕒 Select Shift", ["A", "B", "C"])

quality = st.text_input("🎯 Enter Quality", placeholder="e.g., 8½ lbs Hess Warp, 15 lbs Sacking Warp")

# =====================================================
# 🧩 2️⃣ FRAME ENTRY
# =====================================================
frame_no = st.text_input("🧾 Frame Number", placeholder="e.g., F-12, F-3A, etc.")

production = st.number_input("⚙️ Production (in kg)", min_value=0.0, step=0.1)

# =====================================================
# ✅ 3️⃣ SUBMIT SECTION
# =====================================================
if st.button("Submit Winding Production Record", use_container_width=True):
    if not quality.strip():
        st.error("⚠️ Quality cannot be empty.")
    elif not frame_no.strip():
        st.error("⚠️ Frame number cannot be empty.")
    elif production <= 0:
        st.error("⚠️ Production must be greater than 0.")
    else:
        record = {
            "Date": str(record_date),
            "Shift": shift,
            "Quality": quality.strip(),
            "Frame Number": frame_no.strip(),
            "Production (kg)": production,
        }

        csv_name = "winding_production_khata_records.csv"

        # --- Save locally ---
        try:
            existing = pd.read_csv(csv_name)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])
        updated.to_csv(csv_name, index=False)

        # --- Push to mock SAP server ---
        ok, resp = post_to_sap_winding(record)
        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            st.warning(f"⚠️ Saved locally. Could not sync: {resp}")

        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 📊 4️⃣ DAILY SUMMARY (OPTIONAL)
# =====================================================
st.markdown("---")
st.subheader("📊 Daily Summary")

try:
    df_all = pd.read_csv("winding_production_khata_records.csv")
    df_today = df_all[df_all["Date"] == str(record_date)]

    if not df_today.empty:
        summary = (
            df_today.groupby("Shift")[["Production (kg)"]]
            .sum()
            .reset_index()
            .sort_values("Shift")
        )
        st.dataframe(summary, use_container_width=True)

        total_prod = summary["Production (kg)"].sum()
        st.write(f"**Total Production (All Shifts):** {total_prod} kg")
    else:
        st.info("No data for the selected date yet.")
except FileNotFoundError:
    st.info("No records found yet. Submit your first record to see the summary.")

st.markdown("---")
st.caption("Developed for Winding Department — Frame-wise Shift Production Entry.")
