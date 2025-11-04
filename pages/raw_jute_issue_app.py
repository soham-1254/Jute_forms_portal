import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_rawjuteissue import post_to_sap_rawjuteissue

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Raw Jute Issue Slip", layout="centered")
st.title("📦 Raw Jute Issue Slip Entry Form")

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
# 1️⃣ Basic Details
# =====================================================
st.subheader("1️⃣ Basic Information")

today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

# =====================================================
# 2️⃣ Issue Details
# =====================================================
st.subheader("2️⃣ Issue Details")

godown_number = st.selectbox("Select Godown Number", ["H2", "G2", "F2", "A2"])
grade = st.selectbox("Select Grade", ["TD10", "TD5", "TD7"])
mill_grade = st.selectbox("Select Mill Grade", ["TD10H", "TD5A", "TD7A"])
section = st.selectbox("Select Section", ["Hessian", "Sacking", "15LBS"])
marks = st.text_input("Enter Marks", placeholder="e.g., Tarabari SA, Mandeep Sunil")

# =====================================================
# 3️⃣ Tally & Katary Details
# =====================================================
st.subheader("3️⃣ Tally and Katary Details")
tally_bales = st.number_input("Tally of Bales", min_value=0, step=1)
katary_name = st.text_input("Katary Name", placeholder="Enter Katary Name")

# =====================================================
# 4️⃣ Validations
# =====================================================
flag_error = False

if tally_bales <= 0:
    st.error("⚠️ Tally of Bales must be greater than 0.")
    flag_error = True
if not marks.strip():
    st.error("⚠️ Marks cannot be empty.")
    flag_error = True
if not katary_name.strip():
    st.error("⚠️ Katary Name cannot be empty.")
    flag_error = True

# =====================================================
# 5️⃣ Submission
# =====================================================
if st.button("📤 Submit Issue Slip"):
    if flag_error:
        st.error("🚫 Submission blocked due to invalid or missing data.")
    else:
        record = {
            "Date": str(record_date),
            "Godown Number": godown_number,
            "Grade": grade,
            "Mill Grade": mill_grade,
            "Section": section,
            "Marks": marks.strip(),
            "Tally of Bales": tally_bales,
            "Katary Name": katary_name.strip(),
        }

        df = pd.DataFrame([record])

        # Save locally
        try:
            existing = pd.read_csv("raw_jute_issue_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("raw_jute_issue_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("raw_jute_issue_records.csv", index=False)

        # Push to Flask + MongoDB
        status = post_to_sap_rawjuteissue(record)

        if status == "success":
            st.success("✅ Record submitted successfully and stored in MongoDB!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check server log.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Raw Jute Department — Streamlit Data Entry Form with Validation & MongoDB Integration")
