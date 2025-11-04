import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_bundle_strength import post_to_sap_bundle_strength  # 🔗 MongoDB integration

# =====================================================
# 🧾 PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Raw Jute Bundle Strength", layout="centered")
st.title("🧵 RAW JUTE BUNDLE STRENGTH REPORT (Gm/Tex)")

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
record_date = st.date_input("Select Date", value=today, min_value=min_date, max_value=today)

quality = st.text_input("Quality (e.g., SEMI NORTHEN)")
mokam = st.text_input("Mokam (e.g., RAMGANJ)")
marka = st.text_input("Marka (e.g., KALI)")
sample_from = st.text_input("Sample Taken From (e.g., R1)")
sample_length = st.number_input("Sample Test Length (cm)", min_value=0.0, step=0.1)

# =====================================================
# 2️⃣ MEASUREMENTS ENTRY
# =====================================================
st.subheader("2️⃣ Bundle Weight & Tenacity (Top / Middle / Bottom)")

sections = ["Top", "Middle", "Bottom"]
bundle_records = {}

for section in sections:
    st.markdown(f"### 🔹 {section} Section")
    num_samples = st.number_input(
        f"Number of samples for {section}", min_value=1, max_value=10, step=1, key=f"samples_{section}"
    )

    data = []
    for i in range(int(num_samples)):
        col1, col2 = st.columns(2)
        with col1:
            wt = st.number_input(f"Bundle Weight (mg) #{i+1} ({section})", min_value=0.0, step=0.1, key=f"wt_{section}_{i}")
        with col2:
            tenacity = st.number_input(f"Tenacity (Gm/Tex) #{i+1} ({section})", min_value=0.0, step=0.1, key=f"tenacity_{section}_{i}")

        if wt == 0 or tenacity == 0:
            st.warning(f"⚠️ Row {i+1} in {section} section has empty or invalid data.")
        data.append({"Bundle Wt (mg)": wt, "Tenacity (Gm/Tex)": tenacity})

    df_section = pd.DataFrame(data)
    if not df_section.empty:
        df_section["Section"] = section
        bundle_records[section] = df_section

# =====================================================
# 3️⃣ CALCULATE AVERAGES (Top / Middle / Bottom / Grand)
# =====================================================
st.subheader("3️⃣ Summary Statistics")

summary = []
grand_tenacity_list = []

for section, df in bundle_records.items():
    if not df.empty:
        avg_tenacity = df["Tenacity (Gm/Tex)"].mean()
        sd = df["Tenacity (Gm/Tex)"].std()
        cv = (sd / avg_tenacity * 100) if avg_tenacity > 0 else 0
        summary.append({
            "Section": section,
            "Avg Tenacity (Gm/Tex)": round(avg_tenacity, 2),
            "SD": round(sd, 2),
            "CV%": round(cv, 2)
        })
        grand_tenacity_list.extend(df["Tenacity (Gm/Tex)"].tolist())

summary_df = pd.DataFrame(summary)

if not summary_df.empty:
    grand_avg = round(pd.Series(grand_tenacity_list).mean(), 2)
    grand_cv = round(pd.Series(grand_tenacity_list).std() / grand_avg * 100, 2)
    st.dataframe(summary_df, use_container_width=True)
    st.success(f"🏁 Grand Average Tenacity: {grand_avg} Gm/Tex | Grand CV%: {grand_cv}")

# =====================================================
# 4️⃣ SUBMISSION
# =====================================================
if st.button("📤 Submit Bundle Strength Report"):
    if not summary_df.empty:
        record = {
            "Date": str(record_date),
            "Quality": quality,
            "Mokam": mokam,
            "Marka": marka,
            "Sample From": sample_from,
            "Sample Test Length (cm)": sample_length,
            "Summary": summary_df.to_dict(orient="records"),
            "Grand Average (Gm/Tex)": grand_avg,
            "Grand CV%": grand_cv
        }

        # --- Save locally as backup
        df_all = pd.concat(bundle_records.values(), ignore_index=True)
        df_all.to_csv("bundle_strength_records.csv", index=False)

        # --- Push to Mock Server
        status = post_to_sap_bundle_strength(record)
        if status == "success":
            st.success("✅ Report submitted successfully and stored in MongoDB!")
        else:
            st.warning("⚠️ Saved locally. MongoDB push failed — check server log.")
    else:
        st.error("❌ No valid data found! Please fill in at least one section with proper values.")

st.markdown("---")
st.caption("Developed for Raw Jute Lab — Streamlit + MongoDB Integration")
