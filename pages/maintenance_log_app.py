import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_maintenance import post_to_sap_maintenance  # 🔗 Flask + MongoDB integration

# -------------------------------------------------------
# 🧾 PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="Maintenance Log Book", layout="centered")
st.title("🧰 Maintenance Log Book — Department Wise with Validation Flags")

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
    ["Batching", "Carding", "Drawing", "Spinning", "Winding", "Maintenance Workshop", "Other"]
)

# -------------------------------------------------------
# 2️⃣ MACHINE & JOB DETAILS
# -------------------------------------------------------
st.subheader("2️⃣ Machine & Job Details")

machine_no = st.text_input("Machine / Section Code", placeholder="e.g., B/C-28, I/C-06, A0, CM")
job_done = st.text_area(
    "Work Description / Job Done",
    placeholder="Describe maintenance or repair activity performed",
    height=120
)
contractor_name = st.text_input("Done By (Contractor / Group Name)", placeholder="e.g., Debu Group, Bijoy Group")
remarks = st.text_input("Remarks / Status", placeholder="e.g., Running fine, Checked by staff, Lubrication done")

# -------------------------------------------------------
# 3️⃣ VALIDATION LOGIC
# -------------------------------------------------------
null_fields = []
if not machine_no.strip():
    null_fields.append("Machine / Section Code")
if not job_done.strip():
    null_fields.append("Job Description")
if not contractor_name.strip():
    null_fields.append("Done By")

null_flag = "YES" if null_fields else "NO"
validation_status = "FAILED" if null_fields else "PASSED"
empty_field_list = ", ".join(null_fields) if null_fields else "None"

# -------------------------------------------------------
# 4️⃣ FILE NAMING
# -------------------------------------------------------
file_name = f"{department.lower().replace(' ', '_')}_log.csv"

# -------------------------------------------------------
# 5️⃣ SUBMIT SECTION
# -------------------------------------------------------
if st.button("📤 Submit Maintenance Entry", use_container_width=True):
    record = {
        "Date": str(record_date),
        "Department": department,
        "Machine / Section Code": machine_no.strip(),
        "Job Description": job_done.strip(),
        "Done By": contractor_name.strip(),
        "Remarks / Status": remarks.strip(),
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
    status_code = post_to_sap_maintenance(record)

    if status_code == "success":
        st.success(f"✅ Record successfully saved in MongoDB and locally in {file_name}")
    else:
        st.warning("⚠️ Saved locally. MongoDB push failed — check Flask server connection.")

    st.dataframe(df)

st.markdown("---")
st.caption("Developed for Maintenance Department — Streamlit + Flask + MongoDB Integration")
