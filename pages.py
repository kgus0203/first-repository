import streamlit as st
import sqlite3
import login
import posting
import friend
import setting
import group
from localization import Localization


# 초기화
if 'localization' not in st.session_state:
    st.session_state.localization = Localization(lang ='ko')  # 기본 언어는 한국어로 설정됨
# 현재 언어 설정 초기화
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'ko'  # 기본값으로 한국어 설정

localization = st.session_state.localization

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


# 페이지 이름 기반 키 추가
current_page = st.session_state["current_page"]

def home_page():
    col1, col2, col3 = st.columns([1, 1, 1])  # 동일한 너비의 세 개 열 생성
    with col1:
        if st.button(localization.get_text("login_button"), key=f"{current_page}_home_login_button"):
            change_page('Login')  # 로그인 페이지로 이동
    with col2:
        if st.button(localization.get_text("signup_button"), key=f"{current_page}_home_signup_button"):
            change_page('Signup')  # 회원가입 페이지로 이동
    with col3:
        if st.button(localization.get_text("forgot_button"), key=f"{current_page}_home_forgot_button"):
            change_page('User manager')  # ID/PW 찾기 페이지로 이동


def id_pw_change_page():
    st.title(localization.get_text("id_pw_change_title"))

    # 현재 로그인된 사용자 ID 가져오기
    user_id = st.session_state.get('logged_in_user')
    if not user_id:
        st.error(localization.get_text("no_user_error"))
        change_page('Login')  # 로그인 페이지로 이동
        return

    # 초기화 상태 설정
    if "id_pw_change_step" not in st.session_state:
        st.session_state['id_pw_change_step'] = "select_action"

    if "current_user_id" not in st.session_state:
        st.session_state['current_user_id'] = user_id

    # ID 또는 PW 변경 선택
    if st.session_state['id_pw_change_step'] == "select_action":
        action = st.radio(
            localization.get_text("select_change_action"),
            [localization.get_text("change_id"), localization.get_text("change_pw")]
        )
        if st.button(localization.get_text("next_button")):
            st.session_state['action'] = action
            st.session_state['id_pw_change_step'] = "input_new_value"

    # 새로운 ID/PW 입력 및 저장
    elif st.session_state['id_pw_change_step'] == "input_new_value":
        new_value = st.text_input(localization.get_text("enter_new_value").format(action=st.session_state['action']))
        if new_value and st.button(localization.get_text("save_button")):
            change = login.ChangeIDPW(
                user_id=st.session_state['current_user_id'],
                new_value=new_value
            )
            if st.session_state['action'] == localization.get_text("change_id") and change.update_id():
                st.success(localization.get_text("id_change_success"))
                st.session_state.clear()  # 세션 초기화로 로그아웃 처리
                change_page("Home")  # 첫 페이지로 이동
            elif st.session_state['action'] == localization.get_text("change_pw") and change.update_password():
                st.success(localization.get_text("pw_change_success"))
                st.session_state.clear()  # 세션 초기화로 로그아웃 처리
                change_page("Home")  # 첫 페이지로 이동




# 로그인 페이지
def login_page():
    # 로그인 페이지 렌더링
    st.write(localization.get_text("login_title"))
    user_id = st.text_input(localization.get_text("user_id_input"), key="login_user_id_input")
    user_password = st.text_input(localization.get_text("password_input"), type='password', key="login_password_input")

    col1, col2 = st.columns([1, 1])  # 버튼을 나란히 배치
    with col1:
        if st.button(localization.get_text("login_button"), key="login_submit_button"):
            if not user_id or not user_password:
                st.error(localization.get_text("login_error_empty"))
            else:
                sign_in = login.SignIn(user_id, user_password)
                if sign_in.sign_in_event():  # 로그인 성공 시
                    st.session_state['user_id'] = user_id  # 로그인한 사용자 ID 저장
                    change_page('after_login')  # 로그인 후 홈화면으로 이동
                else:
                    st.error(localization.get_text("login_error_failed"))
    with col2:
        if st.button(localization.get_text("back_button"), key="login_back_button"):
            go_back()  # 뒤로가기 로직 호출


# 회원가입 페이지
def signup_page():
    st.title(localization.get_text("signup_title"))

    # 사용자 입력 받기
    user_id = st.text_input(localization.get_text("user_id_input"))
    user_password = st.text_input(localization.get_text("password_input"), type='password')
    email = st.text_input(localization.get_text("email_input"))
    # 회원가입 처리 객체 생성
    signup = login.SignUp(user_id, user_password, email)
    col1, col2 = st.columns([1, 1])  # 버튼을 나란히 배치
    with col1:
        if st.button(localization.get_text("signup_button"), key="signup_submit_button"):
            if not user_id or not user_password or not email:
                st.error(localization.get_text("signup_error_empty"))
            else:
                if not signup.validate_email(email):
                    st.error(localization.get_text("invalid_email_error"))
                    return
                # 비밀번호 길이 체크
                if not signup.check_length():
                    return  # 비밀번호가 너무 짧으면 더 이상 진행하지 않음

                # 사용자 ID 중복 체크
                if not signup.check_user():
                    return  # 중복 아이디가 있으면 더 이상 진행하지 않음

                # 모든 검증을 통과하면 회원가입 진행
                signup.sign_up_event()

    with col2:
        if st.button(localization.get_text("back_button"), key="signup_back_button"):
            go_back()  # 뒤로가기 로직 호출


# 로그인 후 홈화면
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
    profile_image_url = result[0] if result and result[
        0] else 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'
    # 사용자 ID 표시 및 로그아웃 버튼
    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
    with col1:
        # 프로필 이미지를 클릭하면 페이지 이동
        st.image(profile_image_url, use_column_width=100)
    with col2:
        st.write(f"**{user_id}**")
    with col3:
        if st.button(localization.get_text("logout_button"), key="logout_button"):
            st.warning(localization.get_text("logout_success"))
            st.session_state.user = ''  # 세션 초기화
            change_page('Home')
    with col4:
        if st.button(localization.get_text("profile_button"), key="profile_button"):
            change_page("Setting")
    if st.button(localization.get_text("view_post_button"), key='posting_button'):
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


# 사이드바 : 그룹, 친구 설정
def friend_and_group_sidebar(user_id):
    st.sidebar.title(localization.get_text("group_management"))  # '그룹 관리'를 title 스타일로 표시
    if st.sidebar.button(localization.get_text("group_management_button")):
        st.session_state["current_page"] = "Group Management"  # 페이지를 'Group Management'로 설정
        st.rerun()

    st.sidebar.title(localization.get_text("friend_management"))  # '친구 관리'도 title 스타일로 표시

    # 친구 리스트
    if st.sidebar.button(localization.get_text("my_friend_list_button")):
        st.session_state["current_page"] = "FriendList"  # 'FriendList' 페이지로 설정
        st.session_state["action"] = "view_friend_list"
        st.rerun()

    # "내 친구 리스트" 상태일 때 추가 UI
    if st.session_state.get("current_page") == "FriendList":
        st.title(localization.get_text("my_friend_list_title"))
        friend.show_friend_list(user_id)  # 친구 리스트 출력

        # 뒤로가기 버튼 추가
        if st.button(localization.get_text("back_button"), key="friend_list_back_button"):
            st.session_state["current_page"] = "Home"  # 홈 페이지로 돌아가기
            st.rerun()

    # 하나의 입력창
    target_id = st.sidebar.text_input(localization.get_text("enter_id_prompt"), key="friend_action_input")

    # 팔로우 요청 버튼
    if st.sidebar.button(localization.get_text("send_friend_request_button"), key="add_friend_button"):
        if target_id:
            friend.add_friend(user_id, target_id)

    # 친구 대기 버튼
    if st.sidebar.button(localization.get_text("friend_requests_button"), key="friend_requests_button"):
        st.session_state["action"] = "view_friend_requests"

    # 차단/해제 버튼
    if st.sidebar.button(localization.get_text("block_button")):
        if target_id:
            friend.block_friend(user_id, target_id)
        else:
            st.session_state["action"] = localization.get_text("enter_id_prompt")

    if st.sidebar.button(localization.get_text("unblock_button")):
        if target_id:
            friend.unblock_friend(user_id, target_id)
        else:
            st.session_state["action"] = localization.get_text("enter_id_prompt")

    # 친구 삭제 버튼
    if st.sidebar.button(localization.get_text("delete_button")):
        if target_id:
            friend.delete_friend(user_id, target_id)
        else:
            st.session_state["action"] = localization.get_text("enter_id_prompt")

    # 작업 결과 또는 상태 표시
    if "action" in st.session_state:
        st.write(st.session_state["action"])
        del st.session_state["action"]


# 게시물 등록 페이지
def upload_post():
    st.header(localization.get_text("upload_post_header"))
    title = st.text_input(localization.get_text("post_title_input"))
    content = st.text_area(localization.get_text("post_content_input"))
    image_file = st.file_uploader(localization.get_text("image_file_upload"), type=['jpg', 'png', 'jpeg'])
    file_file = st.file_uploader(localization.get_text("general_file_upload"), type=['pdf', 'docx', 'txt', 'png', 'jpg'])

    # 카테고리 선택을 위한 Selectbox
    post_manager = posting.PostManager('uploads')  # DB 경로 설정
    category_names = post_manager.get_category_names()  # 카테고리 이름만 가져옴

    # Selectbox에서 카테고리 선택
    selected_category_name = st.selectbox(localization.get_text("category_select"), category_names)

    # 선택한 카테고리 이름에 해당하는 category_id 구하기
    categories = post_manager.get_category_options()
    category_dict = {category[1]: category[0] for category in categories}
    selected_category_id = category_dict[selected_category_name]

    location_search = posting.LocationSearch()
    location_search.display_location_on_map()

    col1, col2 = st.columns([6, 2])

    with col1:
        if st.button(localization.get_text("post_register_button")):
            if title and content:
                post_manager.add_post(title, content, image_file, file_file, selected_category_id)
                st.success(localization.get_text("post_register_success"))
            else:
                st.error(localization.get_text("post_register_error"))

    with col2:
        if st.button(localization.get_text("back_button")):
            go_back()  # 뒤로가기 로직 호출


# 게시물 수정 페이지
def change_post():
    st.header(localization.get_text("edit_post_header"))
    post_id = st.number_input(localization.get_text("edit_post_id_input"), min_value=1)
    posts = posting.get_all_posts()
    post = next((p for p in posts if p['p_id'] == post_id), None)

    if post:
        title = st.text_input(localization.get_text("post_title_input"), value=post['p_title'])
        content = st.text_area(localization.get_text("post_content_input"), value=post['p_content'])
        image_file = st.file_uploader(localization.get_text("image_file_upload"), type=['jpg', 'png', 'jpeg'], key='image_upload')
        file_file = st.file_uploader(localization.get_text("general_file_upload"), type=['pdf', 'docx', 'txt', 'png', 'jpg'], key='file_upload')
        location = st.number_input(localization.get_text("location_id_input"), min_value=1, value=post['p_location'])
        category = st.number_input(localization.get_text("category_id_input"), min_value=1, value=post['p_category'])

        if st.button(localization.get_text("edit_post_button")):
            posting.update_post(post_id, title, content, image_file, file_file, location, category)
            st.success(localization.get_text("edit_post_success"))
    else:
        st.error(localization.get_text("edit_post_not_found_error"))


# 게시물 삭제 페이지
def delete_post():
    st.header(localization.get_text("delete_post_header"))
    post_id = st.number_input(localization.get_text("delete_post_id_input"), min_value=1)
    posts = posting.get_all_posts()
    post = next((p for p in posts if p['p_id'] == post_id), None)

    if post:
        if st.button(localization.get_text("delete_post_button")):
            delete_post(post_id)
            st.success(localization.get_text("delete_post_success"))
    else:
        st.error(localization.get_text("delete_post_not_found_error"))


# 게시글 목록
def view_post():
    col1, col2, col3 = st.columns([6, 2, 2])  # 비율 6 : 2 : 2
    with col1:
        st.title(localization.get_text("view_post_header"))  # 제목을 왼쪽에 배치
    with col2:
        if st.button(localization.get_text("back_button")):
            go_back()  # 뒤로가기 로직 호출
    with col3:
        if st.button(localization.get_text("upload_post_button")):
            change_page('Upload Post')
    # PostManager 인스턴스를 생성
    post_manager = posting.PostManager()
    # display_posts 메서드를 호출
    post_manager.display_posts()


# 세팅 페이지
def setting_page():
    user_id = st.session_state.get("user_id")

    with sqlite3.connect('zip.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_email FROM user WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

    user_email = result[0] if result else None

    col1, col2 = st.columns([8, 2])
    with col1:
        st.title(localization.get_text("my_page_header"))
    with col2:
        if st.button(localization.get_text("back_button")):
            go_back()

    view = setting.SetView(user_id, user_email)
    view.render_user_profile()
    view.render_alarm_settings()
    theme_manager = setting.ThemeManager()
    theme_manager.render_button()
    theme_manager.select_language()

    view.render_posts()

def usermanager_page():
    st.title(localization.get_text("user_manager_page_title"))  # "사용자 관리 페이지"
    email = st.text_input(localization.get_text("email_input_prompt"))  # "이메일을 입력하세요:"

    # 확인 버튼
    if st.button(localization.get_text("confirm_button"), key="usermanager_confirm_button"):
        smtp_email = "kgus0203001@gmail.com"  # 발신 이메일 주소
        smtp_password = "pwhj fwkw yqzg ujha"  # 발신 이메일 비밀번호
        user_manager = login.UserManager(smtp_email, smtp_password)

        # 이메일 등록 여부 확인
        user_info = user_manager.is_email_registered(email)
        if user_info:
            st.success(localization.get_text("password_recovery_email_sent"))  # "비밀번호 복구 메일을 전송했습니다"
            user_manager.send_recovery_email(email)  # 복구 이메일 전송
        else:
            st.warning(localization.get_text("email_not_registered_warning"))  # "등록되지 않은 이메일입니다."

    # 뒤로가기 버튼
    if st.button(localization.get_text("back_button"), key="usermanager_back_button"):
        change_page("Home")  # 첫 페이지로 이동




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
    'User manager': usermanager_page,
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
