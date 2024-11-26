import pandas as pd
import streamlit as st
import sqlite3
import bcrypt
import pages

# 데이터베이스 연결 함수
def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형식으로 반환
    return conn


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
            cursor = connection.cursor()
            query = "SELECT * FROM user WHERE user_id = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    # 아이디로 사용자 검색
    def search_user(self, user_id):
        connection = create_connection()
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM user WHERE user_id = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    # 비밀번호 해싱 및 사용자 추가
    def insert_user(self, user):
        connection = create_connection()

        # 비밀번호 해싱 (bcrypt 사용)
        hashed_password = bcrypt.hashpw(user.user_password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor = connection.cursor()
            query = "INSERT INTO user (user_id, user_password, user_email, user_is_online) VALUES (?, ?, ?, 0)"
            cursor.execute(query, (user.user_id, hashed_password, user.user_email))
            connection.commit()
        except sqlite3.IntegrityError as e:  # UNIQUE 제약 조건으로 발생하는 오류 처리
            if "user_email" in str(e):
                st.error("이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.")
            elif "user_id" in str(e):
                st.error("이미 사용 중인 아이디입니다. 다른 아이디를 사용해주세요.")
            else:
                st.error("회원가입 중 알 수 없는 오류가 발생했습니다.")
            return  # 예외 발생 시 함수 종료
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return  # 예외 발생 시 함수 종료
        finally:
            connection.close()

        # 회원가입 성공 메시지 (오류가 없을 경우에만 실행)
        st.success("회원가입이 완료되었습니다!")
        pages.change_page('Login')

    # 비밀번호 체크 (bcrypt로 비교)
    def check_password(self, hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def insert_user(self, user):
    connection = create_connection()



    # 비밀번호 해싱 (bcrypt 사용)
    hashed_password = bcrypt.hashpw(user.user_password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor = connection.cursor()
        query = "INSERT INTO user (user_id, user_password, user_email, user_is_online) VALUES (?, ?, ?, 0)"
        cursor.execute(query, (user.user_id, hashed_password, user.user_email))
        connection.commit()
    except sqlite3.IntegrityError as e:  # UNIQUE 제약 조건으로 발생하는 오류 처리
        if "user_email" in str(e):
            st.error("이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.")
        elif "user_id" in str(e):
            st.error("이미 사용 중인 아이디입니다. 다른 아이디를 사용해주세요.")
        else:
            st.error("회원가입 중 알 수 없는 오류가 발생했습니다.")
        return  # 예외 발생 시 함수 종료
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
        return  # 예외 발생 시 함수 종료
    finally:
        connection.close()

    # 회원가입 성공 메시지 (오류가 없을 경우에만 실행)
    st.success("회원가입이 완료되었습니다!")


    # 비밀번호 체크 (bcrypt로 비교)
    def check_password(self, hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# 회원가입 처리 클래스
class SignUp:
    def __init__(self, user_id, user_password, user_email):
        self.user = UserVO(user_id=user_id, user_password=user_password, user_email=user_email)

    def sign_up_event(self):
        dao = UserDAO()

        # 사용자 추가 (모든 예외 처리는 insert_user에서 처리)
        dao.insert_user(self.user)

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
            stored_hashed_password = result['user_password']  # result는 딕셔너리 형태
            if dao.check_password(stored_hashed_password, self.user_password):  # bcrypt로 비밀번호 비교
                st.session_state["user_id"] = self.user_id  # 로그인 성공 시 세션에 user_id 저장
                pages.change_page('after_login')
                return True
            else:
                st.error("비밀번호가 잘못되었습니다.")
        else:
            st.error("아이디가 존재하지 않습니다.")
        return False
