import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "User", "Admin"]


def login():

    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
user_quiz = st.Page(
    "pages/user/quiz.py",
    title="Welcome Page",
    icon=":material/help:",
    default=(role == "User"),
)
user_adaptive = st.Page(
    "pages/user/adaptive.py", title="Adaptive Quizz", icon=":material/bug_report:"
)
user_scenario = st.Page(
    "pages/user/scenario.py", title="Adaptive Scenario Quizz", icon=":material/bug_report:"
)
user_report = st.Page(
    "pages/user/report.py", title="Report stats", icon=":material/bug_report:"
)
admin_dashboard = st.Page(
    "pages/admin/dashboard.py",
    title="Admin Dashboard",
    icon=":material/dashboard:",
    default=(role == "Admin"),
)
admin_report = st.Page("pages/admin/reports.py", title="Admin Report", icon=":material/security:")

account_pages = [logout_page, settings]
request_pages = [user_quiz, user_adaptive, user_scenario, user_report ]
admin_pages = [admin_dashboard, admin_report]

st.title("Welcome to Quizz!!")
st.logo("pages/images/horizontal_logo.png", icon_image="pages/images/quiz.png")

page_dict = {}
if st.session_state.role in ["User", "Admin"]:
    page_dict["User"] = request_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()