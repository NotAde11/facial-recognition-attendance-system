import streamlit as st
import backend
import time
from datetime import datetime

# 1. AUTHENTICATION CHECK
if not st.session_state.get("authenticated"):
    st.switch_page("login.py")

# 2. NAVIGATION STATE (Slot this in here)
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"
    
if "cam_index" not in st.session_state:
    st.session_state.cam_index = 0

# Universal function to return to dashboard
def go_back():
    st.session_state.current_page = "main"
    st.rerun()

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #000000 !important;
        }
        [data-testid="stSidebar"] {
            border-right: 2px solid #4A90E2 !important;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
        /* Optional: Match the sidebar background to the main page black */
        [data-testid="stSidebarContent"] {
            background-color: #0D1B2A !important;
        }
        /* Remove the padding at the top of the sidebar */
        [data-testid="stSidebarUserContent"] {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col_logo, col_title, col_user = st.columns([1, 4, 1])

with col_title:
    st.markdown(
        """
        <style>
        .title-text {
            font-family: 'Algerian', 'Stencil', 'Fantasy', serif !important;
            background: linear-gradient(45deg, #4A90E2, #FFFFFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 70px !important;
            font-weight: 700 !important;
            text-align: left; /* Change to 'left' if you want it in the corner */
            white-space: nowrap;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        }
        </style>
        <p class="title-text">PresenceID</p>
        """,
        unsafe_allow_html=True
    )

with col_logo:
    st.image("logo_icon.png", width=120)

with col_user:
    st.markdown("""
    <style>
    .user-text {
        font-size: 17px;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)
    # st.markdown('<div class="user-text">Logged in as:</div>', unsafe_allow_html=True)
    # st.write(st.session_state.get("username", "User"))
    
    username = st.session_state.get("username", "User")

    # Combine the label and the colored username in one line
    st.markdown(f"""
        <div class="user-text">
            Logged in as: <br> <span style="color: #4A90E2;">{username}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 2px solid; border-image: linear-gradient(to right, #0000FF, #00BFFF, #ADD8E6) 1;'>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>Admin Menu</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.8;'>Facial Recognition System</p>", unsafe_allow_html=True)

    if st.button("⚙️ Settings", width="stretch"):
        st.session_state.current_page = "settings"
        st.rerun()
    
    if st.button("📊 View Stats", width="stretch"):
        st.session_state.current_page = "stats"
        st.rerun()
    
    if st.button("Logout", width="stretch"):
        st.session_state.authenticated = False
        st.session_state.current_page = "main"
        st.rerun()

# ---------------- MAIN GRID ----------------

# Style for each button
st.markdown("""
<style>
/* 1. MAIN PAGE BUTTONS - Target buttons NOT in the sidebar */
    [data-testid="stMain"] div.stButton > button[kind="secondary"] {
        width: 100%;
        height: 60px; 
        font-size: 18px;
        border: 2.5px solid #4A90E2;
        border-radius: 10px;
        background-color: transparent;
    }
    
/* Hover effect for Main Buttons */
    [data-testid="stMain"] div.stButton > button:hover {
        background-color: #B3E5FC !important;
        color: black !important;
        border-color: #000000 !important;
        transition: 0.3s;
    }  

/* Hover effect for Logout Button */
    [data-testid="stMain"] div.stButton > button[kind="primary"]:hover {
        background-color: #4A90E2 !important; 
        border-color: #ffffff !important;
        transition: 0.3s;
    }

[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    background-color: transparent;
    color: #ffffff;
    border: 1px solid #F5F5F5; /* Your primary blue */
    border-radius: 8px;        /* Matches the login box feel */
    transition: 0.3s;
}

/* Add that Deep Blue hover we talked about */
[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #1B3A5B !important; 
    border-color: #E1F5FE !important; /* Light blue glow on hover */
}
        
/* 2. TARGET ONLY PRIMARY BUTTONS (Logout) */
    [data-testid="stMain"] div.stButton > button[kind="primary"] {
        background-color: #B3E5FC !important;
        color: #000000 !important;
        border: 2px solid #ffffff;
        border-radius: 10px;
        height: 55px !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.current_page == "main":
    # Row 1
    col1, col2 = st.columns([2, 2])

    with col1:
        if st.button("🎥 Start Recognition", width="stretch"):
            with st.spinner("Initializing Camera..."):
                # Capture the result from the backend function
                result = backend.run_recognition(cam_index=st.session_state.cam_index)
                st.toast(result) # Show the result as a toast notification
                
            msg_placeholder = st.empty()
        
            if "Error" in result:
                msg_placeholder.error(result)
            else:
                msg_placeholder.success(result)
                
            # Wait for 3 seconds, then clear the message
            time.sleep(3)
            msg_placeholder.empty()

    with col2:
        if st.button("📊 View Attendance Table", width="stretch"):
            st.session_state.current_page = "attendance"
            st.rerun()

    st.markdown("<hr style='border: 2px solid; border-image: linear-gradient(to right, #0000FF, #00BFFF, #ADD8E6) 1;'>", unsafe_allow_html=True)

    # Row 2
    col3, col4 = st.columns([2, 2])

    with col3:
        if st.button("🔧 Update Students", width="stretch"):
            st.session_state.current_page = "update_students"
            st.rerun()

    with col4:
        if st.button("📅 Initialize Today", width="stretch"):
            result = backend.initialize_attendance()
            if "Error" in result:
                st.error(result)
            else:
                st.success(result)
                # Optional: Add a brief sleep and rerun to refresh the table if it's visible
                time.sleep(2)
                st.rerun()

    st.markdown("<hr style='border: 2px solid; border-image: linear-gradient(to right, #0000FF, #00BFFF, #ADD8E6) 1;'>", unsafe_allow_html=True)

    # Row 3
    col5, col6 = st.columns([2, 2])

    with col5:
        if st.button("🚀 Model Full Retrain", width="stretch"):
            # Create a placeholder to hold the status container
            status_placeholder = st.empty()
            
            with status_placeholder.status("Processing full dataset...", expanded=True) as status:
                res = backend.process_classifier(mode="full")
                if "Error" in res:
                    status.update(label=res, state="error", expanded=False)
                else:
                    status.update(label=res, state="complete", expanded=False)
            
            # Wait 3 seconds, then wipe the entire status container away
            time.sleep(3)
            status_placeholder.empty()

    with col6:
        if st.button("⚡ Quick Retrain", width="stretch"):
            status_placeholder = st.empty()
            
            with status_placeholder.status("Updating model...", expanded=True) as status:
                res = backend.process_classifier(mode="quick")
                if "Error" in res:
                    status.update(label=res, state="error", expanded=False)
                else:
                    status.update(label=res, state="complete", expanded=False)
                
            time.sleep(3)
            status_placeholder.empty()
                                
    
elif st.session_state.current_page == "attendance":
    current_date = datetime.now().strftime("%d/%m/%Y")
    st.subheader(f"Today's Attendance Records {current_date}")
    
    data = backend.get_attendance_data()
    
    if isinstance(data, str): 
        st.error(data)
    else:
        if data.empty:
            st.info("No records found for today.")
        else:
            st.dataframe(data, width="stretch", hide_index=True)
            
            # Add your CSV button here
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="attendance.csv", mime='text/csv')

    if st.button("⬅ Back to Dashboard"):
        go_back()
        
elif st.session_state.current_page == "update_students":
    st.subheader("Manage Students")
    
    msg_slot = st.empty()
    # Input fields
    up_id = st.text_input("Student Matric No. (Format: NNDDNNNNNN, e.g., 22CG031879)")
    up_name = st.text_input("Student Name")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📸 Capture / Update Photos", width="stretch"):
            with st.spinner("Opening Camera..."):
                res = backend.generate_dataset(up_id, up_name)
                # 2. Check the result and show the message in the slot
                if "Error" in res:
                    msg_slot.error(res)
                else:
                    msg_slot.success(res)
                
                # 3. Wait 4 seconds, then wipe the message clean
                time.sleep(4)
                msg_slot.empty()

    with col_b:
        if st.button("🗑 Delete Student", width="stretch"):
            res = backend.remove_student(up_id)
            # 2. Check the result and show the message in the slot
            if "Error" in res:
                msg_slot.error(res)
            else:
                msg_slot.success(res)
                
            # 3. Wait 4 seconds, then wipe the message clean
            time.sleep(4)
            msg_slot.empty()


    st.markdown("<hr style='border: 2px solid; border-image: linear-gradient(to right, #0000FF, #00BFFF, #ADD8E6) 1;'>", unsafe_allow_html=True)
    
    if st.button("⬅ Back to Dashboard"):
        go_back()
        
elif st.session_state.current_page == "stats":
    st.header("📊 System Statistics")
    
    stats = backend.get_image_stats()
    
    if isinstance(stats, str):
        st.error(stats)
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 📁 Images Trained")
            st.title(f"{stats['total_data']}")
            
        with c2:
            st.markdown("### 🆕 New Images")
            st.title(f"{stats['total_new']}")
        
        st.divider()
        st.subheader("Images per Registered Student")
        
        # The Scrollable Box
        with st.container(height=300, border=True):
            if not stats["person_counts"]:
                st.info("No images found for registered students.")
            else:
                for person, count in stats["person_counts"].items():
                    # Displaying as a clean progress bar or text
                    st.write(f"**{person}**")
                    st.caption(f"{count} images total")
                    st.progress(min(count/100, 1.0)) # Assuming 100 is your goal
        
    if st.button("⬅ Back to Dashboard"):
        go_back()

elif st.session_state.current_page == "settings":
    st.header("⚙️ System Settings")

    with st.expander("📷 Camera Use", expanded=True):
        # Create a dictionary to map labels to indices
        cam_options = {"Built-in Webcam": 0, "External Camera": 1}
        current_choice = 0 if st.session_state.cam_index == 0 else 1

        selected_label = st.selectbox(
            "Select Camera Source", 
            options=list(cam_options.keys()),
            index=current_choice
        )

    with st.expander("🕒 Attendance Rules"):
        cooldown = st.number_input("Logging Cooldown (Seconds)", min_value=0, value=30)

    with st.expander("🔌 Database & Security"):
        if st.button("Test DB Connection"):
            # logic to ping backend.engine
            st.success("Connection Database: Online")

    with st.expander("👤 User Management and Deletion"):
        st.warning("⚠️ Deleting users is permanent. Proceed with caution.")
        
        target_user = st.text_input("User to delete")
        target_pass = st.text_input("Verif password", type="password")
        
        if st.button("🗑 Delete User", type="primary"):
            if target_user and target_pass:
                # Call the new backend function
                res = backend.delete_json_user(target_user, target_pass)
                    
                if "Success" in res:
                    st.success(res)
                        
                    # Check if you just deleted yourself
                    # Note: Make sure 'current_user' was saved in login.py!
                    if target_user == st.session_state.get("username"): 
                        st.warning("You deleted your own account. Logging out...")
                        time.sleep(2)
                        # Log out logic
                        st.session_state.authenticated = False
                        st.rerun()
                else:
                    st.error(res)
            else:
                st.warning("Please enter a username.")

    if st.button("💾 Save Settings", width="stretch", type="primary"):
        # Save the choices into session_state
        st.session_state.cam_index = cam_options[selected_label]
        
        st.success("Settings saved successfully!")
        time.sleep(1)
        st.rerun()

    if st.button("⬅ Back to Dashboard"):
        go_back()
        
# ---------------- LOGOUT ----------------
st.markdown("<br><br>", unsafe_allow_html=True)

col_spacer, col_logout = st.columns([5, 1])

with col_logout:
    if st.button("Logout", width="stretch", type="primary"):
        # 1. Clear the login state
        st.session_state.authenticated = False
        
        # 2. Reset the page to main so it's fresh when someone logs back in
        st.session_state.current_page = "main"
        
        # 3. Force a rerun to show the login screen immediately
        st.rerun()