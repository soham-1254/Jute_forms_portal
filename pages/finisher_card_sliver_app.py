import streamlit as st
import pandas as pd
from datetime import date, timedelta
import requests
from api_clients.api_client_finishercard import post_to_sap_finishercard  # your existing client

# =====================================================
# CONFIG
# =====================================================
CSV_NAME = "finisher_card_records.csv"
API_URL = "http://localhost:8080/sap/opu/odata/sap/ZFINISHERCARD_API_SRV/FormEntries"

# =====================================================
# PAGE
# =====================================================
st.set_page_config(page_title="Finisher Card Sliver Weight Entry", layout="centered")
st.title("📒 Finisher Card Sliver Weight Entry")

st.markdown("---")

# (optional) navigation like your spool page
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

st.markdown("---")

# =====================================================
# 1️⃣ BASIC INFO
# =====================================================
today = date.today()
min_date = today - timedelta(days=5)

record_date = st.date_input("📅 Select Date", value=today, min_value=min_date, max_value=today)
quality = st.selectbox(
    "🎯 Select Quality",
    ["Hessian", "Sacking Warp", "Special Sacking Warp S4", "S4 Weft"]
)
machine_no = st.number_input("🛠️ Machine Number", min_value=1, step=1)

# =====================================================
# 2️⃣ MEASUREMENTS
# =====================================================
st.subheader("📏 Sliver Weight Measurements")

col1, col2 = st.columns(2)
with col1:
    weight_1 = st.number_input("Weight 1 (gm)", min_value=0.0, step=0.1)
    mr_1 = st.number_input("MR% 1", min_value=0.0, step=0.1, help="Allowed: 0–50")
with col2:
    weight_2 = st.number_input("Weight 2 (gm)", min_value=0.0, step=0.1)
    mr_2 = st.number_input("MR% 2", min_value=0.0, step=0.1, help="Allowed: 0–50")

# =====================================================
# 3️⃣ CALCULATION LOGIC
# =====================================================
def calculate_actual_converted(weight, mr, quality):
    constant = 1.0582
    if quality in ["Sacking Warp", "Sacking Weft", "Special Sacking Warp S4"]:
        converted = (constant * weight) * (120 / (mr + 100))
    else:  # Hessian, S4 Weft
        converted = (constant * weight) * (116 / (mr + 100))
    actual = constant * weight
    return round(actual, 2), round(converted, 2)

actual_1, converted_1 = calculate_actual_converted(weight_1, mr_1, quality)
actual_2, converted_2 = calculate_actual_converted(weight_2, mr_2, quality)

if (weight_1 > 0 and weight_2 > 0):
    avg_converted = round((converted_1 + converted_2) / 2, 2)
else:
    avg_converted = 0.0

st.markdown("---")
st.write(f"📊 **Average Converted Weight:** `{avg_converted} gm`")

# =====================================================
# 4️⃣ SUBMIT
# =====================================================
if st.button("💾 Submit Finisher Card Record", use_container_width=True):

    # ✅ 1. basic validation
    if machine_no <= 0:
        st.error("⚠️ Machine number must be greater than 0.")
    elif weight_1 <= 0 or weight_2 <= 0:
        st.error("⚠️ Both weights must be greater than 0.")
    # ✅ 2. MR% validation (your missing rule)
    elif not (0 <= mr_1 <= 50) or not (0 <= mr_2 <= 50):
        st.error("⚠️ MR% must be between 0 and 50 for both entries.")
    else:
        # ✅ if all good, build record
        record = {
            "Date": str(record_date),
            "Quality": quality,
            "Machine No.": machine_no,
            "Weight 1 (gm)": weight_1,
            "MR% 1": mr_1,
            "Actual 1": actual_1,
            "Converted 1": converted_1,
            "Weight 2 (gm)": weight_2,
            "MR% 2": mr_2,
            "Actual 2": actual_2,
            "Converted 2": converted_2,
            "Average Converted": avg_converted,
        }

        # 🔽 1. save to local CSV (like your spool code)
        try:
            existing = pd.read_csv(CSV_NAME)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])

        updated.to_csv(CSV_NAME, index=False)

        # 🔽 2. try to send to mock SAP / Flask
        ok = False
        resp = None
        try:
            ok, resp = post_to_sap_finishercard(record)
        except Exception as e:
            resp = str(e)

        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            # fallback: raw HTTP
            try:
                r = requests.post(API_URL, json=record, timeout=10)
                if r.status_code in [200, 201]:
                    st.success("✅ Record saved and uploaded to SAP OData endpoint.")
                else:
                    st.warning(f"⚠️ Saved locally but upload failed (status {r.status_code}).")
            except Exception as e:
                st.warning(f"⚠️ Saved locally — server not reachable: {e}")

        # show what we saved
        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 5️⃣ DAILY SUMMARY
# =====================================================
st.markdown("---")
st.subheader("📅 Daily Finisher Card Summary")

try:
    df_all = pd.read_csv(CSV_NAME)
    df_today = df_all[df_all["Date"] == str(record_date)]

    if not df_today.empty:
        avg_today = df_today["Average Converted"].mean()
        total_machines = df_today["Machine No."].nunique()

        st.write(f"**🧮 Average Converted (today):** {avg_today:.2f} gm")
        st.write(f"**🛠️ Machines reported today:** {total_machines}")

        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No records found for the selected date yet.")
except FileNotFoundError:
    st.info("No records yet. Submit the first entry to start tracking.")

st.markdown("---")
st.caption("Developed for Finisher Card Department — Streamlit Digitization Form.")
