import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_breaker import post_to_sap_breaker  # 🔗 Integration with Flask + MongoDB

# ==============================
# 🧾 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="Breaker Card Rollfeed Entry", layout="centered")
st.title("📘 Breaker Card Rollfeed")

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

quality_options = ["B", "(B)", "K", "J", "S", "T", "A", "P", "O", "I I", "H", "M"]
quality = st.selectbox("Select Quality", quality_options)

# ==============================
# 2️⃣ MACHINE / DAY / SHIFT
# ==============================
st.subheader("2️⃣ Machine and Shift Details")

# Machine mapping dictionary
machine_map = {
    "B.CRD-04": "030BC004",
    "B.CRD-05": "030BC005",
    "B.CRD-06": "030BC006",
    "B.CRD-07": "030BC007",
    "B.CRD-16": "030BC016",
    "B.CRD-17": "030BC017",
    "B.CRD-18": "030BC018",
    "B.CRD-19": "030BC019",
    "B.CRD-21": "030BC021",
    "B.CRD-22": "030BC022",
    "B.CRD-23": "030BC023",
    "B.CRD-24": "030BC024"
}

# Dropdown for machine number
machine_no = st.selectbox("Select Machine Number", list(machine_map.keys()))

# Display SAP Machine No.
sap_machine_no = machine_map[machine_no]
st.markdown(f"**🔹 SAP Machine No.: `{sap_machine_no}`**")

# Day & Shift
day_options = [
    "1", "2", "3", "4", "5", "6", "7",
    "1-Saturday", "2-Sunday", "3-Monday", "4-Tuesday",
    "5-Wednesday", "6-Thursday", "7-Friday"
]
selected_day = st.selectbox("Select Day", day_options)
shift = st.selectbox("Select Shift", ["A", "B", "C"])

# ==============================
# 3️⃣ MEASUREMENT SECTION
# ==============================
st.subheader("3️⃣ Weight and MR% Entry")

flagged_error = False  # 🚩 For validation

# --- Entry 1 ---
st.markdown("#### 🔹 Entry 1")
col1, col2 = st.columns(2)
with col1:
    weight1 = st.number_input("Weight 1 (gm)", step=0.1, key="w1")
with col2:
    mr1 = st.number_input("MR% 1", step=0.1, key="mr1")

if weight1 < 0:
    st.error("⚠️ Weight 1 cannot be negative.")
    flagged_error = True
if mr1 < 0 or mr1 >= 50:
    st.error("⚠️ MR% 1 must be between 0 and 50.")
    flagged_error = True

actual_1 = weight1 * 0.0440917 if weight1 >= 0 else 0
converted_1 = (actual_1 * 120) / (mr1 + 100) if (0 <= mr1 < 50) else 0

st.metric("Actual Weight 1 (kg)", f"{actual_1:.4f}")
st.metric("Converted Weight 1 (kg)", f"{converted_1:.4f}")

# --- Entry 2 ---
st.markdown("#### 🔹 Entry 2")
col3, col4 = st.columns(2)
with col3:
    weight2 = st.number_input("Weight 2 (gm)", step=0.1, key="w2")
with col4:
    mr2 = st.number_input("MR% 2", step=0.1, key="mr2")

if weight2 < 0:
    st.error("⚠️ Weight 2 cannot be negative.")
    flagged_error = True
if mr2 < 0 or mr2 >= 50:
    st.error("⚠️ MR% 2 must be between 0 and 50.")
    flagged_error = True

actual_2 = weight2 * 0.0440917 if weight2 >= 0 else 0
converted_2 = (actual_2 * 120) / (mr2 + 100) if (0 <= mr2 < 50) else 0

st.metric("Actual Weight 2 (kg)", f"{actual_2:.4f}")
st.metric("Converted Weight 2 (kg)", f"{converted_2:.4f}")

# ==============================
# 4️⃣ AVERAGE SECTION
# ==============================
st.subheader("4️⃣ Average Converted Weight")

avg_converted = 0.0
if converted_1 > 0 or converted_2 > 0:
    avg_converted = (converted_1 + converted_2) / 2

st.success(f"✅ Average Converted Weight: {avg_converted:.4f} kg")

remarks = st.text_input("Remarks (optional)")

# ==============================
# 5️⃣ SUBMIT & SAVE
# ==============================
if st.button("📤 Submit Record"):
    if flagged_error:
        st.error("🚩 Submission blocked due to invalid entries.")
    else:
        record = {
            "Date": str(record_date),
            "Quality": quality,
            "Machine No": machine_no,
            "SAP Machine No": sap_machine_no,
            "Day": selected_day,
            "Shift": shift,
            "Weight 1 (gm)": weight1,
            "MR% 1": mr1,
            "Actual Weight 1 (kg)": round(actual_1, 4),
            "Converted Weight 1 (kg)": round(converted_1, 4),
            "Weight 2 (gm)": weight2,
            "MR% 2": mr2,
            "Actual Weight 2 (kg)": round(actual_2, 4),
            "Converted Weight 2 (kg)": round(converted_2, 4),
            "Average Converted Weight (kg)": round(avg_converted, 4),
            "Remarks": remarks,
            "Flag Status": "✅ OK" if not flagged_error else "🚩 Invalid Entry"
        }

        # --- Save locally ---
        df = pd.DataFrame([record])
        try:
            existing = pd.read_csv("breaker_card_rollfeed_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("breaker_card_rollfeed_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("breaker_card_rollfeed_records.csv", index=False)

        # --- Push to Flask + MongoDB ---
        status = post_to_sap_breaker(record)
        if status == "success":
            st.success("✅ Record submitted and stored in MongoDB successfully!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check connection or server log.")

        st.dataframe(df)

st.caption("Developed for Breaker Card Department — Streamlit + Flask + MongoDB Integration")
