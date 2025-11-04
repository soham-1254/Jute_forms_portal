import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_morahweight import post_to_sap_morahweight  # 🔗 Flask + MongoDB integration

# =====================================================
# 🧾 PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Morah Weight Entry", layout="centered")
st.title("🧺 Morah Weight Entry Form")

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
# 1️⃣ BASIC INFORMATION
# =====================================================
today = date.today()
min_date = today - timedelta(days=5)

record_date = st.date_input("📅 Select Date", value=today, min_value=min_date, max_value=today)
godown_no = st.text_input("🏠 Godown No.", placeholder="e.g., R3, F2")
quality = st.text_input("🎯 Quality", placeholder="e.g., P, T, SB, etc.")
worker_name = st.text_input("👷 Worker Name", placeholder="e.g., Bijoy, Ranjit, Subhas")

# =====================================================
# 2️⃣ MORAHS ENTRY SECTION
# =====================================================
st.subheader("⚖️ Morah Weights (in grams)")

num_morahs = st.number_input("Enter number of Morahs for this Quality", min_value=1, step=1)
morah_weights = []

for i in range(int(num_morahs)):
    val = st.number_input(f"Morah {i+1} Weight (gm)", min_value=0.0, step=1.0, key=f"morah_{i}")
    morah_weights.append(val)

if any(w <= 0 for w in morah_weights):
    st.warning("⚠️ All Morah weights must be greater than 0.")

# =====================================================
# 3️⃣ CALCULATE AVERAGE
# =====================================================
avg_weight = 0.0
if all(w > 0 for w in morah_weights):
    avg_weight = round(sum(morah_weights) / len(morah_weights), 2)

st.markdown(f"### 📊 Average Morah Weight: **{avg_weight} gm**")

# =====================================================
# 4️⃣ SUBMIT BUTTON
# =====================================================
if st.button("Submit Morah Weight Record", use_container_width=True):
    if not godown_no.strip() or not quality.strip() or not worker_name.strip():
        st.error("⚠️ Godown No., Quality, and Worker Name cannot be empty.")
    elif any(w <= 0 for w in morah_weights):
        st.error("⚠️ All Morah weights must be greater than 0.")
    else:
        record = {
            "Date": str(record_date),
            "Godown No.": godown_no.strip(),
            "Quality": quality.strip(),
            "Worker Name": worker_name.strip(),
            "Morah Weights (gm)": morah_weights,
            "Average Weight (gm)": avg_weight,
            "status": "Pending",
        }

        # Save to CSV
        csv_name = "morah_weight_records.csv"
        try:
            existing = pd.read_csv(csv_name)
            updated = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        except FileNotFoundError:
            updated = pd.DataFrame([record])
        updated.to_csv(csv_name, index=False)

        # Sync to Mock SAP Server
        ok, resp = post_to_sap_morahweight(record)
        if ok:
            st.success("✅ Record saved and synced with Mock SAP Server.")
        else:
            st.warning(f"⚠️ Saved locally — could not sync: {resp}")

        st.dataframe(pd.DataFrame([record]), use_container_width=True)

# =====================================================
# 5️⃣ SUMMARY VIEW
# =====================================================
st.markdown("---")
st.subheader("📅 Daily Summary")

try:
    df = pd.read_csv("morah_weight_records.csv")
    df_today = df[df["Date"] == str(record_date)]

    if not df_today.empty:
        grouped = df_today.groupby("Quality")["Average Weight (gm)"].mean().reset_index()
        grouped.rename(columns={"Average Weight (gm)": "Avg Weight (gm) by Quality"}, inplace=True)

        st.dataframe(df_today, use_container_width=True)
        st.markdown("### 📈 Quality-wise Average Morah Weights")
        st.dataframe(grouped, use_container_width=True)
    else:
        st.info("No records for the selected date yet.")
except FileNotFoundError:
    st.info("No records found yet.")

st.markdown("---")
st.caption("Developed for Raw Jute Department — Morah Weight Register")
