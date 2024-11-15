import streamlit as st
import pymysql
import re
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


# 데이터베이스 연결 함수
def create_connection():
    connection = pymysql.connect(
        host='localhost',
        user='zip',
        password='12zipzip34',
        database='login',
        charset='utf8mb4'
    )
    return connection


# UserVO (사용자 정보 클래스)
class UserVO:
    def __init__(self, user_id='', user_password='', user_email='', user_seq=None, user_is_online=False):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email
        self.user_seq = user_seq
        self.user_is_online = user_is_online


# UserDAO (데이터베이스 연동 클래스)
class UserDAO:
    def insert_user(self, user):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO login (user_id, user_password, user_email) VALUES (%s, %s, %s)"
                cursor.execute(query, (user.user_id, user.user_password, user.user_email))
                connection.commit()
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    def search_user(self, user_id):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM login WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()


# SignUp (회원가입 처리 클래스)
class SignUp:
    def __init__(self, user_id, user_password, user_email):
        self.user = UserVO(user_id=user_id, user_password=user_password, user_email=user_email)

    def sign_up_event(self):
        dao = UserDAO()
        dao.insert_user(self.user)
        st.success("회원가입이 완료되었습니다!")


# UserInfoCheck (사용자 정보 체크)
class UserInfoCheck:
    @staticmethod
    def is_valid_user_info(user):
        # 아이디 유효성 검사
        if len(user.user_id) < 5:
            st.error("아이디는 5자 이상이어야 합니다.")
            return False
        # 비밀번호 유효성 검사
        if len(user.user_password) < 8:
            st.error("비밀번호는 8자 이상이어야 합니다.")
            return False
        # 이메일 유효성 검사
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', user.user_email):
            st.error("유효한 이메일 주소를 입력해주세요.")
            return False
        return True


# ChangeIDPW (아이디 및 비밀번호 변경 클래스)
class ChangeIDPW:
    def __init__(self, current_id, new_id, current_password, new_password):
        self.current_id = current_id
        self.new_id = new_id
        self.current_password = current_password
        self.new_password = new_password

    def update_id(self):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "UPDATE login SET user_id = %s WHERE user_id = %s AND user_password = %s"
                cursor.execute(query, (self.new_id, self.current_id, self.current_password))
                connection.commit()
                if cursor.rowcount > 0:
                    st.success("아이디가 변경되었습니다.")
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    def update_password(self):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "UPDATE login SET user_password = %s WHERE user_id = %s AND user_password = %s"
                cursor.execute(query, (self.new_password, self.current_id, self.current_password))
                connection.commit()
                if cursor.rowcount > 0:
                    st.success("비밀번호가 변경되었습니다.")
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()


# ForgetIDPW (비밀번호 복구 클래스)
class ForgetIDPW:
    def __init__(self, email):
        self.email = email
        self.recovery_token = ''
        self.token_expiry = None

    def generate_recovery_token(self):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self.recovery_token = token
        self.token_expiry = time.time() + 3600  # 1시간 유효
        return token

    def send_recovery_email(self):
        if not self.email:
            st.error("이메일이 설정되지 않았습니다.")
            return

        token = self.generate_recovery_token()
        subject = "비밀번호 복구 요청"
        body = f"복구 토큰: {token}\n1시간 동안 유효합니다."

        msg = MIMEMultipart()
        msg['From'] = 'your_email@example.com'
        msg['To'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('your_email@example.com', 'your_password')
                text = msg.as_string()
                server.sendmail(msg['From'], msg['To'], text)
            st.success(f"복구 이메일이 {self.email}로 전송되었습니다.")
        except Exception as e:
            st.error(f"이메일 전송에 실패했습니다: {e}")

    def verify_token(self, entered_token):
        if self.recovery_token == entered_token and time.time() < self.token_expiry:
            return True
        return False


# UserSearch (사용자 검색)
class UserSearch:
    def __init__(self, user_id):
        self.user_id = user_id

    def user_searched_event(self):
        dao = UserDAO()
        result = dao.search_user(self.user_id)
        if result:
            st.success(f"사용자 {self.user_id}를 찾았습니다.")
            return True
        else:
            st.error("사용자가 존재하지 않습니다.")
            return False


# SignIn (로그인 처리 클래스)
class SignIn:
    def __init__(self, user_id, user_password):
        self.user_id = user_id
        self.user_password = user_password

    def sign_in_event(self):
        dao = UserDAO()
        result = dao.search_user(self.user_id)
        if result and result[1] == self.user_password:
            st.success("로그인 성공")
            return True
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")
            return False


# SignOut (로그아웃 처리 클래스)
class SignOut:
    def __init__(self):
        pass

    def sign_out_event(self):
        st.success("로그아웃 되었습니다.")
        st.experimental_rerun()


# Streamlit UI 구성

# 페이지 선택
page = st.sidebar.selectbox("페이지 선택", ["회원가입", "로그인", "아이디 변경", "비밀번호 변경", "비밀번호 복구"])

# 회원가입 페이지
if page == "회원가입":
    st.title("회원가입")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')
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
    user_password = st.text_input("비밀번호", type='password')

    if st.button("로그인"):
        sign_in = SignIn(user_id, user_password)

