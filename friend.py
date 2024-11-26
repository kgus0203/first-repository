import sqlite3
import streamlit as st

# 데이터베이스 연결 함수
def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형식으로 반환
    return conn


# UserVO (사용자 정보 클래스)
class UserVO:
    def __init__(self, user_id='', user_password='', user_email='', user_seq=None, user_is_online=False, user_mannerscore=0):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email
        self.user_seq = user_seq
        self.user_is_online = user_is_online
        self.user_mannerscore = user_mannerscore  # 매너 점수


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

    # 사용자 추가
    def insert_user(self, user):
        connection = create_connection()
        try:
            cursor = connection.cursor()
            query = "INSERT INTO user (user_id, user_password, user_email, user_is_online, user_mannerscore) VALUES (?, ?, ?, 0, 0)"
            cursor.execute(query, (user.user_id, user.user_password, user.user_email))
            connection.commit()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    # 비밀번호 체크 (비밀번호 해시하지 않음)
    def check_password(self, stored_password, plain_password):
        return stored_password == plain_password


# 로그인 처리 클래스
class SignIn:
    def __init__(self, user_id, user_password):
        self.user_id = user_id
        self.user_password = user_password

    def sign_in_event(self):
        dao = UserDAO()
        result = dao.search_user(self.user_id)

        if result:
            # 저장된 비밀번호 가져오기
            stored_password = result['user_password']  # result는 딕셔너리 형태
            if dao.check_password(stored_password, self.user_password):  # 비밀번호 비교
                st.success("로그인 성공")
                return self.user_id
            else:
                st.error("비밀번호가 잘못되었습니다.")
        else:
            st.error("아이디가 존재하지 않습니다.")
        return False


# 친구 목록 조회
def get_friends(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        query = """
        SELECT u.user_id, u.user_email, u.user_is_online, u.user_mannerscore
        FROM user u
        JOIN friend f ON u.user_id = f.friend_user_id
        WHERE f.user_id = ? AND f.status = 'accepted'
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


# 친구와 매너 점수 표시
def show_friends(user_id):
    friends = get_friends(user_id)

    st.title("친구 목록")
    if not friends:
        st.write("친구가 없습니다.")
    else:
        for friend in friends:
            online_status = "온라인" if friend['user_is_online'] == 1 else "오프라인"
            manner_score = friend['user_mannerscore']
            st.write(f"**친구 ID**: {friend['user_id']} ({online_status})")
            st.write(f"**이메일**: {friend['user_email']}")
            st.write(f"**매너 점수**: {manner_score}")
            st.write("---")


# 친구 팔로우 함수
def follow_friend(user_id, friend_user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 친구 요청 상태 추가 (pending 상태로 저장)
        query = "INSERT INTO friend (user_id, friend_user_id, status) VALUES (?, ?, 'pending')"
        cursor.execute(query, (user_id, friend_user_id))
        conn.commit()
        st.success(f"{friend_user_id}님에게 팔로우 요청을 보냈습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


# 친구 요청을 확인하고, 수락 / 거절하는 함수
def get_follow_requests(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        query = """
        SELECT f.user_id, f.friend_user_id
        FROM friend f
        WHERE f.friend_user_id = ? AND f.status = 'pending'
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


# 친구 요청 수락 / 거절
def handle_follow_request(user_id, friend_user_id, action):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        if action == "accept":
            query = "UPDATE friend SET status = 'accepted' WHERE user_id = ? AND friend_user_id = ?"
        elif action == "reject":
            query = "UPDATE friend SET status = 'rejected' WHERE user_id = ? AND friend_user_id = ?"
        cursor.execute(query, (user_id, friend_user_id))
        conn.commit()

        if action == "accept":
            st.success(f"{friend_user_id}님을 친구로 수락하였습니다.")
        else:
            st.success(f"{friend_user_id}님을 친구 요청을 거절하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


# 메인 페이지
def main():
    # 로그인
    user_id = login()

    if user_id:
        # 로그인 성공 후 친구 목록 보기
        show_friends(user_id)

        # 친구 팔로우 입력
        friend_user_id = st.text_input("팔로우할 친구의 사용자 ID 입력:")
        if st.button("친구 팔로우"):
            if friend_user_id:
                follow_friend(user_id, friend_user_id)
            else:
                st.error("친구의 사용자 ID를 입력해 주세요.")

        # 친구 요청 보기 및 수락 / 거절
        requests = get_follow_requests(user_id)
        if requests:
            st.title("친구 요청 목록")
            for request in requests:
                st.write(f"**{request['user_id']}님**으로부터 팔로우 요청이 왔습니다.")
                accept_button = st.button(f"수락 {request['user_id']}")
                reject_button = st.button(f"거절 {request['user_id']}")

                if accept_button:
                    handle_follow_request(user_id, request['user_id'], "accept")
                elif reject_button:
                    handle_follow_request(user_id, request['user_id'], "reject")
        else:
            st.write("팔로우 요청이 없습니다.")
    else:
        st.warning("로그인 후 사용해 주세요.")


# 로그인 페이지
def login():
    page = st.sidebar.selectbox("페이지 선택", ["로그인", "회원가입"])

    if page == "회원가입":
        st.title("회원가입")
        user_id = st.text_input("아이디")
        user_password = st.text_input("비밀번호", type='password')
        email = st.text_input("이메일")

        if st.button("회원가입"):
            # 입력 값 검증 (간단한 예시)
            if not user_id or not user_password or not email:
                st.error("모든 필드를 입력해 주세요.")
            else:
                user_info = UserVO(user_id=user_id, user_password=user_password, user_email=email)
                signup = SignUp(user_id, user_password, email)
                signup.sign_up_event()

    elif page == "로그인":
        st.title("로그인")
        user_id = st.text_input("아이디")
        user_password = st.text_input("비밀번호", type='password')

        if st.button("로그인"):
            # 입력 값 검증
            if not user_id or not user_password:
                st.error("아이디와 비밀번호를 입력해 주세요.")
            else:
                sign_in = SignIn(user_id, user_password)
                return sign_in.sign_in_event()

    return None


if __name__ == "__main__":
    main()
