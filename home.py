import streamlit as st
from streamlit_extras.row import row


# Function to handle logout logic
def logout():
    st.session_state.clear()
    st.success("Logged out successfully!")
    st.rerun()

def home():
    role = st.session_state.get('role')
    # Define pages for navigation
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
    user_quiz = st.Page("pages/user/welcome.py", title="Dashboard", icon=":material/home:", default=(role == "User"))
    user_adaptive = st.Page("pages/user/adaptive.py", title="Adaptive Quiz", icon=":material/line_style:")
    user_scenario = st.Page("pages/user/scenario.py", title="Scenario Quiz", icon=":material/interests:")
    user_report = st.Page("pages/user/report.py", title="Report stats", icon=":material/analytics:")
    user_challenge = st.Page("pages/user/challenge.py", title="Peer Challenge", icon=":material/group:")
    admin_dashboard = st.Page("pages/admin/dashboard.py", title="Admin Dashboard", icon=":material/dashboard:", default=(role == "Admin"))
    admin_report = st.Page("pages/admin/reports.py", title="Admin Report", icon=":material/analytics:")
    admin_view = st.Page("pages/admin/admin.py", title="Admin View", icon=":material/security:")
    superadmin_view = st.Page("pages/admin/super_admin.py", title="Super Admin Dashboard", icon=":material/security:", default=(role == "super_admin"))


    account_pages = [logout_page, settings]
    request_pages = [user_quiz, user_adaptive, user_scenario, user_report,user_challenge]
    admin_pages = [admin_dashboard, admin_report, admin_view]
    superadmin_pages = [superadmin_view]

    # Logo for the app
    # st.title("Welcome to Quizz!!")
    st.logo("pages/images/horizontal_logo.png", icon_image="pages/images/quiz.png")

    # Main navigation logic
    if st.session_state.role is None or not st.session_state.logged_in:
        # If user is not logged in, show login/signup pages
        # pg = st.navigation([st.Page(main_page)])
        st.switch_page("main.py")  # Login and Signup are separate pages
        
    else:
        # If user is logged in, show appropriate pages based on their role
        page_dict = {}
        if st.session_state.role in ["User", "Admin", "super_admin"]:
            page_dict["User"] = request_pages
        if st.session_state.role == "Admin":
            page_dict["Admin"] = admin_pages
        if st.session_state.role == "super_admin":
            page_dict["Admin"] = admin_pages
            page_dict["Super Admin"] = superadmin_pages


        # Sidebar with navigation options
        # st.sidebar.title(f"Welcome, {st.session_state.username}!")
        header1, header2 = st.columns([1,0.2])
        with header2.expander("Profile", icon=":material/account_circle:"):
            # with st.container(border=True):
            # row2 = row([0.3,1], vertical_align="bottom")
            col1,col2 = st.columns([0.6,1])
            col1.image(st.session_state["profile_photo"],use_container_width=True)
            col2.write(f"**{st.session_state['username']}**")
            col2.write(f"**{st.session_state.role}**")

        # Display the pages based on the user's role
        if len(page_dict) > 0:
            pg = st.navigation({"Account": account_pages} | page_dict)
            pg.run()