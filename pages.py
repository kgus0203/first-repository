import pandas as pd
import streamlit as st
import sqlite3
import bcrypt
import database
import login
import posting
import friend
import setting
import group

# 시작은 홈화면
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# 페이지 전환 함수
def change_page(page_name):
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.session_state["current_page"] != page_name:
        st.session_state["history"].append(st.session_state["current_page"])
    st.session_state["current_page"] = page_name
    st.rerun()


# 뒤로가기 함수
def go_back():
    if 'history' in st.session_state and st.session_state.history:
        st.session_state.current_page = st.session_state.history.pop()  # 이전 페이지로 이동
        st.rerun()
    else:
        st.warning("이전 페이지가 없습니다.")  # 방문 기록이 없을 경우 처리
        st.rerun()

# 홈 페이지 함수 (로그인 전)
def home_page():
    col1, col2, col3 = st.columns([1, 1, 1])  # 동일한 너비의 세 개 열 생성
    with col1:
        if st.button("로그인", key="home_login_button"):
            change_page('Login')  # 로그인 페이지로 이동
    with col2:
        if st.button("회원가입", key="home_signup_button"):
            change_page('Signup')  # 회원가입 페이지로 이동
    with col3:
        if st.button("ID/PW 찾기", key="home_forgot_button"):
            change_page('User manager')  # ID/PW 찾기 페이지로 이동


def id_pw_change_page():
    st.title("<ID/PW 변경>")

    # 현재 로그인된 사용자 ID 가져오기
    user_id = st.session_state.get('logged_in_user')
    if not user_id:
        st.error("사용자 정보가 없습니다. 다시 로그인해주세요.")
        change_page('Login')  # 로그인 페이지로 이동
        return

    # 초기화 상태 설정
    if "id_pw_change_step" not in st.session_state:
        st.session_state['id_pw_change_step'] = "select_action"

    if "current_user_id" not in st.session_state:
        st.session_state['current_user_id'] = user_id

    # ID 또는 PW 변경 선택
    if st.session_state['id_pw_change_step'] == "select_action":
        action = st.radio("변경할 항목을 선택하세요", ["ID 변경", "비밀번호 변경"])
        if st.button("다음"):
            st.session_state['action'] = action
            st.session_state['id_pw_change_step'] = "input_new_value"

    # 새로운 ID/PW 입력 및 저장
    elif st.session_state['id_pw_change_step'] == "input_new_value":
        new_value = st.text_input(f"새로 사용할 {st.session_state['action']}를 입력하세요")
        if new_value and st.button("저장"):
            change = login.ChangeIDPW(
                user_id=st.session_state['current_user_id'],
                new_value=new_value
            )
            if st.session_state['action'] == "ID 변경" and change.update_id():
                st.success("ID가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                st.session_state.clear()  # 세션 초기화로 로그아웃 처리
                change_page("Home")  # 첫 페이지로 이동
            elif st.session_state['action'] == "비밀번호 변경" and change.update_password():
                st.success("비밀번호가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                st.session_state.clear()  # 세션 초기화로 로그아웃 처리
                change_page("Home")  # 첫 페이지로 이동

#로그인 페이지
def login_page():
    st.title("로그인")
    user_id = st.text_input("아이디", key="login_user_id_input")
    user_password = st.text_input("비밀번호", type='password', key="login_password_input")

    col1, col2 = st.columns([1, 1])  # 버튼을 나란히 배치
    with col1:
        if st.button("로그인", key="login_submit_button"):
            if not user_id or not user_password:
                st.error("아이디와 비밀번호를 입력해 주세요.")
            else:
                sign_in = login.SignIn(user_id, user_password)
                if sign_in.sign_in_event():  # 로그인 성공 시
                    st.session_state['user_id'] = user_id  # 로그인한 사용자 ID 저장
                    change_page('after_login')  # 로그인 후 홈화면으로 이동
                else:
                    st.error("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.")
    with col2:
        if st.button("뒤로가기", key="login_back_button"):
            go_back()  # 뒤로가기 로직 호출



#회원가입 페이지
def signup_page():
    st.title("회원가입")

    # 사용자 입력 받기
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')
    email = st.text_input("이메일")

    col1, col2 = st.columns([1, 1])  # 버튼을 나란히 배치
    with col1:
        if st.button("회원가입", key="signup_submit_button"):
            if not user_id or not user_password or not email:
                st.error("모든 필드를 입력해 주세요.")
            else:
                # 회원가입 처리 객체 생성
                signup = login.SignUp(user_id, user_password, email)

                # 비밀번호 길이 체크
                if not signup.check_length():
                    return  # 비밀번호가 너무 짧으면 더 이상 진행하지 않음

                # 사용자 ID 중복 체크
                if not signup.check_user():
                    return  # 중복 아이디가 있으면 더 이상 진행하지 않음

                # 모든 검증을 통과하면 회원가입 진행
                signup.sign_up_event()

    with col2:
        if st.button("뒤로가기", key="signup_back_button"):
            go_back()  # 뒤로가기 로직 호출


#로그인 후 홈화면
def after_login():
    # 타이틀을 중앙에 크게 배치
    st.markdown("<h1 style='text-align: center;'>맛ZIP</h1>", unsafe_allow_html=True)
    # 사용자 정보
    user_id = st.session_state.get("user_id")
    # 로그인 정보 없을 시 처리
    if not user_id:
        st.error("로그인 정보가 없습니다. 다시 로그인해주세요.")
        change_page('Login')
        return

    # 친구 관리 사이드바 추가
    friend_and_group_sidebar(user_id)
    # 데이터베이스 연결
    conn = sqlite3.connect('zip.db')
    cursor = conn.cursor()

    # 사용자 프로필 정보 가져오기
    cursor.execute("SELECT profile_picture_path FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    # 프로필 이미지 경로 설정 (없을 경우 기본 이미지 사용)
    profile_image_url = result[0] if result and result[0] else 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'
    # 사용자 ID 표시 및 로그아웃 버튼
    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
    with col1:
        # 프로필 이미지를 클릭하면 페이지 이동
        st.image(profile_image_url,use_container_width=100
        )
    with col2:
        st.write(f"**{user_id}**")
    with col3:
        if st.button("로그아웃", key="logout_button"):
            st.warning("로그아웃 되었습니다.")
            st.session_state.user=''  # 세션 초기화
            change_page('Home')
    with col4:
        if st.button("내 프로필", key="profile_button"):
            change_page("Setting")
    if st.button('View Post', key='posting_button'):
        change_page('View Post')

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

def friend_and_group_sidebar(user_id):
    st.sidebar.title("그룹 관리")  # '그룹 관리'를 title 스타일로 표시
    if st.sidebar.button("그룹 관리"):
        st.session_state["current_page"] = "Group Management"  # 페이지를 'Group Management'로 설정
        st.rerun()  # 페이지 새로고침

    # 친구 관리 상위 요소
    st.sidebar.title("친구 관리")  # '친구 관리'도 title 스타일로 표시
    # 친구찾기 버튼
    if st.sidebar.button("친구찾기"):
        friend_user_id = st.text_input("추가할 친구 ID:")
        if st.button("팔로우 요청 보내기"):
            if friend_user_id:
                friend.follow_friend(user_id, friend_user_id)
            else:
                st.error("친구 ID를 입력하세요.")

    # 친구 대기 버튼
    if st.sidebar.button("친구 대기"):
        pending_requests = friend.get_follow_requests(user_id)
        if pending_requests:
            st.subheader("친구 요청 대기 목록")
            for req in pending_requests:
                st.write(f"요청자: {req['user_id']}")
                if st.button(f"수락: {req['user_id']}"):
                    friend.handle_follow_request(user_id, req['user_id'], "accept")
                if st.button(f"거절: {req['user_id']}"):
                    friend.handle_follow_request(user_id, req['user_id'], "reject")
        else:
            st.write("대기 중인 요청이 없습니다.")

    # 차단/해제 버튼
    if st.sidebar.button("차단/해제"):
        blocked_user_id = st.text_input("차단/해제할 친구 ID:")
        if st.button("차단"):
            st.write(f"{blocked_user_id}님을 차단했습니다.")  # 여기에 차단 로직 추가 가능
        if st.button("차단 해제"):
            st.write(f"{blocked_user_id}님 차단을 해제했습니다.")  # 여기에 차단 해제 로직 추가 가능

    # 친구 삭제 버튼
    if st.sidebar.button("삭제"):
        delete_user_id = st.text_input("삭제할 친구 ID:")
        if st.button("삭제 확인"):
            # 삭제 로직 호출
            st.write(f"{delete_user_id}님을 친구 목록에서 삭제했습니다.")  # 여기에 삭제 로직 추가 가능

# 게시물 등록 페이지
def upload_post() :
    st.header("게시물 등록")
    title = st.text_input("게시물 제목")
    content = st.text_area("게시물 내용")
    image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'])
    file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'])


    # 카테고리 선택을 위한 Selectbox
    post_manager = posting.PostManager('uploads')  # DB 경로 설정
    category_names = post_manager.get_category_names()  # 카테고리 이름만 가져옴


    # Selectbox에서 카테고리 선택
    selected_category_name = st.selectbox("카테고리", category_names)


   # 선택한 카테고리 이름에 해당하는 category_id 구하기
    categories = post_manager.get_category_options()
    category_dict = {category[1]: category[0] for category in categories}
    selected_category_id = category_dict[selected_category_name]


    location_search = posting.LocationSearch()
    location_search.display_location_on_map()

    col1, col2 = st.columns([6, 2])

    with col1:
        if st.button("게시물 등록"):
            if title and content:
                post_manager.add_post(title, content, image_file, file_file, selected_category_id)
                st.success("게시물이 등록되었습니다.")
            else:
                st.error("제목과 내용을 입력해 주세요.")

        with col2:
            if st.button("뒤로가기"):
                go_back()  # 뒤로가기 로직 호출


# 게시물 수정 페이지
def change_post() :
    st.header("게시물 수정")
    post_id = st.number_input("수정할 게시물 ID", min_value=1)
    posts = posting.get_all_posts()
    post = next((p for p in posts if p['p_id'] == post_id), None)

    if post:
        title = st.text_input("게시물 제목", value=post['p_title'])
        content = st.text_area("게시물 내용", value=post['p_content'])
        image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'], key='image_upload')
        file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'], key='file_upload')
        location = st.number_input("위치 ID", min_value=1, value=post['p_location'])
        category = st.number_input("카테고리 ID", min_value=1, value=post['p_category'])

        if st.button("게시물 수정"):
            posting.update_post(post_id, title, content, image_file, file_file, location, category)
            st.success("게시물이 수정되었습니다.")
    else:
        st.error("해당 게시물이 존재하지 않습니다.")

# 게시물 삭제 페이지
def delete_post() :
    st.header("게시물 삭제")
    post_id = st.number_input("삭제할 게시물 ID", min_value=1)
    posts = posting.get_all_posts()
    post = next((p for p in posts if p['p_id'] == post_id), None)

    if post:
        if st.button("게시물 삭제"):
            delete_post(post_id)
            st.success("게시물이 삭제되었습니다.")
    else:
        st.error("해당 게시물이 존재하지 않습니다.")

#게시글 목록
def view_post():
    col1, col2, col3 = st.columns([6, 2, 2])  # 비율 6 : 2 : 2
    with col1:
        st.title("게시물 목록")  # 제목을 왼쪽에 배치
    with col2:
        if st.button("뒤로가기"):
            go_back()  # 뒤로가기 로직 호출
    with col3:
        if st.button("글 작성"):
            change_page('Upload Post')
    # PostManager 인스턴스를 생성
    post_manager = posting.PostManager()
    # display_posts 메서드를 호출
    post_manager.display_posts()

#세팅 페이지
def setting_page():
    user_id = st.session_state.get("user_id")

    with sqlite3.connect('zip.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_email FROM user WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

    user_email = result[0] if result else None

    col1, col2 = st.columns([8, 2])
    with col1:
        st.title("내 페이지")
    with col2:
        if st.button("뒤로가기"):
            go_back()

    view = setting.SetView(user_id, user_email)
    view.render_user_profile()
    view.render_alarm_settings()
    theme_manager = setting.ThemeManager()
    theme_manager.render_button()

    view.render_posts()


def usermanager_page():

    st.title("사용자 관리 페이지")
    email = st.text_input('이메일을 입력하세요: ')

    if st.button("확인", key="forgot_confirm_button"):
        smtp_email = "kgus0203001@gmail.com"  # 발신 이메일 주소
        smtp_password = "pwhj fwkw yqzg ujha"  # 발신 이메일 비밀번호
        user_manager = login.UserManager(smtp_email, smtp_password)

        # 이메일 등록 여부 확인
        user_info = user_manager.is_email_registered(email)
        if user_info:
            st.success(f"비밀번호 복구 메일을 전송했습니다")
            # 복구 이메일 전송
            user_manager.send_recovery_email(email)
        else:
            st.warning("등록되지 않은 이메일입니다.")

    if st.button("뒤로가기", key="forgot_back_button"):
                    # 첫 페이지로 이동
                    change_page("Home")


# 페이지 함수 매핑
page_functions = {
    'Home': home_page,
    'Login': login_page,
    'Signup': signup_page,
    'after_login': after_login,
    'Upload Post': upload_post,
    'Change Post': change_post,
    'Delete Post': delete_post,
    'View Post': view_post,
    'Setting': setting_page,
    'User manager' : usermanager_page,
    'ID PW 변경': id_pw_change_page,
    'Group Management': group.main,
}

# 현재 페이지 디버깅
st.write(f"Current Page: {st.session_state['current_page']}")  # 디버깅용 코드

# 현재 페이지 렌더링
if st.session_state["current_page"] in page_functions:
    page_functions[st.session_state["current_page"]]()  # 매핑된 함수 호출
else:
    st.error(f"페이지 {st.session_state['current_page']}를 찾을 수 없습니다.")
