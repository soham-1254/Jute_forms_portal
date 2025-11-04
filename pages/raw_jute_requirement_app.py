import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_rawjute import post_to_sap_rawjute  # 🔗 Integration with Flask + MongoDB

# =====================================================
# 🧾 PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Raw Jute Requirement & Issue Report", layout="centered")
st.title("🌾 Raw Jute Requirement & Issue Report")

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
# 1️⃣ BASIC DETAILS
# =====================================================
st.subheader("1️⃣ Basic Information")

today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("📅 Select Date", value=today, min_value=min_date, max_value=today)

batch_type = st.selectbox(
    "Select Batch Type",
    ["SALE YARN", "TEA BAG", "HESSIAN", "SKG. WARP", "SKG. WEFT"],
)

# =====================================================
# 2️⃣ QUALITY-WISE ENTRY
# =====================================================
st.subheader("2️⃣ Quality-Wise Requirement & Issue Entry")

quality_list = [
    "B6", "B7", "A6", "A7", "BTD6", "TD6", "SN9", "SN10", "SB6",
    "Good A5", "N10", "SB4", "SN8", "N8", "SB5", "SN5", "SN11"
]

num_rows = st.number_input("Enter Number of Quality Rows", min_value=1, max_value=10, value=4, step=1)
data = []

for i in range(num_rows):
    st.markdown(f"#### 🔹 Entry {i+1}")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        quality = st.selectbox("Quality", quality_list, key=f"quality_{i}")
    with c2:
        req_mill = st.number_input("Req (Mill)", min_value=0.0, step=1.0, key=f"req_mill_{i}")
    with c3:
        req_katary = st.number_input("Req (Katary)", min_value=0.0, step=1.0, key=f"req_katary_{i}")
    with c4:
        iss_mill = st.number_input("Issue (Mill)", min_value=0.0, step=1.0, key=f"iss_mill_{i}")
    with c5:
        iss_katary = st.number_input("Issue (Katary)", min_value=0.0, step=1.0, key=f"iss_katary_{i}")
    with c6:
        remark = st.text_input("Remark", key=f"remark_{i}")

    data.append({
        "Quality": quality,
        "Req_Mill": req_mill,
        "Req_Katary": req_katary,
        "Iss_Mill": iss_mill,
        "Iss_Katary": iss_katary,
        "Remark": remark.strip()
    })

# =====================================================
# 3️⃣ TOTAL CALCULATION
# =====================================================
st.subheader("3️⃣ Total Summary")

df = pd.DataFrame(data)
total_req = df["Req_Mill"].sum() + df["Req_Katary"].sum()
total_iss = df["Iss_Mill"].sum() + df["Iss_Katary"].sum()

colA, colB = st.columns(2)
with colA:
    st.metric("📦 Total Requirement", f"{total_req:.2f}")
with colB:
    st.metric("🚚 Total Issue", f"{total_iss:.2f}")

# =====================================================
# 4️⃣ SUBMIT RECORD
# =====================================================
st.subheader("4️⃣ Submit Report")

if st.button("📤 Submit Record"):
    # Validation at submission only
    invalid_rows = [
        i + 1 for i, row in enumerate(data)
        if any(value < 0 for value in [row["Req_Mill"], row["Req_Katary"], row["Iss_Mill"], row["Iss_Katary"]])
    ]

    if invalid_rows:
        st.error(f"❌ Submission blocked. Negative values found in row(s): {invalid_rows}")
    else:
        record = {
            "Date": str(record_date),
            "Batch": batch_type,
            "Entries": data,
            "Total_Requirement": total_req,
            "Total_Issue": total_iss
        }

        status = post_to_sap_rawjute(record)

        if status == "success":
            st.success("✅ Record successfully submitted to Mock SAP Server and stored in MongoDB!")
        else:
            st.warning("⚠️ Validation passed but data push failed — check connection or logs.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Hastings Mill — Raw Jute Requirement & Issue Digital Register (Streamlit + Flask + MongoDB)")
