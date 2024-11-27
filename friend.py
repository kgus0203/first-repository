import sqlite3
import streamlit as st


# 데이터베이스 연결 함수
def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
    return conn

# 내 친구 리스트 기능
def show_friend_list(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT friend_user_id FROM friend WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        friends = cursor.fetchall()
        if friends:
            st.title("내 친구 리스트")
            for friend in friends:
                st.write(f"- {friend['friend_user_id']}")
        else:
            st.write("친구가 없습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 친구 추가 기능
def add_friend(user_id, friend_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 상대방이 회원가입했는지 확인
        query = "SELECT user_id FROM user WHERE user_id = ?"
        cursor.execute(query, (friend_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            st.error("없는 ID입니다.")
            return

        # 중복 신청 방지
        query = """
            SELECT * FROM myFriendrequest 
            WHERE user_id = ? AND requested_user_id = ?
        """
        cursor.execute(query, (user_id, friend_id))
        already_requested = cursor.fetchone()

        if already_requested:
            st.error("이미 친구 신청을 보냈습니다.")
            return

        # 친구 신청 추가 (양방향 대기)
        cursor.execute("INSERT INTO myFriendrequest (user_id, requested_user_id) VALUES (?, ?)", (user_id, friend_id))
        cursor.execute("INSERT INTO otherRequest (user_id, requester_user_id) VALUES (?, ?)", (friend_id, user_id))
        conn.commit()
        st.success(f"{friend_id}님에게 친구 신청을 보냈습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
   
        # 삽입 후 데이터베이스 확인
        cursor.execute("SELECT * FROM myFriendrequest WHERE user_id = ? AND requested_user_id = ?", (user_id, friend_id))
        my_request_check = cursor.fetchall()
        cursor.execute("SELECT * FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (friend_id, user_id))
        other_request_check = cursor.fetchall()

        # 디버깅용 로그 출력
        st.write(f"myFriendrequest 데이터: {my_request_check}")
        st.write(f"otherRequest 데이터: {other_request_check}")

        st.success(f"{friend_id}님에게 친구 신청을 보냈습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 친구 차단 기능
def block_friend(user_id, friend_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 친구 리스트에서 삭제 및 차단 리스트로 이동
        cursor.execute("DELETE FROM friend WHERE user_id = ? AND friend_user_id = ?", (user_id, friend_id))
        cursor.execute("INSERT INTO block (user_id, blocked_user_id) VALUES (?, ?)", (user_id, friend_id))
        conn.commit()
        st.success(f"{friend_id}님을 차단하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 차단 해제 기능
def unblock_friend(user_id, friend_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 차단 리스트에서 삭제 및 친구 리스트로 이동
        cursor.execute("DELETE FROM block WHERE user_id = ? AND blocked_user_id = ?", (user_id, friend_id))
        cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (user_id, friend_id))
        conn.commit()
        st.success(f"{friend_id}님을 차단 해제하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 친구 대기 기능

def handle_follow_request(user_id, requester_id, action):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        if action == "accept":
            # 친구 요청을 수락 (친구 목록에 추가)
            cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (user_id, requester_id))
            cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (requester_id, user_id))
            # 요청 삭제
            cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (user_id, requester_id))
            conn.commit()
            st.success(f"{requester_id}님과 친구가 되었습니다.")
        elif action == "reject":
            # 친구 요청을 거절 (요청 삭제)
            cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (user_id, requester_id))
            conn.commit()
            st.success(f"{requester_id}님의 요청을 거절하였습니다.")
        else:
            st.error("올바르지 않은 작업입니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()
# 친구 대기 상태 조회
def show_friend_requests(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()

        # 내가 보낸 친구 신청 목록
        st.title("내가 보낸 친구 신청")
        cursor.execute("SELECT requested_user_id FROM myFriendrequest WHERE user_id = ?", (user_id,))
        sent_requests = cursor.fetchall()
        if sent_requests:
            st.write(f"보낸 요청 데이터: {sent_requests}")  # 디버깅용
            for request in sent_requests:
                st.write(f"- {request['requested_user_id']}")
        else:
            st.write("보낸 친구 신청이 없습니다.")

        # 내가 받은 친구 신청 목록
        st.title("나에게 온 친구 신청")
        cursor.execute("SELECT requester_user_id FROM otherRequest WHERE user_id = ?", (user_id,))
        received_requests = cursor.fetchall()
        if received_requests:
            st.write(f"받은 요청 데이터: {received_requests}")  # 디버깅용
            for request in received_requests:
                st.write(f"- {request['requester_user_id']}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"수락: {request['requester_user_id']}", key=f"accept_{request['requester_user_id']}"):
                        accept_friend_request(user_id, request['requester_user_id'])
                with col2:
                    if st.button(f"거절: {request['requester_user_id']}", key=f"reject_{request['requester_user_id']}"):
                        reject_friend_request(user_id, request['requester_user_id'])
        else:
            st.write("받은 친구 신청이 없습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


# 친구 신청 수락
def accept_friend_request(user_id, requester_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 친구 리스트로 이동
        cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (user_id, requester_id))
        cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (requester_id, user_id))
        # 요청 삭제
        cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (user_id, requester_id))
        conn.commit()
        st.success(f"{requester_id}님과 친구가 되었습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 친구 신청 거절
def reject_friend_request(user_id, requester_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 요청 삭제
        cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (user_id, requester_id))
        conn.commit()
        st.success(f"{requester_id}님의 요청을 거절하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 친구 삭제 기능
def delete_friend(user_id, friend_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM friend WHERE user_id = ? AND friend_user_id = ?", (user_id, friend_id))
        conn.commit()
        st.success(f"{friend_id}님을 친구 목록에서 삭제하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

