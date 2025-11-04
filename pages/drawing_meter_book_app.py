import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_drawingmeter import post_to_sap_drawingmeter
# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Drawing Meter Book", layout="centered")
st.title("📘 Drawing Meter Book Entry Form")

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

# -------------------------------
# 1️⃣ BASIC INFORMATION
# -------------------------------
st.subheader("1️⃣ Basic Information")

today = date.today()
min_date = today - timedelta(days=5)

record_date = st.date_input(
    "Select Date",
    value=today,
    min_value=min_date,
    max_value=today
)

shift = st.selectbox("Select Shift", ["A", "B", "C"])
machine_type = st.selectbox(
    "Select Machine Type",
    ["1st Drawing", "2nd Drawing", "3rd Drawing"]
)
machine_number = st.number_input("Enter Machine Number", min_value=1, step=1)

# -------------------------------
# 2️⃣ MACHINE PERFORMANCE ENTRY
# -------------------------------
st.subheader("2️⃣ Machine Performance Data")

eff_100 = st.number_input("Machine Efficiency at 100% (m/min)", min_value=0.0, step=0.1)

col1, col2, col3 = st.columns(3)

with col1:
    opening = st.number_input("Opening (m)", min_value=0.0, step=0.1)
with col2:
    closing = st.number_input("Closing (m)", min_value=0.0, step=0.1)
with col3:
    difference = closing - opening if closing >= opening else 0
    st.metric("Difference (m)", f"{difference:.2f}")

# -------------------------------
# 3️⃣ EFFICIENCY CALCULATION
# -------------------------------
st.subheader("3️⃣ Recorded Efficiency")

if eff_100 > 0:
    recorded_eff = (difference / eff_100) * 100
else:
    recorded_eff = 0.0

st.metric("Recorded Efficiency (%)", f"{recorded_eff:.2f}")

# -------------------------------
# 4️⃣ VALIDATION CHECKS
# -------------------------------
flag_error = False
if closing < opening:
    st.error("⚠️ Closing reading cannot be less than Opening reading.")
    flag_error = True
if any(v < 0 for v in [opening, closing, eff_100]):
    st.error("⚠️ Negative values are not allowed.")
    flag_error = True

remarks = st.text_input("Remarks (optional)")

# -------------------------------
# 5️⃣ SUBMIT & SAVE
# -------------------------------
if st.button("Submit Entry"):
    if flag_error:
        st.error("🚫 Submission blocked due to invalid or negative values.")
    else:
        record = {
            "Date": str(record_date),
            "Shift": shift,
            "Machine Type": machine_type,
            "Machine Number": machine_number,
            "Efficiency@100%": eff_100,
            "Opening (m)": opening,
            "Closing (m)": closing,
            "Difference (m)": round(difference, 2),
            "Recorded Efficiency (%)": round(recorded_eff, 2),
            "Remarks": remarks
        }

        df = pd.DataFrame([record])

        # Save or append to CSV
        try:
            existing = pd.read_csv("drawing_meter_book_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("drawing_meter_book_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("drawing_meter_book_records.csv", index=False)

        st.success("✅ Drawing Meter Record Saved Successfully!")
        st.dataframe(df)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Developed for Drawing Department — Streamlit Digitization Form")
