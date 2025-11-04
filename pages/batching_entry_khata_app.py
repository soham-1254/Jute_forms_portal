import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_batching import post_to_sap_batching  # 🔗 Flask + MongoDB Integration

# =====================================================
# 🧭 PAGE CONFIGURATION
# =====================================================
st.set_page_config(page_title="Batching Entry Forms", layout="centered")
st.title("📋 Batching Department Entry Forms — Streamlit + Flask + MongoDB Integration")

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


shift_options = ['A', 'B', 'C']
today = date.today()
min_date = today - timedelta(days=5)

# =====================================================
# 1️⃣ MACHINE ALLOCATION FORM
# =====================================================
st.header("1️⃣ Machine Allocation")
record_date_machine = st.date_input("Select Date (Machine Allocation)", value=today, min_value=min_date, max_value=today, key="machine_date")

machine_options = ["Spreader", "Softner", "Inter Spreader", "Ropes & Habijabi", "Cutting"]
machine = st.selectbox("Select Machine", machine_options, key="machine_dropdown")
shift = st.selectbox("Select Shift", shift_options, key="machine_shift")

approx_production = st.number_input(f"Approx Production for {machine} - Shift {shift} (MT/EA)", step=0.01, key="machine_approx")

flag_machine = approx_production < 0
if flag_machine:
    st.error("🚩 Approx Production cannot be negative.")

if st.button("Submit Machine Allocation"):
    record = {
        "FormType": "Machine Allocation",
        "Date": str(record_date_machine),
        "Machine": machine,
        "Shift": shift,
        "Approx Production (MT/EA)": approx_production
    }

    df = pd.DataFrame([record])
    df.to_csv("batching_machine_records.csv", mode="a", index=False, header=False)

    status = post_to_sap_batching(record)
    if status == "success":
        st.success("✅ Record saved & sent to MongoDB successfully!")
    else:
        st.warning("⚠️ Saved locally. MongoDB push failed.")

    st.dataframe(df)

# =====================================================
# 2️⃣ PILE MADE FORM
# =====================================================
st.header("2️⃣ Pile Made (TON)")
pile_qualities = ["BTR", "A5", "A6", "A7"]
record_date_pile = st.date_input("Select Date (Pile Made)", value=today, min_value=min_date, max_value=today, key="pile_date")
selected_pile_quality = st.selectbox("Select Quality", pile_qualities, key="pile_quality")

pile_values = {}
for shift in shift_options:
    pile_values[shift] = st.number_input(f"Pile Made (TON) for {selected_pile_quality} - Shift {shift}", step=0.01, key=f"pile_{shift}")

if st.button("Submit Pile Made"):
    df_pile = pd.DataFrame([
        {"FormType": "Pile Made", "Date": str(record_date_pile), "Quality": selected_pile_quality, "Shift": shift, "Pile Made (TON)": val}
        for shift, val in pile_values.items()
    ])
    df_pile.to_csv("batching_pile_records.csv", mode="a", index=False, header=False)

    # Push each record to MongoDB
    for _, row in df_pile.iterrows():
        status = post_to_sap_batching(row.to_dict())

    if status == "success":
        st.success("✅ Pile Made data saved & pushed successfully!")
    else:
        st.warning("⚠️ MongoDB push failed — check connection.")

    st.dataframe(df_pile)

# =====================================================
# 3️⃣ ROLL MADE FORM
# =====================================================
st.header("3️⃣ Roll Made (EA)")
roll_qualities = ["P", "O", "T", "J", "B"]
record_date_roll = st.date_input("Select Date (Roll Made)", value=today, min_value=min_date, max_value=today, key="roll_date")
selected_roll_quality = st.selectbox("Select Quality", roll_qualities, key="roll_quality")

roll_values = {}
for shift in shift_options:
    roll_values[shift] = st.number_input(f"Roll Made (EA) for {selected_roll_quality} - Shift {shift}", step=1, key=f"roll_{shift}")

if st.button("Submit Roll Made"):
    df_roll = pd.DataFrame([
        {"FormType": "Roll Made", "Date": str(record_date_roll), "Quality": selected_roll_quality, "Shift": shift, "Roll Made (EA)": val}
        for shift, val in roll_values.items()
    ])
    df_roll.to_csv("batching_roll_records.csv", mode="a", index=False, header=False)

    for _, row in df_roll.iterrows():
        status = post_to_sap_batching(row.to_dict())

    if status == "success":
        st.success("✅ Roll Made data saved & pushed successfully!")
    else:
        st.warning("⚠️ MongoDB push failed — check connection.")

    st.dataframe(df_roll)

# =====================================================
# 4️⃣ ROPES & HABIJABI + CUTTING FORM
# =====================================================
st.header("4️⃣ Ropes & Habijabi and Cutting")
record_date_extra = st.date_input("Select Date (Ropes & Cutting)", value=today, min_value=min_date, max_value=today, key="extra_date")

ropes_value = st.number_input("Approx Production for Ropes & Habijabi (m)", step=0.1, key="ropes_value")
cutting_value = st.number_input("Approx Production for Cutting (m)", step=0.1, key="cutting_value")

if st.button("Submit Ropes & Cutting"):
    record = {
        "FormType": "Ropes & Cutting",
        "Date": str(record_date_extra),
        "Ropes & Habijabi (m)": ropes_value,
        "Cutting (m)": cutting_value
    }

    df = pd.DataFrame([record])
    df.to_csv("batching_extra_records.csv", mode="a", index=False, header=False)

    status = post_to_sap_batching(record)
    if status == "success":
        st.success("✅ Ropes & Cutting record saved & pushed to MongoDB!")
    else:
        st.warning("⚠️ Saved locally, but push failed.")

    st.dataframe(df)

# =====================================================
st.markdown("---")
st.caption("Developed for Batching Department — Digitization via Streamlit + Flask + MongoDB Integration")
