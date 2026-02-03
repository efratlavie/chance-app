import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="💬 צ'אט חי – Chance VIP", layout="centered")

st.title("💬 צ'אט חי – Chance VIP")
st.write("צ'אט פתוח לכל המשתמשים")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

with st.form("chat_form", clear_on_submit=True):
    username = st.text_input("שם / כינוי")
    message = st.text_input("הודעה")
    send = st.form_submit_button("שלח")

    if send and username and message:
        supabase.table("chat_messages").insert({
            "username": username,
            "message": message,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

st.markdown("---")
st.subheader("💬 הודעות אחרונות")

data = (
    supabase
    .table("chat_messages")
    .select("*")
    .order("created_at", desc=False)
    .execute()
)

for row in data.data:
    st.markdown(f"**{row['username']}**: {row['message']}")
