import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_cardingrepinning import post_to_sap_cardingrepinning  # 🔗 MongoDB integration

# =====================================================
# 🧾 PAGE CONFIGURATION
# =====================================================
st.set_page_config(page_title="Carding Repinning Report", layout="centered")
st.title("🧰 Carding Department — Repinning Report")

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
record_date = st.date_input(
    "Select Date",
    value=today,
    min_value=min_date,
    max_value=today
)

labour_name = st.text_input("Labour Name (e.g., Haidar, Abinunu, Jamil)")

# =====================================================
# 2️⃣ MACHINE ENTRIES SECTION
# =====================================================
st.subheader("2️⃣ Machine Parts & Details")

num_entries = st.number_input(
    "Job Done",
    min_value=1,
    max_value=20,
    step=1
)

entries = []
for i in range(int(num_entries)):
    st.markdown(f"### 🔹 Entry #{i+1}")
    col1, col2 = st.columns(2)
    with col1:
        part_name = st.text_input(f"Machine Part Name (e.g., Cylinder, Worker, Feed Roller)", key=f"part_{i}")
        dimensions = st.text_input(f"Dimensions (Length × Width)", key=f"dim_{i}")
    with col2:
        quantity = st.number_input(f"Quantity (Pcs)", min_value=0, step=1, key=f"qty_{i}")
        machine_type = st.text_input(f"Machine Type (e.g., B/C, T/C)", key=f"type_{i}")
        machine_no = st.number_input(f"Machine Number", min_value=0, step=1, key=f"no_{i}")

    # Validation prompt (only after input)
    if quantity == 0:
        st.warning(f"⚠️ Entry #{i+1}: Quantity cannot be 0.")

    entries.append({
        "Machine Part": part_name,
        "Dimensions": dimensions,
        "Quantity (pcs)": quantity,
        "Machine Type": machine_type,
        "Machine Number": machine_no
    })

# =====================================================
# 3️⃣ SUBMIT SECTION
# =====================================================
if st.button("📤 Submit Repinning Record"):
    invalid_entries = [e for e in entries if e["Quantity (pcs)"] <= 0 or not e["Machine Part"]]

    if not labour_name.strip():
        st.error("❌ Labour name cannot be empty.")
    elif invalid_entries:
        st.error("🚫 Some entries are invalid. Please ensure all quantities > 0 and part names filled.")
    else:
        df = pd.DataFrame(entries)
        df["Date"] = record_date
        df["Labour Name"] = labour_name

        # Save locally
        try:
            existing = pd.read_csv("carding_repinnning_records.csv")
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_csv("carding_repinnning_records.csv", index=False)
        except FileNotFoundError:
            df.to_csv("carding_repinnning_records.csv", index=False)

        # Send to Flask + MongoDB
        record = {
            "Date": str(record_date),
            "Labour Name": labour_name,
            "Entries": entries
        }

        status = post_to_sap_cardingrepinning(record)
        if status == "success":
            st.success("✅ Repinning Report submitted and stored in MongoDB successfully!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check connection or server log.")

        st.dataframe(df)

st.markdown("---")
st.caption("Developed for Carding Department — Streamlit + Flask + MongoDB Integration")
