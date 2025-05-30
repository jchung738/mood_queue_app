import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets Setup ---
@st.cache_resource

def connect_to_gsheet():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Mood Queue Tracker").sheet1
    return sheet

sheet = connect_to_gsheet()

# --- Title ---
st.title("🧠 Mood of the Queue")
st.write("Log how the ticket queue *feels* today.")

# --- Mood Logging ---
st.subheader("1. Log a Mood")
mood = st.selectbox("Select a mood:", ["😊", "😠", "😕", "🎉"])
note = st.text_input("Optional note:")

if st.button("Submit Mood"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, mood, note])
    st.success("Mood logged successfully!")

# --- Mood Visualization ---
st.subheader("2. Today's Mood Trends")

def load_data():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
    return df

df = load_data()
today = datetime.now().date()
df_today = df[df['date'] == today]

if not df_today.empty:
    mood_counts = df_today['mood'].value_counts().reset_index()
    mood_counts.columns = ['Mood', 'Count']
    fig = px.bar(mood_counts, x='Mood', y='Count', title='Mood Counts Today', color='Mood')
    st.plotly_chart(fig)
else:
    st.info("No moods logged today yet.")

# --- Auto-refresh option ---
st.markdown("---")
refresh = st.checkbox("Auto-refresh every 30s")
if refresh:
    st.experimental_rerun()
