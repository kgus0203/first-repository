import streamlit as st

@st.dialog("그룹생성 페이지")
def make_group():

    select_species = st.selectbox(
        '그룹을 생성하시겠습니까?',
        ['네','아니오']

    )
    st.radio(
        "어떤 종류의 음식점을 가나요?",
        options=["양식", "패스트푸드", "한식", "중식",'일식','분식'],

    )
    st.text_input(label="몇 명을 모집할까요?")
    st.text_input(label="그룹명을 정해주세요")
    st.date_input("모집 마감일은 언제까지인가요?")
    st.button("적용")

from datetime import datetime

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
    }
    .group-box {
        border: 2px solid #333333;
        padding: 20px;
        border-radius: 10px;
        background-color: #333333;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.dialog("group")
def group_name():
    st.markdown(
        """
        <style>
        .member-box {
            border: 2px solid #333333;
            padding: 20px;
            border-radius: 10px;
            background-color: #333333;
            color: white;
            margin: 10px 0;
            font-size: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .admin-icon {
            font-size: 24px;
            color: gold;
            margin-right: 8px;
        }
        .member-icon {
            font-size: 24px;
            color: lightgray;
            margin-right: 8px;
        }
        .manner-score {
            color: lightblue;
            font-size: 18px;
            margin-left: 15px;
            margin-right: auto;
        }
        .remove-button {
            color: red;
            font-size: 18px;
        }
        .bottom-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 상단 그룹 정보
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 그룹1")
        st.write("현재 인원: 5 / 전체 수용 가능 인원: 10")
    with col2:
        st.button("채팅창 열기")
        st.button("수정")

    # 어드민 정보 박스
    st.markdown(
        """
        <div class="member-box">
            <span><span class="admin-icon">👑</span><strong>ADMIN</strong></span>
            <span class="manner-score">⭐⭐⭐⭐⭐ (5.0)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 멤버 정보와 매너 점수 표시 함수
    def display_member_box(member_name, score, member_number):
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        full_stars = int(score)  # 버림 방식
        stars = "⭐" * full_stars

        st.markdown(
            f"""
            <div class="member-box">
                <span><span class="member-icon">{number_emojis[member_number - 1]}</span><strong>{member_name}</strong></span>
                <span class="manner-score">{stars} ({score})</span>
                <span class="remove-button">❌</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 멤버 목록
    members = [
        {"name": "멤버 1", "score": 4.5},
        {"name": "멤버 2", "score": 3.0},
        {"name": "멤버 3", "score": 4.0},
        {"name": "멤버 4", "score": 2.5},
    ]

    # 멤버 박스
    for i, member in enumerate(members, start=1):
        display_member_box(member["name"], member["score"], i)

    # 멤버 초대 박스
    st.markdown(
        """
        <div class="member-box">
            <span><strong>+ 멤버 초대하기</strong></span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 삭제 / 완료 버튼
    st.markdown(
        """
        <div class="bottom-buttons">
            <button style="background-color: #ff4b4b; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer;">삭제</button>
            <button style="background-color: #4caf50; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer;">완료</button>
        </div>
        """,
        unsafe_allow_html=True
    )


# 상단 제목과 검색 버튼 설정 (중앙 정렬)
st.markdown("<h1 class='centered-title'>그룹 페이지</h1>", unsafe_allow_html=True)

if st.button("그룹 생성",use_container_width=True,icon='🧑‍🤝‍🧑'):
    make_group()
# 검색 버튼
if st.button("그룹 검색",use_container_width=True,icon='🔍'):
    st.write("")

# 그룹 정보 예시
groups = [
    {"name": "그룹 1", "current_members": 5, "max_members": 10, "deadline": "2024-12-31"},
    {"name": "그룹 2", "current_members": 3, "max_members": 10, "deadline": "2024-11-30"},
]

for i in range(3):
    if i < len(groups):  # 그룹이 존재하는 경우
        group = groups[i]

        st.markdown(
            f"""
            <div class="group-box">
                <h2>{group["name"]}</h2>
                <p><strong>인원:</strong> {group['current_members']} / {group['max_members']}</p>
                <p><strong>마감일:</strong> {group['deadline']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if "group_name" not in st.session_state:
            if st.button("group %d" %(i+1),use_container_width=True):
                group_name()

    else:  # 그룹이 없는 경우
        st.markdown(
            """
            <div class="group-box">
                <h2>+ 그룹을 생성하십시오</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    # 그룹들 사이에 구분선
    st.write("---")

