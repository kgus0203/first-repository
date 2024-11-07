from ctypes.wintypes import PWORD
import pandas as pd
import streamlit as st

col1, col2 = st.columns(2)

col5,col6=st.columns(2)
@st.dialog("로그인 페이지")
def login():
    st.write("")
    username=st.text_input("사용자 이름")
    password=st.text_input("비밀번호", type='password')
    st.button("ID/PW찾기",use_container_width=True)
    if st.button("로그인","pages/home2.py",use_container_width=True):
        st.switch_page("pages/home2.py")



with col1:
    st.title("맛ZIP")
with col2:
    col3,col4 = st.columns(2)
    with col3:
        st.button("회원가입",use_container_width=True)
    with col4:
        if "login" not in st.session_state:
            if st.button("로그인",use_container_width=True):
                login()

# 중앙: 추천 포스트 리스트
st.title("추천 맛집 포스트")
st.write("인기 포스팅")

# 예시 포스트 데이터
posts = pd.DataFrame({
    "작성자": ["user1", "user2", "user3", "user4"],
    "맛집 이름": ["맛집1", "맛집2", "맛집3", "맛집4"],
    "이미지": [
        "https://cdn.pixabay.com/photo/2021/02/04/12/47/food-5981232_960_720.jpg",  # 임시 이미지 URL
        "https://cdn.pixabay.com/photo/2015/11/19/10/38/food-1050813_960_720.jpg",
        "https://cdn.pixabay.com/photo/2017/07/15/13/45/french-restaurant-2506490_960_720.jpg",
        "https://cdn.pixabay.com/photo/2020/06/30/15/03/table-5356682_960_720.jpg"
    ]
})

# 포스트를 두 개씩 카드 형식으로 나열
for i in range(0, len(posts), 2):
    cols = st.columns(2)  # 두 개의 컬럼 생성
    for j, col in enumerate(cols):
        if i + j < len(posts):
            post = posts.iloc[i + j]
            with col:
                st.image(post["이미지"], caption=post["맛집 이름"], use_column_width=True)  # 이미지 표시
                st.subheader(post["맛집 이름"])  # 맛집 이름 표시

# 우측 하단: 그룹 및 친구 버튼
st.markdown(
    """
    <div style='position: fixed; bottom: 20px; right: 20px;'>
        <button onclick="window.location.href='#'">그룹</button>
        <button onclick="window.location.href='#'">친구</button>
    </div>
    """, unsafe_allow_html=True)

