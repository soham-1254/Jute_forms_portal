import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_rollstockavail import post_to_sap_rollstockavail  # 🔗 Flask + MongoDB Integration

# =====================================================
# 🧾 PAGE CONFIGURATION
# =====================================================
st.set_page_config(page_title="Roll Stock Availability", layout="centered")
st.title("📋 Roll Stock Availability Entry")

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
st.subheader("1️⃣ Basic Details")
today = date.today()
min_date = today - timedelta(days=5)
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

quality_options = ['P', 'O', 'T', 'X', 'B', 'K', 'J', 'I', 'L', 'A', 'S', 'R']
selected_quality = st.selectbox("Select Quality", quality_options)

# =====================================================
# 2️⃣ Maturity Hours
# =====================================================
st.subheader("2️⃣ Maturity Hours")
maturity_hours = st.number_input(f"Enter Maturity Hours for {selected_quality}", min_value=0, step=1)

# =====================================================
# 3️⃣ Stock Availability
# =====================================================
st.subheader("3️⃣ Stock Availability (MT)")
time_slots = ['6 AM', '11 AM', '2 PM', '5 PM', '10 PM']
stock_availability = {}
flag_raised = False

for slot in time_slots:
    val = st.number_input(f"Stock at {slot} for {selected_quality}", step=1.0, key=f"stock_{slot}")
    if val < 0:
        st.error(f"⚠️ Stock at {slot} cannot be negative!")
        flag_raised = True
    stock_availability[slot] = val

if flag_raised:
    st.warning("🚩 Negative value(s) detected. Please correct before submitting.")

# =====================================================
# 4️⃣ Submit Button
# =====================================================
if st.button("Submit Roll Stock Record"):
    if maturity_hours < 0 or any(v < 0 for v in stock_availability.values()):
        st.error("❌ Submission blocked. Negative values detected.")
    else:
        record = {
            'Date': str(record_date),
            'Quality': selected_quality,
            'Maturity Hours': maturity_hours,
        }
        for slot, val in stock_availability.items():
            record[slot] = val

        df = pd.DataFrame([record])

        # --- Save locally
        try:
            existing = pd.read_csv("roll_stock_availability.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("roll_stock_availability.csv", index=False)
        except FileNotFoundError:
            df.to_csv("roll_stock_availability.csv", index=False)

        # --- Push to Flask + MongoDB
        status = post_to_sap_rollstockavail(record)
        if status == "success":
            st.success(f"✅ Roll Stock record for {selected_quality} saved to MongoDB successfully!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check server logs.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Roll Stock Availability — Streamlit + Flask + MongoDB Integration")
