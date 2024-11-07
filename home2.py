import pandas as pd
import streamlit as st

# 페이지 스타일
st.markdown(
    """
    <style>
    .profile-box {
        display: flex;
        align-items: center;
    }
    .profile-photo {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: #cccccc;  /* 임시 배경색 */
        margin-right: 10px;
    }
    .status-circle {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-on {
        background-color: green;
    }
    .status-off {
        background-color: lightgray;
    }
    .friend-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #333;
        font-size: 18px;
    }
    .top-buttons {
        display: flex;
        gap: 10px;
        margin-left: auto;
    }
    .friend-buttons {
        display: flex;
        justify-content: flex-start; /* 버튼을 좌측 정렬 */
        gap: 10px;
        margin-top: 10px; /* 버튼 상단 여백 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 예시 사용자 정보
USER_PROFILE = {
    "username": "사용자이름",
    "profile_pic": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"  # 임시 프로필 이미지 URL
}

# 타이틀을 중앙에 크게 배치
st.markdown("<h1 style='text-align: center;'>맛ZIP</h1>", unsafe_allow_html=True)

# 사용자 프로필 및 로그아웃 버튼 표시
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.image(USER_PROFILE["profile_pic"], width=50)  # 프로필 사진
with col2:
    st.write(f"**{USER_PROFILE['username']}**")  # 사용자 이름
with col3:
    if st.button("로그아웃"):
        st.warning("로그아웃 되었습니다.")  # 로그아웃 동작 추가 가능

# 사이드바 제목
st.sidebar.title('친구 목록')

# 사이드바에 사용자 프로필과 버튼들을 한 줄에 배치
st.sidebar.markdown(
    f"""
    <div class="profile-box">
        <div class="profile-photo" style="background-image: url('{USER_PROFILE["profile_pic"]}');"></div>  <!-- 프로필 사진 -->
        <span><strong>{USER_PROFILE["username"]}</strong></span>
    </div>
    """,
    unsafe_allow_html=True
)

# 프로필 아래에 버튼 배치
st.sidebar.markdown(
    """
    <div class="friend-buttons">
        <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #4CAF50; color: white; border: none; cursor: pointer;">친구찾기</button>
        <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #FFA500; color: white; border: none; cursor: pointer;">친구 대기</button>
        <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #FF6347; color: white; border: none; cursor: pointer;">차단/해제</button>
        <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #DC143C; color: white; border: none; cursor: pointer;">삭제</button>
    </div>
    """,
    unsafe_allow_html=True
)

# 친구 목록 섹션
st.sidebar.markdown("## 친구 목록")

# 친구 상태 표시 함수
def display_friend(name, online):
    status_color = "status-on" if online else "status-off"
    st.sidebar.markdown(
        f"""
        <div class="friend-row">
            <span>{name}</span>
            <div class="status-circle {status_color}"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 친구 목록 데이터 (예시)
friends = [
    {"name": "친구 1", "online": True},
    {"name": "친구 2", "online": False},
    {"name": "친구 3", "online": True},
    {"name": "친구 4", "online": False},
]

# 친구 목록 출력
for friend in friends:
    display_friend(friend["name"], friend["online"])

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
                st.subheader(post["맛집 이름"])  # 맛집 이름 표시
                st.image(post["이미지"], caption=post["맛집 이름"], use_column_width=True)  # 이미지 표시

# 우측 하단: 그룹 버튼
st.markdown(
    """
    <div style='position: fixed; bottom: 20px; right: 20px;'>
        <button onclick="window.location.href='#'">그룹</button>
    </div>
    """, unsafe_allow_html=True)


