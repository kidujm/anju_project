import streamlit as st
import pandas as pd
import os
import random

# ==========================================
# 1. 페이지 초기 설정 및 CSS
# ==========================================

st.set_page_config(
    page_title="오늘의 술안주 추천",
    layout="centered"
)

def local_css():
    st.markdown("""
    <style>
    :root {
        --brand: #00AC83;
        --brand2: #00c79a;
    }

    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background-color: #f6fffd;
    }

    .block-container {
        max-width: 420px !important;
        padding: 0 !important;
    }

    .stButton > button {
        padding: 10px 20px !important;
        border-radius: 18px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        background: #fff;
        color: #111 !important;
        font-weight: 600 !important;
        width: 100%;
    }

    .stButton > button:hover {
        background: #f2f2f2 !important;
    }

    .card {
        background: #fff;
        border-radius: 15px;
        padding: 18px;
        margin: 12px 14px;
        border: 1px solid rgba(0,0,0,0.05);
    }

    .topbar {
        padding: 14px;
        background: #fff;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }

    .brandmark {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        background: rgba(0,172,131,0.15);
        display: grid;
        place-items: center;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드
# ==========================================

@st.cache_data
def load_all_data():
    questions = pd.read_excel("data/anju_question_list.xlsx")
    types = pd.read_excel("data/anju_type_profiles.xlsx")
    dishes = pd.read_excel("data/anju_db_extended.xlsx")
    return questions, types, dishes

# ==========================================
# 3. 비디오 렌더링 (GitHub 배포용)
# ==========================================

def render_hero_video(path: str):
    if os.path.exists(path):
        st.video(path, autoplay=True, loop=True, muted=True)

# ==========================================
# 4.
