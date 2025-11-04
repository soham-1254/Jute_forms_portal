import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_finisherrollfeed import post_to_sap_finisherrollfeed  # 🔗 Flask + MongoDB integration

# ==============================
# 🧾 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="Finisher Card Rollfeed Entry", layout="centered")
st.title("📒 Finisher Card Rollfeed Record")

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

# ==============================
# 1️⃣ BASIC DETAILS
# ==============================
st.subheader("1️⃣ Basic Information")
today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

quality_options = ["XX", "Special", "Rollfeed", "Others"]
quality = st.selectbox("Select Quality", quality_options)

# ==============================
# 2️⃣ MACHINE DETAILS
# ==============================
st.subheader("2️⃣ Machine & Measurement Entry")
machine_no = st.text_input("Enter Machine Number")

# ==============================
# 3️⃣ MEASUREMENTS ENTRY
# ==============================
st.markdown("#### 🔹 Enter Measurements for Two Readings")

col1, col2 = st.columns(2)
with col1:
    weight_1 = st.number_input("Weight 1 (gm)", min_value=0.0, step=0.1, key="w1")
    mr_1 = st.number_input("MR% 1", min_value=0.0, max_value=50.0, step=0.1, key="mr1")

with col2:
    weight_2 = st.number_input("Weight 2 (gm)", min_value=0.0, step=0.1, key="w2")
    mr_2 = st.number_input("MR% 2", min_value=0.0, max_value=50.0, step=0.1, key="mr2")

# --- Calculations ---
actual_1 = weight_1 * 0.0440917 if weight_1 > 0 else 0
converted_1 = (actual_1 * 120) / (mr_1 + 100) if (mr_1 >= 0 and mr_1 < 50) else 0
actual_2 = weight_2 * 0.0440917 if weight_2 > 0 else 0
converted_2 = (actual_2 * 120) / (mr_2 + 100) if (mr_2 >= 0 and mr_2 < 50) else 0

avg_converted = 0.0
if converted_1 > 0 or converted_2 > 0:
    avg_converted = (converted_1 + converted_2) / 2

st.success(f"📊 Average of Converted Weights: {avg_converted:.4f} kg")

# ==============================
# 4️⃣ SUBMIT BUTTON
# ==============================
if st.button("📤 Submit Record"):
    if (weight_1 <= 0 or weight_2 <= 0 or 
        mr_1 <= 0 or mr_1 > 50 or mr_2 <= 0 or mr_2 > 50):
        st.error("🚫 Invalid input — Ensure all weights >0 and MR% between 0–50.")
    else:
        record = {
            "Date": str(record_date),
            "Quality": quality,
            "Machine No": machine_no,
            "Weight 1 (gm)": weight_1,
            "MR% 1": mr_1,
            "Actual Weight 1 (kg)": round(actual_1, 4),
            "Converted Weight 1 (kg)": round(converted_1, 4),
            "Weight 2 (gm)": weight_2,
            "MR% 2": mr_2,
            "Actual Weight 2 (kg)": round(actual_2, 4),
            "Converted Weight 2 (kg)": round(converted_2, 4),
            "Average Converted Weight (kg)": round(avg_converted, 4)
        }

        # --- Save locally ---
        df = pd.DataFrame([record])
        try:
            existing = pd.read_csv("finisher_card_rollfeed_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("finisher_card_rollfeed_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("finisher_card_rollfeed_records.csv", index=False)

        # --- Push to Flask + MongoDB ---
        status = post_to_sap_finisherrollfeed(record)
        if status == "success":
            st.success("✅ Record submitted and stored in MongoDB successfully!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check server log.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Finisher Card Section — Streamlit + Flask + MongoDB Integration")
