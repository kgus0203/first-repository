import streamlit as st
import pymysql
import bcrypt


# 데이터베이스 연결 함수
def create_connection():
    connection = pymysql.connect(
        host='192.168.0.48',
        user='zip',  # MySQL 사용자 계정
        password='12zipzip34',  # MySQL 비밀번호
        database='zip',  # 데이터베이스 이름
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
    # 아이디 중복 체크
    def check_user_id_exists(self, user_id):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM user WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result is not None
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    # 아이디로 사용자 검색
    def search_user(self, user_id):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM user WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    # 비밀번호 해싱 및 사용자 추가
    def insert_user(self, user):
        connection = create_connection()

        # 비밀번호 해싱 (bcrypt 사용)
        hashed_password = bcrypt.hashpw(user.user_password.encode('utf-8'), bcrypt.gensalt())

        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO user (user_id, user_password, user_email) VALUES (%s, %s, %s)"
                cursor.execute(query, (user.user_id, hashed_password.decode('utf-8'), user.user_email))
                connection.commit()
        except pymysql.MySQLError as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    # 비밀번호 체크 (bcrypt로 비교)
    def check_password(self, hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# 회원가입 처리 클래스
class SignUp:
    def __init__(self, user_id, user_password, user_email):
        self.user = UserVO(user_id=user_id, user_password=user_password, user_email=user_email)

    def sign_up_event(self):
        dao = UserDAO()

        # 아이디 중복 체크
        if dao.check_user_id_exists(self.user.user_id):
            st.error("이미 사용 중인 아이디입니다.")
            return

        dao.insert_user(self.user)
        st.success("회원가입이 완료되었습니다!")


# 로그인 처리 클래스
class SignIn:
    def __init__(self, user_id, user_password):
        self.user_id = user_id
        self.user_password = user_password

    def sign_in_event(self):
        dao = UserDAO()
        result = dao.search_user(self.user_id)

        if result:
            # 저장된 해시된 비밀번호 가져오기
            stored_hashed_password = result[1]  # result[1]은 해싱된 비밀번호
            if dao.check_password(stored_hashed_password, self.user_password):  # bcrypt로 비밀번호 비교
                st.success("로그인 성공")
                return True
            else:
                st.error("비밀번호가 잘못되었습니다.")
        else:
            st.error("아이디가 존재하지 않습니다.")
        return False


# Streamlit UI 구성

# 페이지 선택
page = st.sidebar.selectbox("페이지 선택", ["회원가입", "로그인"])

# 회원가입 페이지
if page == "회원가입":
    st.title("회원가입")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')
    email = st.text_input("이메일")

    if st.button("회원가입"):
        user_info = UserVO(user_id=user_id, user_password=user_password, user_email=email)
        signup = SignUp(user_id, user_password, email)
        signup.sign_up_event()

# 로그인 페이지
elif page == "로그인":
    st.title("로그인")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')

    if st.button("로그인"):
        sign_in = SignIn(user_id, user_password)
        sign_in.sign_in_event()
