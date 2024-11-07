from ctypes.wintypes import PWORD
import pandas as pd
import streamlit as st
from streamlit import date_input, caption
import datetime



#-- UserDAO--
#InsertDbUser 입력받은 UserVO를 디비에 연결
#UpdateDbUser
#DeleteDbUser
#SearchDbUser
#isValidUserVO 유저 객체가 유효한지 검사, 무결성 유지
#generateSeq 새로운 사용자의 시퀀스 번호 생성
#updateUserId
#updateUserPassword

#-- signup --

#sendConfirmationEmail 회원 가입 성공 후 확인 이메일 발송
#clearSignupData 회원가입 이후 객체 내 데이터 초기화

#--UserInfoCheck --
#essential_user_info_check 필수 항목이 모두 채워져 있는지 확인
#existing_user_overlap_check
#password_check
#is_online_check
#email_auth

# -- change ID/password --

#current_id
#new_id
#current_password
#new_password
#changeDate
#update_id
#update_password
#validate_new_id_password

# -- forgot --
#email 복구 이메일
#recovery_token 비밀번호 복구 시 고유 복구 토큰, 랜덤 생성, 특정 시간동안 유효
#token_expiry 토큰 유효 시간 정의
#is_recovered 비밀번호가 성공적으로 변경되었는지
#send_recovery_email
#generate_token 복구 토큰 생성
#recover_id_password 복구 검증 트루,폴스
#validate_recovery_token 복구 토큰 유혀성 검사
#is_Token_Expired 토큰 만료 확인

# -- UserSearch --
#searched_user 검색 유저 객체를 저장하는 변수
#user_searched_event 검색 성공 여부
#get_searched_user 검색 객체 반환
#result_event 검색 결과 출력

# -- signin --
#sign_in_user 로그인 시도 사용자 정보
#sign_in_evnet 로그인 절차 실행
#aleart_message
#result_event 로그인 절차가 끝났을 때 결과 전달

# --signout --
#sign_out_user
#sign_out_user
#update_user_offline 로그아웃 시 발생 로직
#result_event 로그아웃 결과

@st.dialog("로그인 페이지")
def login():
    st.write("")
    username=st.text_input("사용자 이름")
    password=st.text_input("비밀번호", type='password')
    st.button("ID/PW찾기",use_container_width=True)
    if st.button("로그인","pages/home2.py",use_container_width=True):
        st.switch_page("pages/home2.py")

class UserVO:
    def __init__(self,user_id, user_password, user_email):
        self.user_ID=user_id
        self.user_password=user_password
        self.user_email=user_email
        self.user_seq=0
        self.user_is_online=False

    def uservo(self):
        self.user_ID = ''
        self.user_password = ''
        self.user_email = ''
        self.user_seq = 0
        self.user_is_online = False
    def get_ID(self):
        return self.user_ID
    def get_password(self):
        return self.user_password
    def get_email(self):
        return self.user_email
    def get_seq(self):
        return self.user_seq
    def get_ie_online(self):
        return self.user_is_online

    @st.dialog("회원가입")
    def authentication(self):
        self.user_ID = st.text_input("설정할 ID 입력")
        self.user_password = st.text_input("설정할 비밀번호 입력",type="password")
        self.user_password = st.text_input("설정할 이메일 입력")

class SignUp(UserVO):
    def __init__(self):
        super().__init__('','','')
        self.sign_up_status=False
        self.errorMessage='유효하지 않습니다. 비밀번호는 8자리 이상이어야 합니다.'
        self.signUpDate=''


    @st.dialog("회원가입")
    def sign_up_evnet(self):
        user_id=st.text_input("설정할 ID 입력")

        if user_id:
            self.user_ID=user_id
        self.user_password = st.text_input("설정할 비밀번호 입력", type="password")
        if len(self.user_password) < 8 :
            st.error(self.errorMessage)
        self.user_password = st.text_input("설정할 이메일 입력")
        a=st.button("submit",use_container_width=True)


    def validateUserInput(self):
        if len(self.user_password) >= 8 :
            return True
        elif len(self.user_password) < 8 :
            return False

    def result_event(self,valid):
        if valid == True:
            st.rerun()

    def clearSignUpData(self):
        super().uservo()








col1, col2 = st.columns(2)
col5, col6 = st.columns(2)
with col1:
    st.title("맛ZIP")
with col2:
    col3,col4 = st.columns(2)
    with col3:
        if st.button("회원가입",use_container_width=True):
            authentication=SignUp()
            authentication.sign_up_evnet()
            valid=authentication.validateUserInput()
            authentication.result_event(valid)

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

