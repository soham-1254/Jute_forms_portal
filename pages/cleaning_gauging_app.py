import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_cleaning import post_to_sap_cleaning  # 🔗 Integration with Flask + MongoDB

# -------------------------------------------------------
# 🧾 PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="M/c Cleaning & Gauging Job", layout="centered")
st.title("🧰 M/c Cleaning & Gauging Job Register")

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

# -------------------------------------------------------
# 1️⃣ BASIC INFORMATION
# -------------------------------------------------------
st.subheader("1️⃣ Basic Information")

min_date = date.today() - timedelta(days=5)
max_date = date.today()
record_date = st.date_input(
    "Select Date",
    value=date.today(),
    min_value=min_date,
    max_value=max_date
)

department = st.selectbox(
    "Select Department",
    ["Carding", "Batching", "Drawing", "Spinning", "Winding", "Maintenance Workshop", "Other"]
)

# -------------------------------------------------------
# 2️⃣ MACHINE DETAILS
# -------------------------------------------------------
st.subheader("2️⃣ Machine Details")

machine_type = st.text_input("Machine Type (Mandatory)", placeholder="e.g., Fin. Card, Breaker Card, Draw Frame")
machine_no = st.number_input("Machine Number", min_value=1, step=1)

# -------------------------------------------------------
# 3️⃣ CONTRACTOR & STAFF DETAILS
# -------------------------------------------------------
st.subheader("3️⃣ Contractor & Staff Details")

contractor_name = st.text_input("Name of Contractor / Group", placeholder="e.g., Debu Group, Bijoy Group")
mech_staff = st.text_input("Sign / Name of Mech. Staff", placeholder="e.g., Banasri, Biswajit")
status = st.selectbox("Status", ["Paid", "Unpaid"])

# -------------------------------------------------------
# 4️⃣ VALIDATION CHECK
# -------------------------------------------------------
null_fields = []
if not machine_type.strip():
    null_fields.append("Machine Type")
if not contractor_name.strip():
    null_fields.append("Contractor Name")
if not mech_staff.strip():
    null_fields.append("Mech Staff")

null_flag = "YES" if null_fields else "NO"
validation_status = "FAILED" if null_fields else "PASSED"
empty_field_list = ", ".join(null_fields) if null_fields else "None"

# -------------------------------------------------------
# 5️⃣ FILE NAMING
# -------------------------------------------------------
file_name = f"{department.lower().replace(' ', '_')}_cleaning_gauging.csv"

# -------------------------------------------------------
# 6️⃣ SUBMIT & SAVE
# -------------------------------------------------------
if st.button("📤 Submit Cleaning & Gauging Record", use_container_width=True):
    record = {
        "Date": str(record_date),
        "Department": department,
        "Machine Type": machine_type.strip(),
        "Machine Number": machine_no,
        "Contractor Name": contractor_name.strip(),
        "Mech Staff": mech_staff.strip(),
        "Status": status,
        "NULL_CHECK": null_flag,
        "EMPTY_FIELDS": empty_field_list,
        "VALIDATION_STATUS": validation_status
    }

    df = pd.DataFrame([record])

    # --- Save locally ---
    try:
        existing = pd.read_csv(file_name)
        updated = pd.concat([existing, df], ignore_index=True)
        updated.to_csv(file_name, index=False)
    except FileNotFoundError:
        df.to_csv(file_name, index=False)

    # --- Push to Flask + MongoDB ---
    status_code = post_to_sap_cleaning(record)

    if status_code == "success":
        st.success(f"✅ Record saved successfully in DB (Flask + MongoDB) and CSV: **{file_name}**")
    else:
        st.warning(f"⚠️ Saved locally. DB push failed — check Flask server connection.")

    st.dataframe(df)

st.markdown("---")
st.caption("Developed for Carding Department — Streamlit + Flask + MongoDB Integration")
