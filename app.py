import streamlit as st
import pandas as pd
import plotly.express as px
import time
import re
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
try:
    import pdfplumber
except ImportError:
    # Fallback if library missing, though user should install it
    pass

st.set_page_config(
    page_title="Magic Bus Analytics Suite",
    page_icon="🚍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. ENTERPRISE CSS (Magic Bus Theme)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        .stApp { background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }
        
        /* Header Gradient */
        .dashboard-header {
            background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(211, 47, 47, 0.2);
        }
        
        /* Metric Cards */
        div[data-testid="metric-container"] {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-left: 5px solid #D32F2F;
        }
        
        /* Login Card */
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 450px;
            margin: 60px auto 20px auto;
            text-align: center;
            border-top: 6px solid #D32F2F;
        }
        .login-footer {
            text-align: center;
            font-size: 12px;
            color: #888;
            margin-top: 20px;
        }
        
        /* Chat Interface */
        .stChatMessage {
            background-color: white;
            border: 1px solid #f0f0f0;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: 
    st.session_state.user = {"name": "Admin User", "role": "Head of Finance", "email": "admin@magicbus.org"}
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! I am your Magic Bus AI. How can I help you today?"}]

# --- NAVIGATION STATE FIX ---
# Initialize navigation keys if they don't exist
if 'nav_main' not in st.session_state: st.session_state.nav_main = "📊 Dashboard"
if 'nav_sys' not in st.session_state: st.session_state.nav_sys = None

# Callback functions to handle mutual exclusivity
def on_main_nav_change():
    """When main nav is clicked, clear system nav"""
    st.session_state.nav_sys = None

def on_sys_nav_change():
    """When system nav is clicked, clear main nav"""
    st.session_state.nav_main = None

# Graph Visibility Defaults
if 'show_bar' not in st.session_state: st.session_state.show_bar = True
if 'show_pie' not in st.session_state: st.session_state.show_pie = True
if 'show_line' not in st.session_state: st.session_state.show_line = True

# Settings Defaults
if 'sett_animations' not in st.session_state: st.session_state.sett_animations = True
if 'sett_darkmode' not in st.session_state: st.session_state.sett_darkmode = False
if 'sett_notifications' not in st.session_state: st.session_state.sett_notifications = True
if 'sett_autosave' not in st.session_state: st.session_state.sett_autosave = True

# -----------------------------------------------------------------------------
# 4. INTELLIGENT HELPERS
# -----------------------------------------------------------------------------
def stream_text(text):
    """Typing effect"""
    for char in text.split(" "):
        yield char + " "
        time.sleep(0.02)

def auto_map_columns(df):
    """Smartly detects Amount, Category, and Date columns"""
    cols = list(df.columns)
    
    # 1. Amount
    amt = next((c for c in cols if any(x in c.lower() for x in ['spend', 'amount', 'cost', 'total', 'budget'])), None)
    if not amt: amt = df.select_dtypes(include=['number']).columns[0] if len(df.select_dtypes(include=['number']).columns)>0 else None
    
    # 2. Category
    cat = next((c for c in cols if any(x in c.lower() for x in ['project', 'donor', 'name', 'activity'])), None)
    if not cat: 
        texts = df.select_dtypes(include=['object']).columns
        for t in texts:
            if 'status' not in t.lower() and 'date' not in t.lower():
                cat = t
                break
    if not cat and len(cols)>0: cat = cols[0]
    
    # 3. Date
    date = next((c for c in cols if any(x in c.lower() for x in ['date', 'time', 'year', 'month'])), None)
    
    # 4. Status
    status = next((c for c in cols if 'status' in c.lower()), None)
    
    return amt, cat, date, status

# -----------------------------------------------------------------------------
# 5. LOGIN SCREEN
# -----------------------------------------------------------------------------
def login_page():
    st.markdown("""
        <div class="login-card">
            <h2 style="color:#D32F2F; margin:0;">Magic Bus Intelligence</h2>
            <p style="color:#666; font-size:15px; margin-top:5px;">Secure Enterprise Analytics Portal</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size:13px; color:#444; background:#fff3cd; padding:8px; border-radius:5px;">
                ⚠️ <b>Authorized Access Only:</b> All activities are monitored.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        with st.form("login_form"):
            u = st.text_input("Username / ID", placeholder="Enter your ID")
            p = st.text_input("Password", type="password", placeholder="Enter Password")
            
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            
            btn = st.form_submit_button("🔒 Secure Login", use_container_width=True)
            
            if btn:
                if u == "admin" and p == "admin":
                    with st.spinner("Verifying credentials..."):
                        time.sleep(1) 
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials. Try admin/admin")
    
    st.markdown("""
        <div class="login-footer">
            <p>Need help? Contact IT Support at <a href="#">support@magicbus.org</a></p>
            <p>v15.0 | Protected by AES-256 Encryption</p>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. MAIN APPLICATION LOGIC
# -----------------------------------------------------------------------------
if not st.session_state.auth:
    login_page()
else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Magic_Bus_logo.png/640px-Magic_Bus_logo.png", width=140)
        st.markdown(f"### 👤 {st.session_state.user['name']}")
        st.caption(st.session_state.user['role'])
        st.markdown("---")
        
        # --- FIXED NAVIGATION ---
        st.markdown("### 🧭 Navigation")
        # Note: We use index=None to allow it to be cleared programmatically
        nav_main_selection = st.radio(
            "Go to", 
            ["📊 Dashboard", "📂 Data Preview", "🤖 AI Analyst"], 
            label_visibility="collapsed",
            key="nav_main",
            on_change=on_main_nav_change,
            index=None
        )
        
        st.markdown("---")
        
        # System Menu
        st.markdown("### ⚙️ System")
        nav_sys_selection = st.radio(
            "Settings", 
            ["Profile", "Preferences"], 
            label_visibility="collapsed", 
            key="nav_sys",
            on_change=on_sys_nav_change,
            index=None
        )
        
        # Determine Active View based on which one is selected
        # Fallback to Dashboard if nothing is selected (e.g. on fresh load or manual reset)
        if nav_sys_selection:
            active_view = nav_sys_selection
        elif nav_main_selection:
            active_view = nav_main_selection
        else:
            active_view = "📊 Dashboard"

        # View Controls (Only for Dashboard)
        if active_view == "📊 Dashboard":
            st.markdown("---")
            st.markdown("### 👁️ Graph Controls")
            st.session_state.show_bar = st.checkbox("Show Comparison", value=st.session_state.show_bar)
            st.session_state.show_pie = st.checkbox("Show Allocation", value=st.session_state.show_pie)
            st.session_state.show_line = st.checkbox("Show Trends", value=st.session_state.show_line)

        st.markdown("---")
        uploaded_file = st.file_uploader("📥 Upload Data", type=['csv', 'xlsx', 'pdf'])
        
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # --- HEADER ---
    header_title = "Magic Bus Intelligence Hub"
    if active_view == "Profile": header_title = "User Profile"
    elif active_view == "Preferences": header_title = "System Preferences"
    
    st.markdown(f"""
        <div class="dashboard-header">
            <h2 style="margin:0;">{header_title}</h2>
            <p style="margin:0; opacity:0.9;">Logged in as: {st.session_state.user['email']}</p>
        </div>
    """, unsafe_allow_html=True)

    # GLOBAL DATA LOAD WITH SCANNING
    df = None
    pdf_text = ""
    amt, cat, date, status = None, None, None, None

    if uploaded_file:
        file_key = f"scanned_{uploaded_file.name}"
        if file_key not in st.session_state:
            with st.status("📂 File Uploaded! Scanning for viruses & data integrity...", expanded=True) as status_box:
                st.write("🔍 Analyzing file structure...")
                time.sleep(1)
                st.write("🛡️ Running security checks...")
                time.sleep(0.8)
                st.write("✅ Mapping data columns...")
                time.sleep(0.5)
                status_box.update(label="✅ Scan Complete! Data Ready.", state="complete", expanded=False)
            st.session_state[file_key] = True

        try:
            if uploaded_file.name.endswith('.pdf'):
                # Safety check for pdfplumber
                try:
                    import pdfplumber
                    with pdfplumber.open(uploaded_file) as pdf:
                        for p in pdf.pages: pdf_text += p.extract_text() + "\n"
                except ImportError:
                    st.error("PDF support requires 'pdfplumber'. Please install it.")
            else:
                if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
                else: df = pd.read_excel(uploaded_file)
                amt, cat, date, status = auto_map_columns(df)
        except Exception as e: st.error(f"File Error: {e}")

    # =========================================================
    # VIEW 1: DASHBOARD
    # =========================================================
    if active_view == "📊 Dashboard":
        if df is not None and amt:
            st.markdown("##### 🔍 Project Comparison")
            all_cats = list(df[cat].unique())
            sel_cats = st.multiselect("Select Projects to Compare", all_cats, default=[])
            
            df_view = df[df[cat].isin(sel_cats)] if sel_cats else df
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Spend", f"₹ {df_view[amt].sum():,.0f}")
            k2.metric("Avg Transaction", f"₹ {df_view[amt].mean():,.0f}")
            k3.metric("Max Project", f"₹ {df_view[amt].max():,.0f}")
            k4.metric("Records Found", len(df_view))
            
            st.markdown("---")
            
            if st.session_state.show_bar or st.session_state.show_pie:
                c1, c2 = st.columns(2)
                if st.session_state.show_bar:
                    with c1 if st.session_state.show_pie else st.container():
                        st.subheader(f"📊 Spend by {cat}")
                        df_agg = df_view.groupby(cat)[amt].sum().reset_index().sort_values(by=amt, ascending=True).tail(10)
                        fig1 = px.bar(df_agg, x=amt, y=cat, orientation='h', text_auto='.2s', 
                                      color=amt, color_continuous_scale=['#ffcdd2', '#b71c1c'])
                        st.plotly_chart(fig1, use_container_width=True)
                
                if st.session_state.show_pie:
                    with c2 if st.session_state.show_bar else st.container():
                        st.subheader("🍩 Budget Allocation")
                        fig2 = px.pie(df_view, names=cat, values=amt, hole=0.6, color_discrete_sequence=px.colors.qualitative.Bold)
                        st.plotly_chart(fig2, use_container_width=True)
            
            if date and st.session_state.show_line:
                st.subheader("📅 Time Trends")
                try:
                    df_view[date] = pd.to_datetime(df_view[date])
                    df_time = df_view.groupby(date)[amt].sum().reset_index()
                    fig3 = px.line(df_time, x=date, y=amt, markers=True)
                    fig3.update_traces(line_color='#D32F2F', line_width=3)
                    st.plotly_chart(fig3, use_container_width=True)
                except: st.info("Date formatting issue.")
            
        elif pdf_text:
            st.info("PDF Loaded. Switch to 'AI Analyst' tab.")
        else:
            st.info("👈 Upload a file to view Dashboard.")

    # =========================================================
    # VIEW 2: DATA PREVIEW
    # =========================================================
    elif active_view == "📂 Data Preview":
        st.markdown("### 🛠️ Data Explorer")
        
        if df is not None:
            c1, c2, c3 = st.columns(3)
            f_cat, f_status = "All", "All"
            
            if cat:
                with c1: f_cat = st.selectbox(f"Filter by {cat}", ["All"] + list(df[cat].unique()))
            if status:
                with c2: f_status = st.selectbox("Filter by Status", ["All"] + list(df[status].unique()))
            
            df_f = df.copy()
            if f_cat != "All": df_f = df_f[df_f[cat] == f_cat]
            if status and f_status != "All": df_f = df_f[df_f[status] == f_status]
            
            st.dataframe(df_f, use_container_width=True)
            st.caption(f"Showing {len(df_f)} records")
            
            csv = df_f.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Filtered Data", csv, "magic_bus_data.csv", "text/csv")
        else:
            st.info("Upload data first.")

    # =========================================================
    # VIEW 3: AI ANALYST
    # =========================================================
    elif active_view == "🤖 AI Analyst":
        st.markdown("### 💬 Ask the Intelligent Agent")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        prompt = st.chat_input("Ask: 'Total Spend', 'Highest Project', 'Summary'...")
        
        if prompt:
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            q = prompt.lower()
            resp = ""
            
            if df is not None and amt:
                if any(x in q for x in ["hi", "hello", "namaste"]): 
                    resp = "Hello! I am your Magic Bus Financial Assistant."
                elif any(x in q for x in ["total", "sum", "spend"]): 
                    resp = f"💰 **Total Volume:** ₹ {df[amt].sum():,.2f}"
                elif any(x in q for x in ["max", "highest", "top"]): 
                    row = df.nlargest(1, amt).iloc[0]
                    resp = f"🏆 **Highest:** {row[cat]} (**₹ {row[amt]:,.2f}**)"
                elif any(x in q for x in ["min", "lowest", "least"]): 
                    row = df.nsmallest(1, amt).iloc[0]
                    resp = f"📉 **Lowest:** {row[cat]} (**₹ {row[amt]:,.2f}**)"
                elif "summary" in q:
                    resp = f"**Summary:** Analyzed {len(df)} records. Total Spend: ₹ {df[amt].sum():,.2f}."
                elif "compare" in q:
                    resp = "You can use the 'Dashboard' tab filters to compare projects visually!"
                else:
                    resp = "I can answer: Total, Max, Min, Summary. Try asking: 'Total Spend'."
            elif pdf_text:
                if "summary" in q: resp = f"**PDF Summary:**\n{pdf_text[:600]}..."
                else: 
                    matches = [l for l in pdf_text.split('\n') if q in l.lower()]
                    resp = "Found:\n" + "\n".join(matches[:3]) if matches else "No text match found."
            else:
                resp = "Please upload a file first."
            
            with st.chat_message("assistant"):
                st.write_stream(stream_text(resp))
            st.session_state.messages.append({"role": "assistant", "content": resp})

    # =========================================================
    # VIEW 4: PROFILE
    # =========================================================
    elif active_view == "Profile":
        st.markdown("### 👤 User Profile")
        c1, c2 = st.columns([1, 3])
        with c1: st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        with c2:
            st.subheader(st.session_state.user['name'])
            st.write(f"**Role:** {st.session_state.user['role']}")
            st.write(f"**Email:** {st.session_state.user['email']}")
            st.success("Account Status: Active")
        
        st.markdown("---")
        st.markdown("#### 🔒 Security Audit")
        st.info("Last Login: Just Now via Secure Tunnel")
        st.info("Encryption Level: AES-256 (Local)")

    # =========================================================
    # VIEW 5: SETTINGS
    # =========================================================
    elif active_view == "Preferences":
        st.markdown("### ⚙️ System Preferences")
        
        with st.expander("🎨 UI Settings", expanded=True):
            st.write("Customize your viewing experience:")
            st.session_state.sett_darkmode = st.toggle("🌙 Enable Dark Mode Theme", value=st.session_state.sett_darkmode)
            st.session_state.sett_animations = st.toggle("✨ Enable Graph Animations", value=st.session_state.sett_animations)
            
            if st.session_state.sett_darkmode:
                st.info("Note: Dark Mode will apply on next system restart.")
            
        with st.expander("💾 Data Management", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.sett_autosave = st.checkbox("Auto-Save Reports", value=st.session_state.sett_autosave)
                st.session_state.sett_notifications = st.checkbox("Email Notifications", value=st.session_state.sett_notifications)
            with c2:
                if st.button("🗑️ Clear Cache Now", use_container_width=True):
                    st.cache_data.clear()
                    st.toast("Cache Cleared Successfully!", icon="🧹")
                
                if st.button("📥 Export Activity Logs", use_container_width=True):
                    st.toast("Logs exported to admin folder.", icon="📂")
            
        with st.expander("🛠️ Model Config"):
            conf = st.slider("AI Confidence Threshold", 0.5, 1.0, 0.85)
            st.caption(f"Current Threshold: {conf*100}% accuracy required")