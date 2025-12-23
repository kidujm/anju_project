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
# 4. 결과 계산 로직
# ==========================================

QUESTION_WEIGHT = {1: 3, 2: 3, 3: 2, 4: 2}

def calculate_result(answers, questions, types, dishes):
    type_scores = {t['keyword']: 0 for _, t in types.iterrows()}

    for q_no, answer in answers.items():
        weight = QUESTION_WEIGHT.get(int(q_no), 1)

        best_type = None
        best_score = 0

        for _, t in types.iterrows():
            tokens = str(t['core_combo']).split(',')
            match = sum(tok.strip() in answer for tok in tokens)

            if match > best_score:
                best_score = match
                best_type = t['keyword']

        if best_type:
            type_scores[best_type] += weight

    for k in type_scores:
        type_scores[k] += random.uniform(0, 0.3)

    best_keyword = max(type_scores, key=type_scores.get)
    best_type = types[types['keyword'] == best_keyword].iloc[0]

    dishes = dishes.copy()
    dishes["score"] = 0

    spicy_count = sum("매콤" in a for a in answers.values())
    mild_count = sum("담백" in a for a in answers.values())
    soup_count = sum("국물" in a for a in answers.values())

    dishes["score"] += dishes["spicy_level"] * spicy_count
    dishes["score"] += (5 - dishes["spicy_level"]) * mild_count

    if soup_count > 0:
        dishes["score"] -= dishes["spicy_level"] * 0.5

    dishes["score"] += [random.uniform(0, 0.5) for _ in range(len(dishes))]

    top_dishes = dishes.sort_values("score", ascending=False).head(5)

    return best_type, top_dishes

# ==========================================
# 5. 메인 앱
# ==========================================

def main():
    local_css()
    questions, types, dishes = load_all_data()

    st.markdown("""
    <div class="topbar">
        <div class="brandmark">🍻</div>
        <div>
            <b>오늘의 술안주 추천</b><br>
            <small>STEP 선택형 테스트</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "step" not in st.session_state:
        st.session_state.step = "landing"
    if "q_idx" not in st.session_state:
        st.session_state.q_idx = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    # ------------------------------
    # 랜딩 페이지
    # ------------------------------
    if st.session_state.step == "landing":
        render_hero_video("videos/hero.mp4")

        st.markdown("""
        <div class="card">
            <p>질문에 답하면 엑셀 DB 기반으로 오늘의 술안주를 추천해드립니다.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("시작하기"):
            st.session_state.step = "quiz"
            st.rerun()

    # ------------------------------
    # 퀴즈 페이지
    # ------------------------------
    elif st.session_state.step == "quiz":
        q_idx = st.session_state.q_idx
        q_row = questions.iloc[q_idx]
        q_no = int(q_row["q_no"])

        img_path = f"images/q{q_no}.png"
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)

        st.progress((q_idx + 1) / len(questions))

        st.markdown(f"""
        <div class="card">
            <h3>Q{q_no}. {q_row['question']}</h3>
        </div>
        """, unsafe_allow_html=True)

        options = [
            q_row.get("option_1"),
            q_row.get("option_2"),
            q_row.get("option_3"),
            q_row.get("option_4"),
        ]
        options = [o for o in options if pd.notna(o) and str(o).strip() != ""]

        for opt in options:
            if st.button(opt, key=f"{q_idx}_{opt}"):
                st.session_state.answers[str(q_no)] = opt
                if q_idx + 1 < len(questions):
                    st.session_state.q_idx += 1
                else:
                    st.session_state.step = "result"
                st.rerun()

        if q_idx > 0:
            if st.button("← 이전 질문"):
                st.session_state.q_idx -= 1
                st.rerun()

    # ------------------------------
    # 결과 페이지
    # ------------------------------
    elif st.session_state.step == "result":
        best_type, top_dishes = calculate_result(
            st.session_state.answers,
            questions,
            types,
            dishes
        )

        st.balloons()

        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <h2>{best_type['keyword']}</h2>
            <p>{best_type['core_combo']}</p>
        </div>

        <div class="card">
            <h4>추천 안주 TOP 5</h4>
            <ul>
                {''.join(f"<li>{n}</li>" for n in top_dishes['name'])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("다시 테스트하기"):
            st.session_state.step = "landing"
            st.session_state.q_idx = 0
            st.session_state.answers = {}
            st.rerun()

# ==========================================
# 실행
# ==========================================

if __name__ == "__main__":
    main()
