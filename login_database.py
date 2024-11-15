import pymysql
import streamlit as st
import re
from pymysql import MySQLError
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import random

def create_connection():
    connection = pymysql.connect(
        host='172.20.10.12',
        user='zip',
        password='12zipzip34',
        database='login',
        charset='utf8mb4'
    )
    return connection

class ChangeIDPW:
    def __init__(self):
        self.current_id = ''
        self.new_id = ''
        self.current_password = ''
        self.new_password = ''

    # 아이디 변경 함수
    def update_id(self, current_id, new_id):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    UPDATE login 
                    SET user_id = %s
                    WHERE user_id = %s
                """
                cursor.execute(query, (new_id, current_id))
                connection.commit()
        except Exception as e:
            print(f"아이디를 수정할 수 없습니다.: {e}")
        finally:
            connection.close()

    # 비밀번호 변경 함수
    def update_password(self, current_password, new_password):
        validation_result = self.validate_new_id_password(current_password, new_password)
        if validation_result is not None:
            st.warning(validation_result)
            return

        connection = create_connection()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                query = """
                    UPDATE login 
                    SET user_password = %s
                    WHERE user_password = %s
                """
                cursor.execute(query, (new_password, current_password))
                connection.commit()

                # 비밀번호 변경이 적용된 행의 수가 0이면, 현재 비밀번호가 일치하지 않는 것
                if cursor.rowcount == 0:
                    st.warning("현재 비밀번호가 일치하지 않습니다.")
                else:
                    st.success("비밀번호가 성공적으로 변경되었습니다!")

        except MySQLError as e:
            st.error(f"비밀번호를 변경할 수 없습니다.: {e}")
        finally:
            connection.close()

    # 비밀번호 유효성 검사 함수
    def validate_new_id_password(self, current_password, new_password):
        # 1. 비밀번호 길이 검사 (최소 8자, 최대 20자)
        if len(new_password) < 8 or len(new_password) > 20:
            return "비밀번호는 최소 8자, 최대 20자여야 합니다."

        # 2. 대문자 포함 검사
        if not re.search(r'[A-Z]', new_password):
            return "비밀번호는 최소한 하나의 대문자를 포함해야 합니다."

        # 3. 소문자 포함 검사
        if not re.search(r'[a-z]', new_password):
            return "비밀번호는 최소한 하나의 소문자를 포함해야 합니다."

        # 4. 숫자 포함 검사
        if not re.search(r'\d', new_password):
            return "비밀번호는 최소한 하나의 숫자를 포함해야 합니다."

        # 5. 특수 문자 포함 검사 (특수 문자는 !@#$%^&*() 등)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            return "비밀번호는 최소한 하나의 특수 문자를 포함해야 합니다."

        # 6. 현재 비밀번호와 동일한지 확인
        if current_password == new_password:
            return "새로운 비밀번호는 현재 비밀번호와 달라야 합니다."

        return None  # 모든 검증 통과 시 None 반환


class ForgotIDPW:
    def __init__(self):
        self.email = ''  # 복구를 위한 이메일
        self.recovery_token = ''  # 고유 복구 토큰
        self.token_expiry = None  # 복구 토큰의 만료 시간
        self.is_recovered = False  # 비밀번호가 성공적으로 변경되었는지 여부

    def generate_recovery_token(self):
        """
        고유한 복구 토큰을 생성합니다.
        """
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # 16자리 랜덤 문자열
        self.recovery_token = token
        self.token_expiry = time.time() + 3600  # 토큰은 1시간 동안 유효 (3600초)
        return token

    def send_recovery_email(self):
        """
        사용자의 이메일로 복구 토큰을 보내는 메서드입니다.
        실제 이메일 전송을 위해 SMTP 서버 설정이 필요합니다.
        """
        if not self.email:
            raise ValueError("이메일이 설정되지 않았습니다.")

        token = self.generate_recovery_token()

        # 이메일 설정
        subject = "아이디/비밀번호 복구 요청"
        body = f"복구 토큰: {token}\n복구 토큰은 1시간 동안 유효합니다."

        msg = MIMEMultipart()
        msg['From'] = 'your_email@example.com'
        msg['To'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # SMTP 서버로 이메일 전송
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('your_email@example.com', 'your_password')  # SMTP 로그인 정보
                text = msg.as_string()
                server.sendmail(msg['From'], msg['To'], text)
            st.success(f"복구 이메일이 {self.email}로 전송되었습니다.")
        except Exception as e:
            st.error(f"이메일 전송에 실패했습니다: {e}")

    def verify_token(self, entered_token):
        """
        사용자가 입력한 복구 토큰을 검증하는 메서드입니다.
        """
        if self.recovery_token == entered_token and time.time() < self.token_expiry:
            return True
        return False

    def reset_password(self, new_password):
        """
        사용자가 복구 토큰을 통해 비밀번호를 변경하는 메서드입니다.
        비밀번호를 새로 설정하고, DB에 업데이트합니다.
        """
        # 비밀번호 유효성 검사 (필요한 경우 추가)
        if len(new_password) < 8:
            st.error("비밀번호는 최소 8자 이상이어야 합니다.")
            return

        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                query = "UPDATE login SET user_password = %s WHERE user_email = %s"
                cursor.execute(query, (new_password, self.email))
                connection.commit()

                if cursor.rowcount > 0:
                    self.is_recovered = True
                    st.success("비밀번호가 성공적으로 변경되었습니다!")
                else:
                    st.warning("해당 이메일을 찾을 수 없습니다.")
        except pymysql.MySQLError as e:
            st.error(f"비밀번호 변경에 실패했습니다: {e}")
        finally:
            connection.close()

    def recover_password(self, entered_token, new_password):
        """
        비밀번호 복구를 위한 메서드입니다.
        복구 토큰이 유효한지 검증하고, 비밀번호를 새로 설정합니다.
        """
        if self.verify_token(entered_token):
            self.reset_password(new_password)
        else:
            st.error("유효하지 않거나 만료된 복구 토큰입니다.")

class UserVO:
    def __init__(self, user_id='', user_password='', user_email='', user_seq=None, user_is_online=False):
        """
        사용자 정보를 초기화하는 생성자
        :param user_id: 사용자 ID
        :param user_password: 사용자 비밀번호
        :param user_email: 사용자 이메일
        :param user_seq: 사용자 고유 번호 (시퀀스)
        :param user_is_online: 온라인 상태 (True: 온라인, False: 오프라인)
        """
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email
        self.user_seq = user_seq
        self.user_is_online = user_is_online

    def get_ID(self):
        """
        사용자 ID를 반환합니다.
        """
        return self.user_id

    def set_ID(self, user_id):
        """
        사용자 ID를 설정합니다.
        :param user_id: 설정할 사용자 ID
        """
        self.user_id = user_id

    def set_password(self, user_password):
        """
        사용자 비밀번호를 설정합니다.
        :param user_password: 설정할 사용자 비밀번호
        """
        self.user_password = user_password

    def get_email(self):
        """
        사용자 이메일을 반환합니다.
        """
        return self.user_email

    def get_seq(self):
        """
        사용자 고유 번호(시퀀스)를 반환합니다.
        """
        return self.user_seq

    def get_is_online(self):
        """
        사용자의 온라인 상태를 반환합니다.
        """
        return self.user_is_online

    def set_is_online(self, is_online):
        """
        사용자의 온라인 상태를 설정합니다.
        :param is_online: 사용자 온라인 상태 (True: 온라인, False: 오프라인)
        """
        self.user_is_online = is_online

    def __repr__(self):
        """
        UserVO 객체를 출력할 때 사용자 정보를 반환하는 메서드입니다.
        """
        return f"UserVO(user_id={self.user_id}, user_email={self.user_email}, user_is_online={self.user_is_online})"


class UserDAO(UserVO):
    def __init__(self, connection=None):
        """
        UserDAO 클래스의 생성자
        :param connection: DB 연결 객체 (기본값 None, 없으면 새로 생성)
        """
        self.connection = connection if connection else self.create_connection()

    def create_connection(self):
        """
        MySQL 데이터베이스에 연결을 생성하는 메서드입니다.
        :return: 연결 객체
        """
        return pymysql.connect(
            host='localhost',
            user='zip',
            password='12zipzip34',
            database='login',
            charset='utf8mb4'
        )

    def insert_db_user(self, user):
        """
        사용자 정보를 데이터베이스에 삽입하는 메서드입니다.
        :param user: UserVO 객체 (사용자 정보)
        :return: 삽입된 행의 개수
        """
        try:
            with self.connection.cursor() as cursor:
                query = """
                    INSERT INTO login (user_id, user_password, user_email, user_is_online) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user.user_id, user.user_password, user.user_email, user.user_is_online))
                self.connection.commit()
                return cursor.rowcount
        except MySQLError as e:
            print(f"DB 삽입 오류: {e}")
            return 0

    def update_db_user(self, user):
        """
        사용자 정보를 데이터베이스에서 업데이트하는 메서드입니다.
        :param user: UserVO 객체 (업데이트할 사용자 정보)
        :return: 업데이트된 행의 개수
        """
        try:
            with self.connection.cursor() as cursor:
                query = """
                    UPDATE login
                    SET user_id = %s, user_password = %s, user_email = %s, user_is_online = %s
                    WHERE user_seq = %s
                """
                cursor.execute(query,
                               (user.user_id, user.user_password, user.user_email, user.user_is_online, user.user_seq))
                self.connection.commit()
                return cursor.rowcount
        except MySQLError as e:
            print(f"DB 업데이트 오류: {e}")
            return 0

    def delete_db_user(self, user_seq):
        """
        사용자 정보를 데이터베이스에서 삭제하는 메서드입니다.
        :param user_seq: 사용자 고유 번호 (user_seq)
        :return: 삭제된 행의 개수
        """
        try:
            with self.connection.cursor() as cursor:
                query = "DELETE FROM login WHERE user_seq = %s"
                cursor.execute(query, (user_seq,))
                self.connection.commit()
                return cursor.rowcount
        except MySQLError as e:
            print(f"DB 삭제 오류: {e}")
            return 0

    def search_db_user(self, user_id=None, user_email=None):
        """
        사용자 정보를 데이터베이스에서 검색하는 메서드입니다.
        :param user_id: (선택적) 검색할 사용자 ID
        :param user_email: (선택적) 검색할 사용자 이메일
        :return: 사용자 객체 (UserVO) 또는 None
        """
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT user_id, user_password, user_email, user_seq, user_is_online FROM login WHERE "
                conditions = []
                values = []

                if user_id:
                    conditions.append("user_id = %s")
                    values.append(user_id)
                if user_email:
                    conditions.append("user_email = %s")
                    values.append(user_email)

                if not conditions:
                    return None  # 검색 조건이 없으면 None 반환

                query += " AND ".join(conditions)

                cursor.execute(query, tuple(values))
                result = cursor.fetchone()

                if result:
                    return UserVO(user_id=result[0], user_password=result[1], user_email=result[2], user_seq=result[3],
                                  user_is_online=result[4])
                else:
                    return None
        except MySQLError as e:
            print(f"DB 검색 오류: {e}")
            return None

    def is_valid_user(self, user_id, password):
        """
        사용자 ID와 비밀번호가 유효한지 확인하는 메서드입니다.
        :param user_id: 사용자 ID
        :param password: 사용자 비밀번호
        :return: 유효하면 True, 아니면 False
        """
        user = self.search_db_user(user_id=user_id)
        if user and user.user_password == password:
            return True
        return False

    def generate_seq(self):
        """
        새로운 사용자 시퀀스를 생성하는 메서드입니다.
        :return: 새로운 사용자 시퀀스
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(user_seq) FROM login")
                result = cursor.fetchone()
                return result[0] + 1 if result[0] else 1
        except MySQLError as e:
            print(f"시퀀스 생성 오류: {e}")
            return None

    def update_user_id(self, current_id, new_id):
        """
        사용자 ID를 변경하는 메서드입니다.
        :param current_id: 현재 사용자 ID
        :param new_id: 새 사용자 ID
        :return: 변경된 행의 개수
        """
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE login SET user_id = %s WHERE user_id = %s"
                cursor.execute(query, (new_id, current_id))
                self.connection.commit()
                return cursor.rowcount
        except MySQLError as e:
            print(f"DB 업데이트 오류: {e}")
            return 0

    def update_user_password(self, current_password, new_password, user_id):
        """
        사용자 비밀번호를 변경하는 메서드입니다.
        :param current_password: 현재 비밀번호
        :param new_password: 새 비밀번호
        :param user_id: 사용자 ID
        :return: 변경된 행의 개수
        """
        if not self.is_valid_user(user_id, current_password):
            print("현재 비밀번호가 잘못되었습니다.")
            return 0

        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE login SET user_password = %s WHERE user_id = %s"
                cursor.execute(query, (new_password, user_id))
                self.connection.commit()
                return cursor.rowcount
        except MySQLError as e:
            print(f"DB 업데이트 오류: {e}")
            return 0


class SignUp(UserVO):
    def __init__(self):
        """
        SignUp 클래스 초기화. 사용자 정보 및 가입 상태 초기화.
        """
        super().__init__()
        self.sign_up_user = None  # 회원가입하려는 사용자 (UserVO 객체)
        self.sign_up_status = False  # 회원가입 성공 여부
        self.errorMessage = ''  # 에러 메시지
        self.signUpDate = None  # 회원가입 날짜

    def sign_up_event(self, user):
        """
        회원가입 이벤트 처리. 회원가입 성공 여부를 결정하고, 필요한 정보를 초기화합니다.
        :param user: UserVO 객체
        """
        self.sign_up_user = user

        # 입력된 사용자 정보 유효성 검사
        if not self.validate_user_input(user):
            self.sign_up_status = False
            return

        # 사용자 정보 데이터베이스에 저장
        if self.insert_user_to_db(user):
            self.sign_up_status = True
            self.send_confirmation_email(user)
            self.signUpDate = self.get_current_time()
        else:
            self.sign_up_status = False

    def result_event(self):
        """
        회원가입 결과를 반환합니다. 성공하거나 실패한 메시지를 반환.
        :return: 회원가입 성공/실패 메시지
        """
        if self.sign_up_status:
            return f"회원가입이 성공적으로 완료되었습니다. 가입일: {self.signUpDate}"
        else:
            return f"회원가입 실패. {self.errorMessage}"

    def validate_user_input(self, user):
        """
        회원가입 입력 정보를 유효성 검증합니다.
        :param user: UserVO 객체 (회원가입하려는 사용자)
        :return: 유효성 검사 결과 (True/False)
        """
        # 1. 이메일 유효성 검사
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, user.user_email):
            self.errorMessage = "유효하지 않은 이메일 주소입니다."
            return False

        # 2. 비밀번호 길이 검사 (최소 8자 이상)
        if len(user.user_password) < 8:
            self.errorMessage = "비밀번호는 최소 8자 이상이어야 합니다."
            return False

        # 3. 비밀번호 확인 (확인 비밀번호가 필요하다면 추가로 체크)
        # 4. 중복 이메일 및 아이디 체크
        if not self.is_email_unique(user.user_email):
            self.errorMessage = "이메일이 이미 존재합니다."
            return False

        if not self.is_user_id_unique(user.user_id):
            self.errorMessage = "사용자 ID가 이미 존재합니다."
            return False

        return True

    def send_confirmation_email(self, user):
        """
        회원가입 후 사용자에게 확인 이메일을 전송하는 메서드입니다.
        :param user: UserVO 객체
        """
        try:
            # 이메일 설정
            subject = "회원가입 확인 이메일"
            body = f"안녕하세요, {user.user_id}님! 회원가입이 성공적으로 완료되었습니다."

            msg = MIMEMultipart()
            msg['From'] = 'your_email@example.com'
            msg['To'] = user.user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # SMTP 서버로 이메일 전송
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('your_email@example.com', 'your_password')  # SMTP 로그인 정보
                text = msg.as_string()
                server.sendmail(msg['From'], msg['To'], text)
            print(f"회원가입 확인 이메일이 {user.user_email}로 전송되었습니다.")
        except Exception as e:
            print(f"이메일 전송에 실패했습니다: {e}")

    def is_email_unique(self, email):
        """
        이메일이 이미 데이터베이스에 존재하는지 확인합니다.
        :param email: 사용자 이메일
        :return: 이메일이 유니크한지 여부
        """
        connection = pymysql.connect(host='localhost', user='zip', password='12zipzip34', database='login',
                                     charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM login WHERE user_email = %s", (email,))
                result = cursor.fetchone()
                return result[0] == 0  # 0이면 유니크, 1이면 이미 존재
        except pymysql.MySQLError as e:
            print(f"DB 오류: {e}")
            return False
        finally:
            connection.close()

    def is_user_id_unique(self, user_id):
        """
        사용자 ID가 데이터베이스에 이미 존재하는지 확인합니다.
        :param user_id: 사용자 ID
        :return: ID가 유니크한지 여부
        """
        connection = pymysql.connect(host='localhost', user='zip', password='12zipzip34', database='login',
                                     charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM login WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result[0] == 0  # 0이면 유니크, 1이면 이미 존재
        except pymysql.MySQLError as e:
            print(f"DB 오류: {e}")
            return False
        finally:
            connection.close()

    def insert_user_to_db(self, user):
        """
        유효성 검사를 통과한 사용자 정보를 데이터베이스에 삽입하는 메서드입니다.
        :param user: UserVO 객체 (회원가입하려는 사용자)
        :return: 삽입 성공 여부 (True/False)
        """
        connection = pymysql.connect(host='localhost', user='zip', password='12zipzip34', database='login',
                                     charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO login (user_id, user_password, user_email, user_is_online)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user.user_id, user.user_password, user.user_email, user.user_is_online))
                connection.commit()
                return cursor.rowcount > 0  # 성공 시 True, 실패 시 False
        except pymysql.MySQLError as e:
            print(f"DB 삽입 오류: {e}")
            return False
        finally:
            connection.close()

    def clear_signup_data(self):
        """
        회원가입 후 객체 내 데이터(UserVO) 초기화
        """
        self.sign_up_user = None
        self.sign_up_status = False
        self.errorMessage = ''
        self.signUpDate = None

    def get_current_time(self):
        """
        현재 시간을 가져오는 메서드입니다.
        :return: 현재 시간 (YYYY-MM-DD HH:MM:SS)
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class UserInfoCheck(UserVO, UserDAO):
    def __init__(self, user: UserVO):
        super().__init__(user.user_id, user.user_password, user.user_email, user.user_seq, user.user_is_online)
        self.user = user

    def essential_user_info_check(self):
        """
        사용자의 필수 항목이 모두 채워져 있는지 확인합니다.
        :return: 필수 정보가 모두 입력된 경우 True, 아니면 False
        """
        if not self.user.user_id or not self.user.user_password or not self.user.user_email:
            return False
        return True

    def existing_user_overlap_check(self):
        """
        데이터베이스 내에 중복된 사용자가 있는지 확인합니다.
        :return: 중복된 사용자 존재 시 True, 아니면 False
        """
        connection = pymysql.connect(host='localhost', user='zip', password='12zipzip34', database='login', charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                # 이메일과 사용자 ID가 중복되는지 체크
                cursor.execute("SELECT COUNT(*) FROM login WHERE user_id = %s OR user_email = %s", (self.user.user_id, self.user.user_email))
                result = cursor.fetchone()
                return result[0] > 0  # 중복된 사용자가 존재하면 True
        except pymysql.MySQLError as e:
            print(f"DB 오류: {e}")
            return False
        finally:
            connection.close()

    def password_check(self):
        """
        비밀번호가 유효한지 확인합니다. 비밀번호는 최소 8자 이상이어야 하고, 숫자, 대문자, 소문자, 특수문자가 포함되어야 합니다.
        :return: 비밀번호가 유효하면 True, 아니면 False
        """
        password = self.user.user_password

        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):  # 대문자 포함 확인
            return False
        if not re.search(r'[a-z]', password):  # 소문자 포함 확인
            return False
        if not re.search(r'\d', password):  # 숫자 포함 확인
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # 특수문자 포함 확인
            return False

        return True

    def is_online_check(self):
        """
        사용자가 온라인 상태인지 확인합니다.
        :return: 온라인 상태이면 True, 아니면 False
        """
        return self.user.user_is_online

    def email_auth(self):
        """
        사용자의 이메일 인증 상태를 확인합니다.
        :return: 이메일이 인증된 상태면 True, 아니면 False
        """
        # 이메일 인증 상태를 확인하는 DB 쿼리 (여기선 예시로 이메일 인증 여부 컬럼을 user_email_verified로 가정)
        connection = pymysql.connect(host='localhost', user='zip', password='12zipzip34', database='login', charset='utf8mb4')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_email_verified FROM login WHERE user_email = %s", (self.user.user_email,))
                result = cursor.fetchone()
                if result and result[0] == 1:  # 1이면 이메일 인증됨
                    return True
                return False
        except pymysql.MySQLError as e:
            print(f"DB 오류: {e}")
            return False
        finally:
            connection.close()


class UserSearch(UserVO):
    def __init__(self):
        # 검색된 사용자 정보를 저장할 변수
        self.searched_user = None

    def user_searched_event(self, search_term):
        """
        사용자가 입력한 검색 기준에 맞는 사용자를 데이터베이스에서 검색합니다.
        :param search_term: 검색 기준 (ID 또는 이메일)
        :return: 검색 성공 여부
        """
        connection = pymysql.connect(host='localhost', user='zip', password='12zipzip34', database='login',
                                     charset='utf8mb4')

        try:
            with connection.cursor() as cursor:
                # 사용자 ID나 이메일로 검색할 수 있도록 쿼리
                query = """
                    SELECT user_id, user_email, user_is_online, user_seq 
                    FROM login 
                    WHERE user_id = %s OR user_email = %s
                """
                cursor.execute(query, (search_term, search_term))
                result = cursor.fetchone()

                if result:
                    # 검색된 사용자 정보가 있으면 UserVO 객체에 저장
                    self.searched_user = UserVO(user_id=result[0], user_email=result[1], user_is_online=result[2],
                                                user_seq=result[3])
                    return True  # 검색 성공
                else:
                    self.searched_user = None
                    return False  # 검색 실패
        except pymysql.MySQLError as e:
            print(f"DB 오류: {e}")
            return False
        finally:
            connection.close()

    def get_searched_user(self):
        """
        검색된 사용자 정보를 반환합니다.
        :return: 검색된 사용자 정보 (UserVO 객체)
        """
        return self.searched_user

    def result_event(self):
        """
        검색 결과를 출력합니다.
        검색된 사용자가 있으면 사용자 정보 출력, 없으면 오류 메시지 출력
        """
        if self.searched_user:
            # 검색된 사용자 정보 출력
            print(f"사용자 ID: {self.searched_user.user_id}")
            print(f"사용자 이메일: {self.searched_user.user_email}")
            print(f"온라인 상태: {'온라인' if self.searched_user.user_is_online else '오프라인'}")
            print(f"사용자 고유 번호: {self.searched_user.user_seq}")
        else:
            print("검색된 사용자가 없습니다.")
