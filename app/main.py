import streamlit as st
import pandas as pd
import plotly.express as px
import uuid
import time
from rag_utils import analyze_question
import os

os.environ["STREAMLIT_SERVER_PORT"] = os.getenv("PORT", "8501")
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="MedBot", layout="wide", page_icon="💊")

# -----------------------------
# Session state
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "typing" not in st.session_state:
    st.session_state.typing = False

# -----------------------------
# CSS Styling
# -----------------------------
st.markdown("""
<style>
body {background: linear-gradient(180deg,#e6f2f5,#ffffff); font-family:'Poppins',sans-serif;}
.chat-header {position: sticky; top:0; z-index:999; background: linear-gradient(90deg,#87cefa,#00bfff); color:white; font-weight:bold; font-size:22px; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 3px 10px rgba(0,0,0,0.2); border-radius:0 0 20px 20px;}
.chat-box {max-height: calc(100vh - 140px); overflow-y:auto; padding:15px; display:flex; flex-direction:column; gap:10px;}
.msg {padding:12px 16px; border-radius:20px; margin:8px 0; max-width:70%; display:flex; align-items:center;}
.user {background: linear-gradient(135deg,#4facfe,#00f2fe); color:white; align-self:flex-end; flex-direction:row-reverse; gap:8px;}
.bot {background:#f1f3f5; color:#212529; align-self:flex-start; gap:8px;}
.msg img {width:32px; height:32px; border-radius:50%;}
.typing {font-style:italic; color:#555; margin-left:40px;}
.input-container {position: sticky; bottom:0; display:flex; align-items:center; gap:8px; padding:10px 15px; background:white; border-top:1px solid #ccc; z-index:998;}
.input-container input {flex:1; padding:12px; border-radius:25px; border:1px solid #ccc; outline:none;}
.send-btn {background:#0dcaf0; border:none; border-radius:50%; width:42px; height:42px; cursor:pointer; font-size:18px;}
@media (max-width: 768px) { .msg {max-width:90%;} .chat-header {font-size:18px;} }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="chat-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/4228/4228675.png" width="30">
        MedBot RAG - Your Health Assistant
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Input handler
# -----------------------------
def process_input():
    user_message = st.session_state.get("temp_input", "").strip()
    if not user_message:
        return

    # Append user message
    st.session_state.chat_history.append({"role":"user","message": user_message})
    st.session_state.typing = True
    time.sleep(0.3)

    # Get response
    responses = analyze_question(user_message)
    st.session_state.chat_history.append({
        "role":"bot",
        "message": responses.get("answer", ""),
        "data": responses.get("data", pd.DataFrame()),
        "fig": responses.get("fig", None)
    })

    st.session_state.typing = False
    st.session_state.temp_input = ""

# -----------------------------
# Display chat
# -----------------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"""
        <div class="msg user">
            <img src="https://cdn-icons-png.flaticon.com/512/147/147144.png">{chat['message']}
        </div>""", unsafe_allow_html=True)
    else:
        bot_html = chat['message'].replace("\n","<br>")
        st.markdown(f"""
        <div class="msg bot">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png">{bot_html}
        </div>""", unsafe_allow_html=True)

        # Display Plotly chart if available with unique key
        if chat.get("fig") is not None:
            st.plotly_chart(chat["fig"], use_container_width=True, key=str(uuid.uuid4()))
        # Display small table preview if fig not available
        elif chat.get("data") is not None and not chat["data"].empty:
            st.dataframe(chat["data"].head(5))

# Typing indicator
if st.session_state.typing:
    st.markdown('<div class="typing">MedBot is typing...</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Input box sticky
# -----------------------------
col1, col2 = st.columns([9,1])
with col1:
    st.text_input(
        "Type your message...",
        key="temp_input",
        label_visibility="collapsed",
        placeholder="Ask MedBot about heart health"
    )
with col2:
    st.button("SEND", key="send_btn", on_click=process_input)
