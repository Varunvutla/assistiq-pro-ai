import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import streamlit as st

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

# ======================================
# INITIALIZE DATABASE
# ======================================

init_db()
create_users_table()

# ======================================
# STREAMLIT CONFIG
# ======================================

st.set_page_config(
    page_title="AssistIQ Pro AI",
    page_icon="🤖",
    layout="wide"
)

# ======================================
# SESSION STATE
# ======================================

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# ======================================
# THEME
# ======================================

theme = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"]
)

st.session_state.theme = theme

# ======================================
# LOAD CSS
# ======================================

if theme == "Dark":
    load_css("assets/dark.css")
else:
    load_css("assets/light.css")

# ======================================
# LOGIN PAGE
# ======================================

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

    # ======================================
    # LOGIN / REGISTER TABS
    # ======================================

    login_tab, register_tab = st.tabs([
        "🔐 Login",
        "📝 Register"
    ])

    # ======================================
    # LOGIN TAB
    # ======================================

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
            key="normal_login_button"
        ):

            user = login_user(
                login_email,
                login_password
            )

            if user:

                st.session_state.user = {
                    "name": user[1],
                    "email": user[2]
                }

                st.success("Login successful")

                st.rerun()

            else:

                st.error(
                    "Invalid email or password"
                )

    # ======================================
    # REGISTER TAB
    # ======================================

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
            key="register_button"
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

    st.markdown("---")

    st.info(
        "Google Login is temporarily disabled."
    )

    st.stop()

# ======================================
# CHAT PAGE
# ======================================

else:

    # ======================================
    # SIDEBAR
    # ======================================

    st.sidebar.title("🤖 AssistIQ Pro AI")

    st.sidebar.caption(
        "Your Personal AI Assistant"
    )

    st.sidebar.success(
        f"Welcome {st.session_state.user['name']}"
    )

    # ======================================
    # NEW CHAT
    # ======================================

    if st.sidebar.button(
        "➕ New Chat",
        key="new_chat_button"
    ):

        st.session_state.messages = []
        st.session_state.conversation_id = None

        st.rerun()

    # ======================================
    # CLEAR CURRENT CHAT
    # ======================================

    if st.sidebar.button(
        "🗑 Clear Current Chat",
        key="clear_chat_button"
    ):

        st.session_state.messages = []

        st.rerun()

    st.sidebar.markdown("---")

    # ======================================
    # CHAT HISTORY
    # ======================================

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

    st.sidebar.markdown("---")

    # ======================================
    # LOGOUT
    # ======================================

    if st.sidebar.button(
        "🚪 Logout",
        key="logout_button"
    ):

        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.conversation_id = None

        st.rerun()

    # ======================================
    # MAIN CHAT AREA
    # ======================================

    st.title("💬 AI Assistant")

    # ======================================
    # WELCOME MESSAGE
    # ======================================

    if len(st.session_state.messages) == 0:

        welcome_message = f"""
👋 Hey {st.session_state.user['name']}!

I'm AssistIQ Pro AI.

How can I help you today?

You can ask me:

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

    # ======================================
    # SHOW CHAT HISTORY
    # ======================================

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])

    # ======================================
    # CHAT INPUT
    # ======================================

    prompt = st.chat_input(
        "Ask me anything..."
    )

    # ======================================
    # HANDLE CHAT
    # ======================================

    if prompt:

        # CREATE NEW CONVERSATION

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