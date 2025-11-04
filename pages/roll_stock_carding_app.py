import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_rollstock import post_to_sap_rollstock  # 🔗 Flask + MongoDB Integration

# =====================================================
# 🧾 PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Roll Stock Carding", layout="centered")
st.title("📋 Roll Stock Carding")

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

today = date.today()
min_date = today - timedelta(days=5)

# =====================================================
# 1️⃣ Daily Cutting Section
# =====================================================
st.subheader("1️⃣ Daily Cutting Section (K & L Cutting)")

cutting_date = st.date_input("Select Date for Cutting", key="cutting_date",
                             value=today, min_value=min_date, max_value=today)

try:
    cutting_records = pd.read_csv("cutting_records.csv")
except FileNotFoundError:
    cutting_records = pd.DataFrame(columns=["Date", "K-Cutting (m)", "L-Cutting (m)"])

existing_cutting = cutting_records.loc[cutting_records["Date"] == str(cutting_date)]

if not existing_cutting.empty:
    st.info(f"✅ Cutting already recorded for {cutting_date}:")
    st.dataframe(existing_cutting)
else:
    k_cutting = st.number_input("K-Cutting (m)", step=0.5, key="k_cutting")
    l_cutting = st.number_input("L-Cutting (m)", step=0.5, key="l_cutting")

    if k_cutting < 0 or l_cutting < 0:
        st.error("🚩 Cutting values cannot be negative.")
    else:
        if st.button("📤 Submit Cutting Record"):
            record = {
                "Date": str(cutting_date),
                "K-Cutting (m)": k_cutting,
                "L-Cutting (m)": l_cutting,
                "Record Type": "Cutting"
            }

            # Save locally
            df = pd.DataFrame([record])
            updated = pd.concat([cutting_records, df], ignore_index=True)
            updated.to_csv("cutting_records.csv", index=False)

            # Push to MongoDB via Flask
            status = post_to_sap_rollstock(record)

            if status == "success":
                st.success("✅ Cutting record saved successfully to MongoDB!")
            else:
                st.warning("⚠️ Saved locally, but MongoDB push failed — check server.")
            st.dataframe(df)

# =====================================================
# 2️⃣ Daily Production & Roll Stock Form
# =====================================================
st.markdown("---")
st.subheader("2️⃣ Daily Production & Roll Stock")

production_date = st.date_input("Select Date", key="prod_date",
                                value=today, min_value=min_date, max_value=today)

quality_types = [
    "TOW X", "TOW Inter", "1st Inter", "2nd Inter", "F/Roll", "L/Jute III",
    "A/G", "LJ/W", "Sweep O", "Cutting C", "Cutt Inter C", "Mesta M",
    "L/Jute NI", "H/J H", "#", "R1"
]
quality_type = st.selectbox("Select Quality Type", quality_types)
frame_type = st.selectbox("Select Frame Type", ["5½", "4¾"])
remarks = st.text_input("Remarks (optional)")

time_slots = ["6 AM", "11 AM", "2 PM", "5 PM", "10 PM"]
selected_slots = st.multiselect("Select Time Slots", time_slots)

roll_stock_data = {}
if selected_slots:
    st.write("Enter Roll Stock Availability (in MT):")
    for slot in selected_slots:
        val = st.number_input(f"Roll Stock at {slot}", step=0.1, key=f"roll_{slot}_{production_date}")
        roll_stock_data[slot] = val

# =====================================================
# 3️⃣ Submit Production Record
# =====================================================
if st.button("📤 Submit Production Record"):
    if not selected_slots:
        st.error("⚠️ Please select at least one time slot before submitting!")
    elif any(val < 0 for val in roll_stock_data.values()):
        st.error("🚫 Invalid input: Negative roll stock values detected.")
    else:
        record = {
            "Date": str(production_date),
            "Quality Type": quality_type,
            "Frame Type": frame_type,
            "Remarks": remarks,
            "Record Type": "Production"
        }
        for slot, val in roll_stock_data.items():
            record[f"Roll Stock {slot} (MT)"] = val

        try:
            prod_records = pd.read_csv("roll_stock_records.csv")
        except FileNotFoundError:
            prod_records = pd.DataFrame()

        df = pd.DataFrame([record])
        updated = pd.concat([prod_records, df], ignore_index=True)
        updated.to_csv("roll_stock_records.csv", index=False)

        # Push to MongoDB
        status = post_to_sap_rollstock(record)
        if status == "success":
            st.success("✅ Production record saved to MongoDB!")
        else:
            st.warning("⚠️ Saved locally, MongoDB push failed — check Flask server.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Carding Department — Roll Stock Entry Digitization (Streamlit + MongoDB)")
