import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_intercard import post_to_sap_intercard  # 🔗 Integration with Flask + MongoDB

# ==============================
# 🧾 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="Inter Card Rollfeed Entry", layout="centered")
st.title("📘 Inter Card Rollfeed Entry Form")

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
st.subheader("1️⃣ Basic Details")
today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

machine_no = st.text_input("Enter Machine Number")

shift = st.selectbox("Select Shift", ["A", "B", "C"])
day_options = [
    "1", "2", "3", "4", "5", "6", "7",
    "1-Saturday", "2-Sunday", "3-Monday", "4-Tuesday",
    "5-Wednesday", "6-Thursday", "7-Friday"
]
selected_day = st.selectbox("Select Day", day_options)

# ==============================
# 2️⃣ QUALITY SELECTION
# ==============================
st.subheader("2️⃣ Quality Selection")
quality_options = ["XX", "Special", "Real Feed", "Other"]
quality = st.selectbox("Select Quality", quality_options)

# ==============================
# 3️⃣ WEIGHT & MR% ENTRY
# ==============================
st.subheader("3️⃣ Weight and MR% Entry")
flagged_error = False

# --- Entry 1 ---
st.markdown("#### 🔹 Entry 1")
col1, col2 = st.columns(2)
with col1:
    weight1 = st.number_input("Weight 1 (gm)", step=0.01, key="w1")
with col2:
    mr1 = st.number_input("MR% 1", step=0.01, key="mr1")

# Validation
if weight1 < 0:
    st.error("⚠️ Weight 1 cannot be negative.")
    flagged_error = True
if mr1 < 0 or mr1 >= 50:
    st.error("⚠️ MR% 1 must be between 0 and 50.")
    flagged_error = True

actual_weight1 = weight1 * 0.0440917 if weight1 >= 0 else 0
converted_weight1 = (actual_weight1 * 120) / (mr1 + 100) if (0 <= mr1 < 50) else 0

st.metric("Actual Weight 1 (kg)", f"{actual_weight1:.4f}")
st.metric("Converted Weight 1 (kg)", f"{converted_weight1:.4f}")

# --- Entry 2 ---
st.markdown("#### 🔹 Entry 2")
col3, col4 = st.columns(2)
with col3:
    weight2 = st.number_input("Weight 2 (gm)", step=0.01, key="w2")
with col4:
    mr2 = st.number_input("MR% 2", step=0.01, key="mr2")

if weight2 < 0:
    st.error("⚠️ Weight 2 cannot be negative.")
    flagged_error = True
if mr2 < 0 or mr2 >= 50:
    st.error("⚠️ MR% 2 must be between 0 and 50.")
    flagged_error = True

actual_weight2 = weight2 * 0.0440917 if weight2 >= 0 else 0
converted_weight2 = (actual_weight2 * 120) / (mr2 + 100) if (0 <= mr2 < 50) else 0

st.metric("Actual Weight 2 (kg)", f"{actual_weight2:.4f}")
st.metric("Converted Weight 2 (kg)", f"{converted_weight2:.4f}")

# ==============================
# 4️⃣ AVERAGE SECTION
# ==============================
st.subheader("4️⃣ Average Converted Weight")
avg_converted = 0.0
if converted_weight1 > 0 or converted_weight2 > 0:
    avg_converted = (converted_weight1 + converted_weight2) / 2
st.success(f"✅ Average Converted Weight: {avg_converted:.4f} kg")

remarks = st.text_input("Remarks (optional)")

# ==============================
# 5️⃣ SUBMIT & SAVE
# ==============================
if st.button("📤 Submit Record"):
    if flagged_error:
        st.error("🚩 Submission blocked due to invalid entries. Please correct highlighted fields.")
    else:
        record = {
            "Date": str(record_date),
            "Machine No": machine_no,
            "Day": selected_day,
            "Shift": shift,
            "Quality": quality,
            "Weight 1 (gm)": weight1,
            "MR% 1": mr1,
            "Actual Weight 1 (kg)": round(actual_weight1, 4),
            "Converted Weight 1 (kg)": round(converted_weight1, 4),
            "Weight 2 (gm)": weight2,
            "MR% 2": mr2,
            "Actual Weight 2 (kg)": round(actual_weight2, 4),
            "Converted Weight 2 (kg)": round(converted_weight2, 4),
            "Average Converted Weight (kg)": round(avg_converted, 4),
            "Remarks": remarks,
            "Flag Status": "✅ OK" if not flagged_error else "🚩 Invalid Entry"
        }

        # --- Save locally ---
        df = pd.DataFrame([record])
        try:
            existing = pd.read_csv("inter_card_rollfeed_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("inter_card_rollfeed_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("inter_card_rollfeed_records.csv", index=False)

        # --- Push to Flask + MongoDB ---
        status = post_to_sap_intercard(record)
        if status == "success":
            st.success("✅ Record submitted and stored in MongoDB successfully!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check server connection or logs.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Inter Card Section — Streamlit + Flask + MongoDB Integration")
