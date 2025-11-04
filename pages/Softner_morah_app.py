import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_softner import post_to_sap_softner  # 🔗 Flask + MongoDB Integration

# ==============================
# 🧾 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="Softner Morah Weight Entry", layout="centered")
st.title("📒 Softner Morah Weight Record")

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
# 1️⃣ BASIC INFO
# ==============================
st.subheader("1️⃣ Basic Information")
today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

# ==============================
# 2️⃣ OPERATORS & QUALITY
# ==============================
st.subheader("2️⃣ Operators and Quality")
operators = []
operator_qualities = {}
invalid_name_flag = False

for i in range(4):
    op_name = st.text_input(f"Operator {i+1} Name", value=f"Operator {i+1}")

    if op_name.strip().isdigit():
        st.error(f"⚠️ Operator {i+1} name cannot be a number!")
        invalid_name_flag = True

    operators.append(op_name)
    quality = st.selectbox(
        f"Quality for {op_name}",
        ["Hessian", "Sacking Warp", "Special Sacking Warp S4", "S4 Weft"],
        key=f"quality_{op_name}"
    )
    operator_qualities[op_name] = quality

# ==============================
# 3️⃣ MORAH WEIGHTS ENTRY
# ==============================
st.subheader("3️⃣ Enter Morah Weights (gm)")
max_rows = st.number_input("Number of morahs per operator", min_value=1, value=10, step=1)
morah_data = {op: [] for op in operators}
negative_flag = False

for op in operators:
    st.markdown(f"#### {op} ({operator_qualities[op]})")
    for idx in range(max_rows):
        weight = st.number_input(f"Morah {idx+1} Weight for {op} (gm)", step=1.0, key=f"{op}_{idx}")
        if weight < 0:
            st.error(f"⚠️ Negative weight detected for {op} at Morah {idx+1}!")
            negative_flag = True
        morah_data[op].append(weight)

# ==============================
# 4️⃣ TOTALS & AVERAGES
# ==============================
st.subheader("4️⃣ Totals, Average, and Weight Range")
totals, averages, weight_ranges = {}, {}, {}

for op in operators:
    weights = morah_data[op]
    totals[op] = sum(weights)
    averages[op] = round(totals[op] / len(weights), 2) if weights else 0
    min_wt = min(weights) if weights else 0
    max_wt = max(weights) if weights else 0
    weight_ranges[op] = (min_wt, max_wt)

    st.write(f"**{op} ({operator_qualities[op]})** — Total: {totals[op]} gm | Average: {averages[op]} gm")
    st.caption(f"Lowest: {min_wt} gm | Highest: {max_wt} gm")

# 🚩 Warnings
if invalid_name_flag:
    st.warning("🚩 Invalid Operator Name(s): Names cannot be numeric.")
if negative_flag:
    st.warning("🚩 Invalid Weight(s): Negative values detected.")

# ==============================
# 5️⃣ SUBMIT RECORD
# ==============================
if st.button("📤 Submit Morah Record"):
    if invalid_name_flag or negative_flag:
        st.error("❌ Submission blocked due to invalid inputs.")
    else:
        records = []
        for op in operators:
            record = {
                "Date": str(record_date),
                "Operator": op,
                "Quality": operator_qualities[op],
                "Total Weight (gm)": totals[op],
                "Average Weight (gm)": averages[op],
                "Min Weight (gm)": weight_ranges[op][0],
                "Max Weight (gm)": weight_ranges[op][1]
            }
            records.append(record)

        df = pd.DataFrame(records)

        # --- Save locally ---
        try:
            existing = pd.read_csv("softner_morah_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("softner_morah_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("softner_morah_records.csv", index=False)

        # --- Push to Flask + MongoDB ---
        success_count = 0
        for rec in records:
            status = post_to_sap_softner(rec)
            if status == "success":
                success_count += 1

        if success_count == len(records):
            st.success(f"✅ {success_count} records submitted and stored in MongoDB successfully!")
        else:
            st.warning("⚠️ Some records saved locally only — check Flask/MongoDB connection.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Softner Section — Streamlit + Flask + MongoDB Integration")
