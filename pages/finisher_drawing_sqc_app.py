import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api_clients.api_client_finsqc import post_to_sap_finsqc  # your existing client

# ----------------------- Config -----------------------
st.set_page_config(page_title="Finisher Drawing SQC Report", layout="centered")
st.title("📘 Finisher Drawing — SQC Report")

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

K_CONST = 1.0582  # Actual = K * Sliver Wt

# factor per quality for Converted calculation
FACTOR_120 = {"Sacking Warp", "Sacking Weft", "Special Sacking Warp"}
FACTOR_116 = {"Hessian", "S4 Weft"}

def converted_factor(quality: str) -> float:
    return 120.0 if quality in FACTOR_120 else 116.0

def calc_actual(sliver_wt: float) -> float:
    return K_CONST * sliver_wt

def calc_converted(actual: float, mr: float, factor: float) -> float:
    denom = mr + 100.0
    return (actual * factor) / denom if denom > 0 else 0.0

# ------------------- Basic Information -------------------
today = date.today()
min_date = today - timedelta(days=5)

st.subheader("1️⃣ Basic Information")
record_date = st.date_input("Date", value=today, min_value=min_date, max_value=today)

quality = st.selectbox(
    "Quality",
    ["Special Sacking Warp", "Hessian", "Sacking Warp", "Sacking Weft", "S4 Weft"]
)

machine_no = st.number_input("Machine No.", min_value=1, step=1)

st.markdown("---")

# ------------------- Three Readings -------------------
st.subheader("2️⃣ Enter 3 Readings (Sliver Weight & MR%)")

def reading(idx: int):
    c1, c2 = st.columns(2)
    with c1:
        w = st.number_input(f"Reading {idx} — Sliver Weight (gm)", min_value=0.0, step=0.1, key=f"w{idx}")
    with c2:
        mr = st.number_input(f"Reading {idx} — MR% (0–50)", min_value=0.0, max_value=50.0, step=0.1, key=f"mr{idx}")
    return w, mr

w1, mr1 = reading(1)
w2, mr2 = reading(2)
w3, mr3 = reading(3)

factor = converted_factor(quality)

# live calcs
a1, a2, a3 = calc_actual(w1), calc_actual(w2), calc_actual(w3)
c1, c2, c3 = (
    calc_converted(a1, mr1, factor),
    calc_converted(a2, mr2, factor),
    calc_converted(a3, mr3, factor),
)

readings_df = pd.DataFrame({
    "Reading": [1, 2, 3],
    "Sliver Wt (gm)": [w1, w2, w3],
    "MR%": [mr1, mr2, mr3],
    "Actual": [round(a1, 4), round(a2, 4), round(a3, 4)],
    "Converted": [round(c1, 4), round(c2, 4), round(c3, 4)],
})

valid = [v for v in [c1, c2, c3] if v > 0]
avg_converted = round(sum(valid) / len(valid), 4) if valid else 0.0

st.write("### Live Calculations")
st.dataframe(readings_df, use_container_width=True)
st.metric("Machine Average (Converted)", f"{avg_converted:.4f}")
st.caption(f"Formula: Actual = 1.0582 × Sliver Wt | Converted = Actual × {int(factor)} / (MR + 100)")

st.markdown("---")

# ------------------- Submit -------------------
st.subheader("3️⃣ Submit")

if st.button("Save SQC Record"):
    errors = []
    for i, (w, mr) in enumerate([(w1, mr1), (w2, mr2), (w3, mr3)], start=1):
        if w <= 0: errors.append(f"Reading {i}: Sliver Weight must be > 0")
        if not (0.0 <= mr <= 50.0): errors.append(f"Reading {i}: MR% must be 0–50")
    if machine_no <= 0: errors.append("Machine No. must be > 0")

    if errors:
        for e in errors: st.error("⚠️ " + e)
        st.stop()

    record = {
        "Date": str(record_date),
        "Quality": quality,
        "FactorUsed": int(factor),
        "Machine No.": int(machine_no),

        "W1 (gm)": w1, "MR1 (%)": mr1, "Actual1": round(a1, 4), "Converted1": round(c1, 4),
        "W2 (gm)": w2, "MR2 (%)": mr2, "Actual2": round(a2, 4), "Converted2": round(c2, 4),
        "W3 (gm)": w3, "MR3 (%)": mr3, "Actual3": round(a3, 4), "Converted3": round(c3, 4),

        "Average Converted": avg_converted,
    }

    df_out = pd.DataFrame([record])

    # local csv
    csv_name = "finisher_drawing_sqc_records.csv"
    try:
        existing = pd.read_csv(csv_name)
        updated = pd.concat([existing, df_out], ignore_index=True)
        updated.to_csv(csv_name, index=False)
    except FileNotFoundError:
        df_out.to_csv(csv_name, index=False)

    # push to mock server
    ok, resp = post_to_sap_finsqc(record)
    if ok:
        st.success("✅ Record saved AND synced to Mock SAP Server.")
    else:
        st.warning(f"⚠️ Saved locally. Sync failed: {resp}")

    st.dataframe(df_out, use_container_width=True)
