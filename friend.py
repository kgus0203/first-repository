#friend.py 이상원 11.27 업로드 2차
#friend.py 이상원 11.29 업로드 3차

#여기서부터-----------------------------------------------------------------------------
import sqlite3
import streamlit as st

# 데이터베이스 연결 함수
def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
    return conn



# 내 친구 리스트 표시
def show_friend_list(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 친구 목록 가져오기
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
# 대기 중인 친구 요청을 표시하는 함수
def show_friend_requests_page(user_id):
    st.title("친구 요청 관리")

    # 내가 보낸 요청 목록
    st.subheader("내가 보낸 친구 요청")
    sent_requests = get_my_sent_requests(user_id)
    if sent_requests:
        for req in sent_requests:
            st.write(f"- {req['requested_user_id']}")
    else:
        st.write("보낸 친구 요청이 없습니다.")

    # 내가 받은 요청 목록
    st.subheader("다른 사람이 보낸 친구 요청")
    received_requests = get_received_requests(user_id)
    if received_requests:
        for req in received_requests:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- {req['requester_user_id']}")
            with col2:
                if st.button(f"수락 ({req['requester_user_id']})", key=f"accept_{req['requester_user_id']}"):
                    accept_friend_request(user_id, req['requester_user_id'])
                if st.button(f"거절 ({req['requester_user_id']})", key=f"reject_{req['requester_user_id']}"):
                    reject_friend_request(user_id, req['requester_user_id'])
    else:
        st.write("받은 친구 요청이 없습니다.")

# 차단 리스트 출력
def show_blocked_list(user_id):
    st.title("차단 목록")
    
    conn = create_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT blocked_user_id FROM block WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        blocked_users = cursor.fetchall()
        if blocked_users:
            st.title("차단 목록")
            for blocked in blocked_users:
                st.write(f"- {blocked['blocked_user_id']}")
        
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()
# 차단 목록을 출력하는 함수
def show_blocked_list_page(user_id):
    st.title("차단 목록")

    blocked_users = show_blocked_list(user_id)  # 차단된 유저 목록 가져오기
    if blocked_users:
        st.subheader("현재 차단된 사용자:")
        for user in blocked_users:
            st.write(f"- {user['blocked_user_id']}")
    else:
        st.write("차단된 사용자가 없습니다.")

#친구 신청 함수 
def add_friend(user_id, friend_id):
    if user_id == friend_id:
        st.error("자신을 친구로 추가할 수 없습니다.")
        return

    conn = create_connection()
    try:
        cursor = conn.cursor()

        # 차단 여부 확인
        query = "SELECT * FROM block WHERE user_id = ? AND blocked_user_id = ?"
        cursor.execute(query, (user_id, friend_id))
        blocked_user = cursor.fetchone()
        if blocked_user:
            st.error("먼저 차단을 해제해주세요.")
            return
        
        # 상대방 존재 확인
        query = "SELECT user_id FROM user WHERE user_id = ?"
        cursor.execute(query, (friend_id,))
        user_exists = cursor.fetchone()
        if not user_exists:
            st.error("없는 ID입니다.")
            return

        # 이미 친구인지 확인
        query = "SELECT * FROM friend WHERE user_id = ? AND friend_user_id = ?"
        cursor.execute(query, (user_id, friend_id))
        already_friends = cursor.fetchone()
        if already_friends:
            st.error("이미 친구입니다.")
            return

        # 이미 요청 보냈는지 확인
        query = "SELECT * FROM myFriendrequest WHERE user_id = ? AND requested_user_id = ?"
        cursor.execute(query, (user_id, friend_id))
        already_requested = cursor.fetchone()
        if already_requested:
            st.error("이미 친구 요청을 보냈습니다.")
            return

        # 친구 요청 등록
        cursor.execute("INSERT INTO myFriendrequest (user_id, requested_user_id) VALUES (?, ?)", (user_id, friend_id))
        cursor.execute("INSERT INTO otherRequest (user_id, requester_user_id) VALUES (?, ?)", (friend_id, user_id))
        conn.commit()

        # 디버깅 로그 추가 (데이터 저장 확인)
        DEBUG_MODE = True  # 디버깅 모드 설정
        if DEBUG_MODE:
         cursor.execute("SELECT * FROM myFriendrequest WHERE user_id = ? AND requested_user_id = ?", (user_id, friend_id))
        st.write("My Friend Requests:", cursor.fetchall())

        st.success(f"{friend_id}님에게 친구 요청을 보냈습니다. 상대방이 수락할 때까지 기다려주세요.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 내가 보낸 친구 요청 조회
def get_my_sent_requests(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT requested_user_id FROM myFriendrequest WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
        return []
    finally:
        conn.close()

# 내가 받은 친구 요청 조회
def get_received_requests(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT requester_user_id FROM otherRequest WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
        return []
    finally:
        conn.close()


def accept_friend_request(user_id, requester_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        
        # 친구 관계 추가
        cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (user_id, requester_id))
        cursor.execute("INSERT INTO friend (user_id, friend_user_id) VALUES (?, ?)", (requester_id, user_id))
        
        # 요청 삭제 (수락된 경우)
        cursor.execute("DELETE FROM myFriendrequest WHERE requested_user_id = ? AND user_id = ?", (user_id, requester_id))
        cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (user_id, requester_id))
        
        # 상대방의 요청 리스트에서도 삭제
        cursor.execute("DELETE FROM myFriendrequest WHERE requested_user_id = ? AND user_id = ?", (requester_id, user_id))
        cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (requester_id, user_id))
        
        conn.commit()
        st.success(f"{requester_id}님과 친구가 되었습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


def reject_friend_request(user_id, requester_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        
        # 요청 삭제 (거절된 경우)
        cursor.execute("DELETE FROM myFriendrequest WHERE requested_user_id = ? AND user_id = ?", (user_id, requester_id))
        cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (user_id, requester_id))
        
        # 상대방의 요청 리스트에서도 삭제
        cursor.execute("DELETE FROM myFriendrequest WHERE requested_user_id = ? AND user_id = ?", (requester_id, user_id))
        cursor.execute("DELETE FROM otherRequest WHERE user_id = ? AND requester_user_id = ?", (requester_id, user_id))
        
        conn.commit()
        st.success(f"{requester_id}님의 친구 요청을 거절했습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()


# 차단
def block_friend(user_id, friend_id):
    if user_id == friend_id:
        st.error("자신을 차단할 수 없습니다.")
        return
    
    conn = create_connection()
    try:
        cursor = conn.cursor()
        
        # user 테이블에서 해당 ID 존재 여부 확인
        query = "SELECT user_id FROM user WHERE user_id = ?"
        cursor.execute(query, (friend_id,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            st.error("없는 ID입니다.")  # 해당 ID가 user 테이블에 없을 경우
            return
        
        # 이미 차단했는지 확인
        query = "SELECT * FROM block WHERE user_id = ? AND blocked_user_id = ?"
        cursor.execute(query, (user_id, friend_id))
        already_blocked = cursor.fetchone()
        
        if already_blocked:
            st.error("이미 차단된 사용자입니다.")
            return

        # 친구 목록에서 삭제 (차단된 경우 친구에서 제거)
        cursor.execute("DELETE FROM friend WHERE user_id = ? AND friend_user_id = ?", (user_id, friend_id))

        # 차단 테이블에 추가
        cursor.execute("INSERT INTO block (user_id, blocked_user_id) VALUES (?, ?)", (user_id, friend_id))
        conn.commit()
        
        st.success(f"{friend_id}님을 차단하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()







# 차단 해제
def unblock_friend(user_id, friend_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 차단된 사용자인지 확인
        query = "SELECT * FROM block WHERE user_id = ? AND blocked_user_id = ?"
        cursor.execute(query, (user_id, friend_id))
        blocked = cursor.fetchone()
        if not blocked:
            st.error("차단된 사용자가 아닙니다.")
            return

        # 차단 해제
        cursor.execute("DELETE FROM block WHERE user_id = ? AND blocked_user_id = ?", (user_id, friend_id))
        conn.commit()
        st.success(f"{friend_id}님을 차단 해제하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

# 친구 삭제
def delete_friend(user_id, friend_id):
    if user_id == friend_id:
        st.error("자신을 삭제할 수 없습니다.")
        return
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # 친구인지 확인
        query = "SELECT * FROM friend WHERE user_id = ? AND friend_user_id = ?"
        cursor.execute(query, (user_id, friend_id))
        is_friend = cursor.fetchone()
        if not is_friend:
            st.error("해당 유저는 내 친구 리스트에 없는 유저입니다.")
            return

        # 친구 삭제
        cursor.execute("DELETE FROM friend WHERE user_id = ? AND friend_user_id = ?", (user_id, friend_id))
        conn.commit()
        st.success(f"{friend_id}님을 친구 목록에서 삭제하였습니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

#여기까지-----------------------------------------------------------------------------
