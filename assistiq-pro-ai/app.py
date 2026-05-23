import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import streamlit as st
import requests

from streamlit_oauth import OAuth2Component

from utils.auth import *

from database.db import (
    init_db,
    create_conversation,
    get_conversations,
    save_message,
    get_messages
)

from utils.ai import generate_response
from utils.helpers import load_css

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="AssistIQ Pro AI",
    page_icon="🤖",
    layout="wide"
)

# =========================================
# DATABASE
# =========================================

init_db()
create_users_table()

# =========================================
# SESSION STATE
# =========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "user" not in st.session_state:
    st.session_state.user = None

# =========================================
# THEME
# =========================================

theme = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"]
)

st.session_state.theme = theme

if theme == "Dark":
    load_css("assets/dark.css")
else:
    load_css("assets/light.css")

# =========================================
# GOOGLE OAUTH
# =========================================

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"

REDIRECT_URI = (
    "https://assistiq-pro-ai-bnqqbtfpnpwdrgffoyzjnp.streamlit.app/"
    "component/streamlit_oauth.authorize_button"
)

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    REFRESH_TOKEN_URL
)

# =========================================
# LOGIN PAGE
# =========================================

if st.session_state.user is None:

    st.markdown(
        """
        <h1 style='text-align:center;'>
        🤖 AssistIQ Pro AI
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h4 style='text-align:center; color:gray;'>
        Your Personal AI Assistant
        </h4>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    login_tab, register_tab = st.tabs([
        "🔐 Login",
        "📝 Register"
    ])

    # =========================================
    # LOGIN TAB
    # =========================================

    with login_tab:

        st.subheader("Login")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            key="normal_login_button",
            use_container_width=True
        ):

            user_data = login_user(
                login_email,
                login_password
            )

            if user_data:

                st.session_state.user = {
                    "name": user_data[1],
                    "email": user_data[2]
                }

                st.success("Login successful")

                st.rerun()

            else:

                st.error(
                    "Invalid email or password"
                )

    # =========================================
    # REGISTER TAB
    # =========================================

    with register_tab:

        st.subheader("Create Account")

        register_name = st.text_input(
            "Name",
            key="register_name"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        if st.button(
            "Create Account",
            key="register_button",
            use_container_width=True
        ):

            success = register_user(
                register_name,
                register_email,
                register_password
            )

            if success:

                st.success(
                    "Account created successfully"
                )

            else:

                st.error(
                    "Email already exists"
                )

    # =========================================
    # GOOGLE LOGIN
    # =========================================

    st.markdown("---")

    result = oauth2.authorize_button(
        name="Continue with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google",
        use_container_width=True
    )

    if result and "token" in result:

        token = result["token"]

        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={
                "Authorization": f"Bearer {token['access_token']}"
            }
        )

        user_info = userinfo_response.json()

        st.session_state.user = {
            "name": user_info.get("name"),
            "email": user_info.get("email")
        }

        st.success(
            f"Welcome {user_info.get('name')}"
        )

        st.rerun()

    st.stop()

# =========================================
# SIDEBAR
# =========================================

st.sidebar.title("🤖 AssistIQ Pro AI")

st.sidebar.caption(
    "Your Personal AI Assistant"
)

st.sidebar.success(
    f"Welcome {st.session_state.user['name']}"
)

# =========================================
# NEW CHAT
# =========================================

if st.sidebar.button(
    "➕ New Chat"
):

    st.session_state.messages = []
    st.session_state.conversation_id = None

    st.rerun()

# =========================================
# CLEAR CHAT
# =========================================

if st.sidebar.button(
    "🗑 Clear Current Chat"
):

    st.session_state.messages = []

    st.rerun()

st.sidebar.markdown("---")

# =========================================
# CHAT HISTORY
# =========================================

conversations = get_conversations(
    st.session_state.user["email"]
)

st.sidebar.subheader("Chat History")

for conv in conversations:

    if st.sidebar.button(
        conv["title"],
        key=f"conv_{conv['id']}"
    ):

        st.session_state.conversation_id = conv["id"]

        old_messages = get_messages(
            conv["id"]
        )

        st.session_state.messages = []

        for msg in old_messages:

            st.session_state.messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        st.rerun()

# =========================================
# LOGOUT
# =========================================

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):

    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.conversation_id = None

    st.rerun()

# =========================================
# MAIN CHAT
# =========================================

st.title("💬 AI Assistant")

if len(st.session_state.messages) == 0:

    welcome_message = f"""
👋 Hey {st.session_state.user['name']}!

I'm AssistIQ Pro AI.

How can I help you today?

• Coding questions
• AI concepts
• Resume help
• Project ideas
• FAQs
"""

    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome_message
    })

# =========================================
# SHOW CHAT
# =========================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

# =========================================
# CHAT INPUT
# =========================================

prompt = st.chat_input(
    "Ask me anything..."
)

if prompt:

    if st.session_state.conversation_id is None:

        title = prompt[:30]

        st.session_state.conversation_id = create_conversation(
            st.session_state.user["email"],
            title
        )

    # USER MESSAGE

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    save_message(
        st.session_state.conversation_id,
        "user",
        prompt
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # AI RESPONSE

    response = generate_response(prompt)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    save_message(
        st.session_state.conversation_id,
        "assistant",
        response
    )

    with st.chat_message("assistant"):

        st.markdown(response)