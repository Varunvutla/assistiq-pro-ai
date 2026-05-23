from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent

def load_css(css_file):

    css_path = BASE_DIR / css_file

    with open(css_path) as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )