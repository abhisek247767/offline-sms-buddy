"""Offline SMS Buddy: the Streamlit page."""

import streamlit as st

from offline_sms_buddy.llm import (
    SmsBuddyError,
    explain_sms,
    looks_risky,
    mentions_otp,
)

st.set_page_config(page_title="Offline SMS Buddy", page_icon="📱", layout="centered")

# Larger text and buttons for older users
st.markdown(
    """
    <style>
    html, body, p, li, label, .stMarkdown { font-size: 21px !important; line-height: 1.6; }
    h1 { font-size: 44px !important; text-align: center; }
    h2, h3 { font-size: 30px !important; }
    .stTextArea textarea { font-size: 22px !important; }
    div.stButton > button {
        font-size: 24px !important;
        padding: 0.6em 1.2em;
        width: 100%;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📱 Offline SMS Buddy")

sms = st.text_area(
    "Paste a confusing SMS below:",
    height=180,
    placeholder="Paste SMS here...",
)

if st.button("Explain SMS", type="primary"):
    if not sms.strip():
        st.warning("Please paste an SMS in the box first.")
    else:
        with st.spinner("Reading your SMS... this can take a few seconds."):
            try:
                result = explain_sms(sms.strip())
            except SmsBuddyError as e:
                st.error(str(e))
                st.stop()

        # Safety warnings that don't depend on the AI
        if looks_risky(sms):
            st.error(
                "🚨 This SMS may be a scam. Do not click any link in it. "
                "Call your bank or company using the number on your card or their official app."
            )
        if mentions_otp(sms):
            st.warning("🔑 Never share an OTP with anyone, even if they say they are from the bank.")

        st.divider()
        st.subheader("🧠 Simple Explanation")
        st.write(result.meaning)

        st.subheader("⚠️ What should I do?")
        st.write(result.what_to_do)

        st.subheader("🛑 Be careful about")
        st.write(result.be_careful)

st.divider()
st.subheader("🔒 Privacy")
st.write(
    "Your SMS is processed on this computer. "
    "No SMS is sent to a cloud AI service."
)