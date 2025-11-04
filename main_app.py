import streamlit as st
from session_manager import init_session, login_user, logout_user, check_timeout
import pandas as pd
import os

# ======================================================
# ⚙️ PAGE CONFIGURATION
# ======================================================
st.set_page_config(page_title="Mill Digital Portal", layout="wide")
init_session()
check_timeout()

# Hide sidebar navigation
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ======================================================
# 👤 USER CREDENTIALS (TEMP DEMO)
# ======================================================
USERS = {
    "admin": {"password": "stil@admin", "role": "Admin"},
    "manager": {"password": "stil@manager123", "role": "Manager"},
    "user": {"password": "stil@user", "role": "User"},
}


def login_page():
    st.markdown(
        """
        <style>
        /* page background */
        .stApp {
            background-color: #000000 !important;
        }

        .login-container {
            background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            width: 420px;
            margin: 3rem auto;
            text-align: center;
        }
        .login-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            color: #1e3a8a;
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }
        .login-sub {
            color: #4b5561;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }

        /* 🔆 darker inputs (not transparent, not too bright) */
        .stTextInput label {
            color: #ffffff !important;               /* keep label bright on dark bg */
            font-weight: 600 !important;
        }
        .stTextInput input {
            background-color: rgba(15, 23, 42, 0.65) !important;  /* dark slate */
            color: #ffffff !important;               /* typed text white */
            border: 1px solid #475569 !important;     /* subtle border */
            border-radius: 8px !important;
        }
        .stTextInput input::placeholder {
            color: #cbd5f5 !important;                /* light but not white */
        }

        /* login button */
        div.stButton > button {
            background-color: #007bff !important;
            color: #ffffff !important;
            border: none;
            width: 100% !important;
            padding: 0.9rem 0 !important;
            font-size: 1rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        div.stButton > button:hover {
            background-color: #0056b3 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='login-container'>
            <div class='login-header'>
                🔐 Mill Digital Entry Portal
            </div>
            <div class='login-sub'>
                Secure access to departmental digital forms
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # inputs (now darker)
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password")

    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.button("Login", use_container_width=True, key="login_btn"):
            user = USERS.get(username)
            if user and user["password"] == password:
                login_user(username, user["role"])
                st.session_state["role"] = user["role"]
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try again.")




# ======================================================
# 🏠 HOMEPAGE (Stylized Dashboard)
# ======================================================
def homepage():
    # Sidebar user info
    st.sidebar.markdown(
        f"""
        <div style="padding:15px; background:linear-gradient(135deg,#3b82f6,#60a5fa);
        border-radius:10px; color:white; text-align:center;">
            👋 <b>{st.session_state.user}</b><br>
            <span style="font-size:14px;">({st.session_state.role})</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.button("🚪 Logout", on_click=logout_user, key="logout_btn")

    # Dashboard Title
    st.markdown(
        """
        <div style="
            background:linear-gradient(135deg,#1e40af,#2563eb);
            padding:20px; border-radius:15px; text-align:center;
            color:white; box-shadow:0 4px 10px rgba(0,0,0,0.25);
        ">
            <h2 style="margin:0;">🏭 Mill Digital Forms Dashboard</h2>
            <p style="font-size:16px; color:#f3f4f6;">
                Manage all department-wise form entries and digital records.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Section Header
    st.markdown(
        """
        <style>
        .section-header {
            background-color: #e0f2fe;
            padding: 10px 15px;
            border-radius: 10px;
            color: #1e3a8a;
            font-weight: 600;
            font-size: 18px;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div class='section-header'>📑 Available Departmental Forms</div>", unsafe_allow_html=True)

    # ==================================================
    # 🧾 Department-wise Form Navigation
    # ==================================================
    if st.session_state.role in ["Admin", "Manager", "User"]:
        st.subheader("📑 Available Departmental Forms")

        # ------------------- RAW JUTE -------------------
        with st.expander("🧵 Raw Jute Department"):
            if st.button("📄 Raw Jute Requirement And Issue Report", key="btn_rjr"):
                st.switch_page("pages/raw_jute_requirement_app.py")
            if st.button("📄 Raw Jute Issue Slip", key="btn_rjis"):
                st.switch_page("pages/raw_jute_issue_app.py")
            if st.button("⚖️ Morah Weight", key="btn_morah"):
                st.switch_page("pages/morah_weight_app.py")

        # ------------------- BATCHING -------------------
        with st.expander("🪢 Batching Department"):
            if st.button("📘 Pile Khata with Roll Stock", key="btn_pilekhata"):
                st.switch_page("pages/roll_stock_availability_app.py")
            if st.button("📘 Entry Khata", key="btn_entrykhata"):
                st.switch_page("pages/batching_entry_khata_app.py")
            if st.button("📗 Log Book", key="btn_batch_log"):
                st.switch_page("pages/maintenance_log_app.py")
            if st.button("📗 Batching History Book", key="btn_batch_history"):
                st.switch_page("pages/history_book_app.py")
            if st.button("🧰 Cleaning and Maintenance (B,C,D)", key="btn_clean_bcd"):
                st.switch_page("pages/cleaning_gauging_app.py")
            if st.button("🧵 Spreader Role Sliver Weight", key="btn_spreader_sliver"):
                st.switch_page("pages/Spreader_app.py")
            if st.button("⚖️ Softener Morah Weight", key="btn_soft_morah"):
                st.switch_page("pages/Softener_morah_app.py")

        # ------------------- CARDING -------------------
        with st.expander("🧶 Carding Department"):
            if st.button("📘 Roll Stock Carding", key="btn_rollstock"):
                st.switch_page("pages/roll_stock_carding_app.py")
            if st.button("📗 Log Book", key="btn_card_log"):
                st.switch_page("pages/maintenance_log_app.py")
            if st.button("📗 Carding History Book", key="btn_carding_history"):
                st.switch_page("pages/history_book_app.py")
            if st.button("🛠️ Repinning Report", key="btn_repinning"):
                st.switch_page("pages/carding_repinning_app.py")
            if st.button("✋ Breaker Card Handfeed", key="btn_handfeed"):
                st.switch_page("pages/breaker_card_handfeed_app.py")
            if st.button("📈 Finisher Card Sliver Weight", key="btn_fsliver"):
                st.switch_page("pages/finisher_card_sliver_app.py")
            if st.button("📉 Breaker Card Rollfeed", key="btn_brollfeed"):
                st.switch_page("pages/breaker_card_rollfeed_app.py")
            if st.button("🔁 Inter Card Roll Feed", key="btn_intercard"):
                st.switch_page("pages/inter_card_rollfeed_app.py")
            if st.button("📊 Finisher Card Roll Feed", key="btn_frollfeed"):
                st.switch_page("pages/finisher_card_rollfeed_app.py")

        # ------------------- DRAWING -------------------
        with st.expander("🧰 Drawing Department"):
            if st.button("📘 Drawing Meter Book", key="btn_drawing_meter"):
                st.switch_page("pages/drawing_meter_book_app.py")
            if st.button("📗 Log Book", key="btn_drawing_log"):
                st.switch_page("pages/maintenance_log_app.py")
            if st.button("📗 Drawing History Book", key="btn_drawing_history"):
                st.switch_page("pages/history_book_app.py")
            if st.button("🧶 Finisher Drawing", key="btn_finisher_draw"):
                st.switch_page("pages/finisher_drawing_sqc_app.py")

        # ------------------- MAINTENANCE -------------------
        with st.expander("🧰 Maintenance Department"):
            if st.button("📗 Log Book", key="btn_maint_log"):
                st.switch_page("pages/maintenance_log_app.py")
            if st.button("⚙️ Front and Back Stop Motion", key="btn_stopmotion"):
                st.switch_page("pages/front_back_stop_motion_app.py")
            if st.button("🚜 Carriage Report", key="btn_carriage"):
                st.switch_page("pages/carriage_report_app.py")
            if st.button("🧽 Cleaning and Maintenance", key="btn_clean_draw"):
                st.switch_page("pages/maintenance_log_app.py")
            if st.button("🔄 Drawing Idle/Revolving/Slicking Report", key="btn_drawing_idle"):
                st.switch_page("pages/revolving_slicking_app.py")

        # ------------------- SPINNING -------------------
        with st.expander("🧵 Spinning Department"):
            if st.button("📈 Winding Production Khata", key="btn_winding_prod"):
                st.switch_page("pages/winding_production_khata_app.py")
            if st.button("📗 Log Book", key="btn_winding_log"):
                st.switch_page("pages/maintenance_log_app.py")
            if st.button("💨 Blow Cleaning", key="btn_blowclean"):
                st.switch_page("pages/cleaning_gauging_app.py")
            if st.button("🧮 Yarn Count", key="btn_yarncount"):
                st.switch_page("pages/yarn_count_report_app.py")

        # ------------------- WINDING -------------------
        with st.expander("🪭 Winding Department"):
            if st.button("🧵 Cop Winding (Weft)", key="btn_copweft"):
                st.switch_page("pages/cop_winding_production_app.py")
            if st.button("🧵 Warp Spool Winding Khata", key="btn_warp_spool"):
                st.switch_page("pages/spool_winding_production_app.py")
            if st.button("📗 Log Book", key="btn_cop_log"):
                st.switch_page("pages/maintenance_log_app.py")

    # ==================================================
    # 👑 ADMIN PANEL (View & Clear Logs)
    # ==================================================
    if st.session_state.role == "Admin":
        st.markdown("---")
        st.subheader("👑 Admin Summary — All Form Records")

        csv_files = [f for f in os.listdir(".") if f.endswith(".csv")]

        if not csv_files:
            st.info("📁 No CSV records found.")
        else:
            for file in csv_files:
                st.markdown(f"#### 📘 {file}")
                df = pd.read_csv(file)
                st.dataframe(df.tail(10), use_container_width=True)

            st.markdown("---")
            st.subheader("🧹 Clear Logs / Reset Data")

            selected_clear_file = st.selectbox("Select a CSV file to clear", csv_files, key="admin_clear_select")

            if st.button("🧾 Clear Selected Log", use_container_width=True, type="primary", key="admin_clear_btn"):
                df = pd.read_csv(selected_clear_file)
                cleared_df = pd.DataFrame(columns=df.columns)
                cleared_df.to_csv(selected_clear_file, index=False)
                st.success(f"✅ Cleared {selected_clear_file} (headers retained).")

            if st.button("🗑️ Clear All CSV Logs", use_container_width=True, key="admin_clear_all"):
                for file in csv_files:
                    df = pd.read_csv(file)
                    cleared_df = pd.DataFrame(columns=df.columns)
                    cleared_df.to_csv(file, index=False)
                st.success("✅ All CSV logs cleared successfully.")

        st.info("⚠️ Only Admins can clear form data logs.")

# ======================================================
# 🚦 PAGE ROUTING
# ======================================================
if not st.session_state.user:
    login_page()
else:
    homepage()
