import streamlit as st
from FriendUser import FriendUser
from FriendManager import FriendManager
from BlockManager import BlockManager
from login2 import UserVO, UserDAO, SignUp, SignIn, SignOut, UserInfoCheck, ForgetIDPW, ChangeIDPW, UserSearch

# 초기 데이터 설정
if "user" not in st.session_state:
    st.session_state.user = FriendUser(user_id="user123", name="John Doe", profile_info="Hello! This is my profile.")
if "friend_manager" not in st.session_state:
    st.session_state.friend_manager = FriendManager()
if "block_manager" not in st.session_state:
    st.session_state.block_manager = BlockManager()
if "user_dao" not in st.session_state:
    st.session_state.user_dao = UserDAO()

user = st.session_state.user
friend_manager = st.session_state.friend_manager
block_manager = st.session_state.block_manager
user_dao = st.session_state.user_dao

# 페이지 선택
page = st.sidebar.selectbox(
    "페이지 선택",
    ["회원가입", "로그인", "친구 관리", "차단 관리", "비밀번호 복구", "사용자 검색", "내 정보"]
)

# 회원가입 페이지
if page == "회원가입":
    st.title("회원가입")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type="password")
    email = st.text_input("이메일")
    if st.button("회원가입"):
        user_info = UserVO(user_id=user_id, user_password=user_password, user_email=email)
        if UserInfoCheck.is_valid_user_info(user_info):
            signup = SignUp(user_id, user_password, email)
            signup.sign_up_event()

# 로그인 페이지
elif page == "로그인":
    st.title("로그인")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        signin = SignIn(user_id, user_password)
        if signin.sign_in_event():
            st.session_state.logged_in_user = user_id

# 친구 관리 페이지
elif page == "친구 관리":
    st.title("친구 관리")
    friend_id = st.text_input("친구 추가/삭제 ID")
    if st.button("친구 추가"):
        if friend_manager.add_friend(friend_id):
            st.success(f"{friend_id} 추가 완료")
        else:
            st.warning(f"{friend_id} 이미 친구 목록에 있음")
    if st.button("친구 삭제"):
        if friend_manager.delete_friend(friend_id):
            st.success(f"{friend_id} 삭제 완료")
        else:
            st.warning(f"{friend_id} 친구 목록에 없음")
    st.subheader("친구 목록")
    st.write(friend_manager.get_friends())

# 차단 관리 페이지
elif page == "차단 관리":
    st.title("차단 관리")
    block_id = st.text_input("차단/해제 사용자 ID")
    if st.button("사용자 차단"):
        if block_manager.block_user(block_id):
            st.success(f"{block_id} 차단 완료")
        else:
            st.warning(f"{block_id} 이미 차단 목록에 있음")
    if st.button("차단 해제"):
        if block_manager.unblock_user(block_id):
            st.success(f"{block_id} 차단 해제 완료")
        else:
            st.warning(f"{block_id} 차단 목록에 없음")
    st.subheader("차단 목록")
    st.write(block_manager.get_blocked_users())

# 비밀번호 복구 페이지
elif page == "비밀번호 복구":
    st.title("비밀번호 복구")
    email = st.text_input("이메일 입력")
    if st.button("복구 토큰 전송"):
        forget_id_pw = ForgetIDPW(email=email)
        forget_id_pw.send_recovery_email()
    token = st.text_input("복구 토큰 입력")
    new_password = st.text_input("새 비밀번호", type="password")
    if st.button("비밀번호 복구"):
        forget_id_pw = ForgetIDPW(email=email)
        if forget_id_pw.verify_token(token):
            forget_id_pw.reset_password(new_password)

# 사용자 검색 페이지
elif page == "사용자 검색":
    st.title("사용자 검색")
    search_term = st.text_input("검색할 사용자 ID/이메일")
    if st.button("검색"):
        user_search = UserSearch()
        if user_search.user_searched_event(search_term):
            searched_user = user_search.get_searched_user()
            st.write(f"ID: {searched_user.user_id}, 이메일: {searched_user.user_email}")
        else:
            st.warning("사용자를 찾을 수 없습니다.")

# 내 정보 페이지
elif page == "내 정보":
    st.title("내 정보")
    st.sidebar.header("프로필")
    st.sidebar.write(f"**ID:** {user.get_user_id()}")
    st.sidebar.write(f"**Name:** {user.get_name()}")
    st.sidebar.write(f"**Profile Info:** {user.get_profile_info()}")
