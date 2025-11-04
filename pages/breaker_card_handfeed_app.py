import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_breakerhand import post_to_sap_breakerhand  # 🔗 Integration with Flask + MongoDB

# ==============================
# 🧾 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="Breaker Card Hand Feed Khata", layout="centered")
st.title("📘 Breaker Card Hand Feed Khata")

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
today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

quality_options = ["A6", "A4", "A5", "A7", "B", "J"]
quality = st.selectbox("Select Quality", quality_options)

# ==============================
# 2️⃣ MACHINE & MEASUREMENT ENTRY
# ==============================
st.subheader("2️⃣ Machine & Measurement Entry")

# Machine mapping: Display + SAP code
machine_map = {
    "B.CRD-09": "030BC009",
    "B.CRD-10": "030BC010",
    "B.CRD-11": "030BC011",
    "B.CRD-12": "030BC012",
    "B.CRD-13": "030BC013",
    "B.CRD-14": "030BC014",
    "B.CRD-15": "030BC015"
}

# Dropdown for machine number
machine_no = st.selectbox("Select Machine Number", list(machine_map.keys()))

# Display SAP Machine No.
sap_machine_no = machine_map[machine_no]
st.markdown(f"**🔹 SAP Machine No.: `{sap_machine_no}`**")

# ==============================
# 3️⃣ MEASUREMENTS ENTRY
# ==============================
st.markdown("#### 🔹 Enter Measurements for Two Readings")

col1, col2 = st.columns(2)
with col1:
    weight_1 = st.number_input("Weight 1 (gm)", step=0.1, key="w1")
    mr_1 = st.number_input("MR% 1", step=0.1, key="mr1")

with col2:
    weight_2 = st.number_input("Weight 2 (gm)", step=0.1, key="w2")
    mr_2 = st.number_input("MR% 2", step=0.1, key="mr2")

# --- Validation ---
flagged_error = False
if weight_1 < 0 or mr_1 < 0 or mr_1 > 50:
    st.error("⚠️ Invalid Entry: Weight 1 or MR% 1 out of range.")
    flagged_error = True
if weight_2 < 0 or mr_2 < 0 or mr_2 > 50:
    st.error("⚠️ Invalid Entry: Weight 2 or MR% 2 out of range.")
    flagged_error = True

# --- Calculations ---
actual_1 = weight_1 * 0.0440917 if weight_1 > 0 else 0
converted_1 = (actual_1 * 120) / (mr_1 + 100) if (mr_1 >= 0 and mr_1 < 50) else 0
actual_2 = weight_2 * 0.0440917 if weight_2 > 0 else 0
converted_2 = (actual_2 * 120) / (mr_2 + 100) if (mr_2 >= 0 and mr_2 < 50) else 0

avg_converted = 0.0
if converted_1 > 0 or converted_2 > 0:
    avg_converted = (converted_1 + converted_2) / 2

st.subheader(f"📊 Average of Converted Weights: {avg_converted:.4f} kg")

remarks = st.text_input("Remarks (optional)")

# ==============================
# 4️⃣ SUBMIT & SAVE
# ==============================
if st.button("📤 Submit Record"):
    if flagged_error:
        st.error("🚩 Submission blocked — please correct invalid fields.")
    else:
        record = {
            "Date": str(record_date),
            "Quality": quality,
            "Machine No": machine_no,
            "SAP Machine No": sap_machine_no,
            "Weight 1 (gm)": weight_1,
            "MR% 1": mr_1,
            "Actual Weight 1 (kg)": round(actual_1, 4),
            "Converted Weight 1 (kg)": round(converted_1, 4),
            "Weight 2 (gm)": weight_2,
            "MR% 2": mr_2,
            "Actual Weight 2 (kg)": round(actual_2, 4),
            "Converted Weight 2 (kg)": round(converted_2, 4),
            "Average Converted Weight (kg)": round(avg_converted, 4),
            "Remarks": remarks,
            "Flag Status": "✅ OK" if not flagged_error else "🚩 Invalid Entry"
        }

        # --- Save locally ---
        df = pd.DataFrame([record])
        try:
            existing = pd.read_csv("breaker_card_handfeed_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("breaker_card_handfeed_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("breaker_card_handfeed_records.csv", index=False)

        # --- Push to Flask + MongoDB ---
        status = post_to_sap_breakerhand(record)
        if status == "success":
            st.success("✅ Record submitted and stored in MongoDB successfully!")
        else:
            st.warning("⚠️ Saved locally — MongoDB push failed. Check server log.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Breaker Card Department — Streamlit + Flask + MongoDB Integration")
