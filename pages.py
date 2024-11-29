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

# 홈 페이지 함수 (로그인 전)
def home_page():
    col1, col2 = st.columns(2)
    with col1:
        st.title("맛ZIP")
    with col2:
        col3, col4, col5 = st.columns(3)
        with col3:
            if st.button((localization.get_text("login_title")), use_container_width=True):
                login_page()
        with col4:
            if st.button((localization.get_text("signup_title")), use_container_width=True):
                signup_page()
        with col5:
            if st.button((localization.get_text("id_pw_change_title")), use_container_width=True):
                id_pw_change_page()

    # 중앙 포스팅 리스트
    st.title(localization.get_text("Recommended Restaurant Posts"))

    # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
    post_manager = posting.PostManager()  # 인스턴스 생성
    post_manager.display_posts_on_home()  # display_posts_on_home 메서드 호출




#로그인 페이지
@st.dialog(localization.get_text("login_title1"))
def login_page():
    user_id = st.text_input(localization.get_text("user_id_input"), key="login_user_id_input")
    user_password = st.text_input(localization.get_text("password_input"), type='password', key="login_password_input")

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

#회원가입 페이지
@st.dialog(localization.get_text("signup_title"))
def signup_page():
    # 사용자 입력 받기
    user_id = st.text_input(localization.get_text("user_id_input"))
    user_password = st.text_input(localization.get_text("password_input"), type='password')
    email = st.text_input(localization.get_text("email_input"))

    # 회원가입 처리 객체 생성
    signup = login.SignUp(user_id, user_password, email)
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
                
#아이디 비번 변경
@st.dialog(localization.get_text("id_pw_change_title"))
def id_pw_change_page():
    st.title(localization.get_text("상원님 아이디 비번 변경 로직 뭔지 모르겠어요1! 알려주시면 고침!"))

    # # 현재 로그인된 사용자 ID 가져오기
    # user_id = st.session_state.get('logged_in_user')
    # if not user_id:
    #     st.error(localization.get_text("no_user_error"))
    #     change_page('Login')  # 로그인 페이지로 이동
    #     return

    # # 초기화 상태 설정
    # if "id_pw_change_step" not in st.session_state:
    #     st.session_state['id_pw_change_step'] = "select_action"

    # if "current_user_id" not in st.session_state:
    #     st.session_state['current_user_id'] = user_id

    # # ID 또는 PW 변경 선택
    # if st.session_state['id_pw_change_step'] == "select_action":
    #     action = st.radio(
    #         localization.get_text("select_change_action"),
    #         [localization.get_text("change_id"), localization.get_text("change_pw")]
    #     )
    #     if st.button(localization.get_text("next_button")):
    #         st.session_state['action'] = action
    #         st.session_state['id_pw_change_step'] = "input_new_value"

    # # 새로운 ID/PW 입력 및 저장
    # elif st.session_state['id_pw_change_step'] == "input_new_value":
    #     new_value = st.text_input(localization.get_text("enter_new_value").format(action=st.session_state['action']))
    #     if new_value and st.button(localization.get_text("save_button")):
    #         change = login.ChangeIDPW(
    #             user_id=st.session_state['current_user_id'],
    #             new_value=new_value
    #         )
    #         if st.session_state['action'] == localization.get_text("change_id") and change.update_id():
    #             st.success(localization.get_text("id_change_success"))
    #             st.session_state.clear()  # 세션 초기화로 로그아웃 처리
    #             change_page("Home")  # 첫 페이지로 이동
    #         elif st.session_state['action'] == localization.get_text("change_pw") and change.update_password():
    #             st.success(localization.get_text("pw_change_success"))
    #             st.session_state.clear()  # 세션 초기화로 로그아웃 처리
    #             change_page("Home")  # 첫 페이지로 이동



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
        st.image(profile_image_url, use_column_width= True)
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
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button(localization.get_text("view_post_button"), key='posting_button'):
            change_page('View Post')
    with col2:
        if st.button(localization.get_text("group_button"), key='group_button'):  # 번역 키 "group_button" 사용
            change_page("Group page")

    # 중앙 포스팅 리스트
    st.title(localization.get_text("Recommended Restaurant Posts"))

    # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
    post_manager = posting.PostManager()  # 인스턴스 생성
    post_manager.display_posts_on_home()  # display_posts_on_home 메서드 호출


    # 친구 관리 사이드바 추가(사이드바 이름 변경 참고 부탁드립니다, 관련 이름 모두 수정함)
    sidebar(user_id)

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

# 사이드바 ui----------------------------------------------------------------------------------------------------------

def sidebar(user_id):
    #사이드바에는 친구만 존재
    st.sidebar.title("친구 관리")

    # 친구 리스트
    if st.sidebar.button("내 친구 리스트"):
        st.session_state["current_page"] = "FriendList"
        st.rerun()
    # 내 친구 리스트 페이지
    if st.session_state.get("current_page") == "FriendList":
        st.title("내 친구 리스트")
        friend.show_friend_list(user_id)
    
        # 친구 리스트 뒤로가기 버튼
        if st.button("뒤로가기", key="friend_list_back_button"):
            st.session_state["current_page"] = "after_login"
            st.rerun()
           


    # 친구 대기 버튼
    if st.sidebar.button("친구 대기"):
        st.session_state["current_page"] = "FriendRequests"
        st.rerun()
    # 친구 대기 페이지
    if st.session_state.get("current_page") == "FriendRequests":
        st.title("친구 대기")
        friend.show_friend_requests_page(user_id)
       
    # 친구 대기 뒤로가기 버튼
        if st.button("뒤로가기", key="friend_requests_back_button"):
            st.session_state["current_page"] = "after_login"
            st.rerun()
        st.write(f"Current Page: {st.session_state.get('current_page', 'None')}")


    # 차단 목록 버튼
    if st.sidebar.button("차단 목록"):
        st.session_state["current_page"] = "BlockedList"
        st.rerun()
    # 차단 목록 페이지
    if st.session_state.get("current_page") == "BlockedList":
        st.title("차단 목록")
        friend.show_blocked_list_page(user_id)
    
    # 차단 목록 뒤로가기 버튼
        if st.button("뒤로가기", key="blocked_list_back_button"):
            st.session_state["current_page"] = "after_login"
            st.rerun()

    # 상호작용할 ID 입력창
    target_id = st.sidebar.text_input("ID를 입력하세요:", key="friend_action_input")


    # 친구 요청 버튼
    if st.sidebar.button("친구 요청 보내기", key="add_friend_button"):
        if target_id:
            friend.add_friend(user_id, target_id)

    # 차단 버튼
    if st.sidebar.button("차단"):
        if target_id:
            friend.block_friend(user_id, target_id)
        else:
            st.session_state["action"] = "ID를 입력하세요."

    # 차단 해제 버튼
    if st.sidebar.button("차단 해제"):
        if target_id:
            friend.unblock_friend(user_id, target_id)
        else:
            st.session_state["action"] = "ID를 입력하세요."

    # 친구 삭제 버튼
    if st.sidebar.button("삭제"):
        if target_id:
            friend.delete_friend(user_id, target_id)
        else:
            st.session_state["action"] = "ID를 입력하세요."

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
    post_manager = posting.PostManager('zip.db')  # DB 경로 설정
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
        if st.button(localization.get_text("upload_post_button")):
            change_page('Upload Post')
    with col3:
        if st.button(localization.get_text("back_button")):
            go_back()  # 뒤로가기 로직 호출        
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

def my_groups_page():
    # 상단 제목 설정 (좌측 정렬)
    col1, col2 = st.columns([4, 4])  # 버튼을 위한 공간 추가
    with col1:
        st.markdown(
            f"<h1 class='centered-title'>{localization.get_text('group_page_title')}</h1>",
            unsafe_allow_html=True,
        )
    with col2:
        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            if st.button(localization.get_text("create_group_button"), use_container_width=True):
                # 그룹 생성 페이지
                group_creation_page()
        with button_col2:
            if st.button(localization.get_text("search_group_button"), use_container_width=True):
                # 그룹 검색 페이지
                search_groups_page()
        with button_col3:
            if st.button(localization.get_text("back_button"), use_container_width=True):
                # 고백
                go_back()

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error(localization.get_text("login_required_error"))
        return


    # GroupAndLocationApp 클래스의 인스턴스를 생성
    app = group.GroupAndLocationApp(db_name="zip.db", kakao_api_key="your_kakao_api_key")
    conn = app.create_connection()  # create_connection 메서드를 호출
    if not conn:
        st.error("데이터베이스 연결 실패")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                g.group_id, 
                g.group_name, 
                g.modify_date, 
                g.meeting_date, 
                g.meeting_time, 
                COUNT(gm.user_id) AS current_members
            FROM "group" g
            JOIN group_member gm ON g.group_id = gm.group_id
            WHERE gm.user_id = ?
            GROUP BY g.group_id
        """, (user_id,))
        groups = cursor.fetchall()

    except sqlite3.Error as e:
        st.error(localization.get_text("db_error").format(e))
        return
    finally:
        conn.close()

    if not groups:
        st.warning(localization.get_text("no_joined_groups"))
        return

    # CSS 스타일링 (어두운 회색 박스 색상, 그룹 박스를 중앙 배치, 버튼 스타일)
    st.markdown(
        """
        <style>
        /* 그룹 박스 중앙 배치 */
        .group-box {
            border: 2px solid #555555;  /* 어두운 회색 테두리 */
            padding: 20px;
            border-radius: 10px;
            background-color: #333333;  /* 어두운 회색 배경 */
            margin: 15px auto;  /* 중앙 정렬을 위한 auto 설정 */
            color: white;  /* 텍스트를 하얀색으로 설정 */
            width: 80%;  /* 박스 크기 설정 */
            text-align: center; /* 텍스트를 중앙 정렬 */
        }
        .group-box h2 {
            margin-bottom: 10px;
        }
        .group-box p {
            margin: 5px 0;
        }

        /* "열기" 버튼 스타일 */
        .open-button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            width: 100%; /* 버튼을 가로로 길게 만들기 */
        }

        .open-button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 그룹 정보 표시
    for group_id, group_name, modify_date, meeting_date, meeting_time, current_members in groups:
        st.markdown(
            f"""
            <div class="group-box">
                <h2>{group_name}</h2>
                <p><strong>인원:</strong> {current_members} / 10</p>
                <p><strong>약속 날짜:</strong> {meeting_date if meeting_date else '설정되지 않음'}</p>
                <p><strong>약속 시간:</strong> {meeting_time if meeting_time else '설정되지 않음'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button(f"세부 정보", key=f"open_group_{group_id}"):
            st.session_state["group_id"] = group_id  # 그룹 ID를 세션에 저장
            change_page("Detail group")  # 세부 정보 페이지 호출

        # 그룹들 사이에 구분선
        st.markdown("---")

# 멤버 박스 출력 함수 (그룹장은 왕관 아이콘만 표시하고, 다른 멤버는 번호만 표시)
def display_member_box(member_name, is_admin, member_number):
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    # 그룹장일 경우 왕관 아이콘만 표시하고, 일반 멤버는 번호만 표시
    member_display = f"{'👑 ' if is_admin else ''}{member_name}"
    member_icon = number_emojis[member_number - 1] if not is_admin else ""  # 그룹장에게는 번호 표시 안함

    st.markdown(
        f"""
        <div class="member-box">
            <span><span class="member-icon">{member_icon}</span><strong>{member_display}</strong></span>
        </div>
        """,
        unsafe_allow_html=True
    )

# 그룹 세부 정보 페이지
def detail_group():
    col1, col2 = st.columns([6, 2])  # 비율 6 : 2
    with col1:
        st.title("그룹 세부 정보")  # 제목을 왼쪽에 배치
    with col2:
        if st.button("뒤로가기 ↩️"):
            go_back()  # 뒤로가기 로직 호출
            
    # 그룹 ID 가져오기 (열기 버튼 클릭 시 해당 그룹 ID가 넘어옴)
    group_id = st.session_state.get("group_id")
    if not group_id:
        st.error("그룹 정보가 없습니다.")
        return

    # GroupAndLocationApp 클래스의 인스턴스를 생성
    app = group.GroupAndLocationApp(db_name="zip.db", kakao_api_key="your_kakao_api_key")
    conn = app.create_connection()  # create_connection 메서드를 호출
    if not conn:
        st.error("데이터베이스 연결 실패")
        return

    try:
        cursor = conn.cursor()
        cursor.execute(""" 
            SELECT 
                g.group_id, 
                g.group_name, 
                g.modify_date, 
                g.meeting_date, 
                g.meeting_time, 
                COUNT(gm.user_id) AS current_members
            FROM "group" g
            JOIN group_member gm ON g.group_id = gm.group_id
            WHERE g.group_id = ?
            GROUP BY g.group_id
        """, (group_id,))
        group_info = cursor.fetchone()

        if not group_info:
            st.error("그룹 정보를 찾을 수 없습니다.")
            return

        group_name, modify_date, meeting_date, meeting_time, current_members = group_info[1], group_info[2], group_info[3], group_info[4], group_info[5]

        # 그룹 정보 표시
        st.markdown(f"### {group_name}")
        st.markdown(f"**현재 인원수:** {current_members} / 10")
        st.markdown(f"**마지막 수정일:** {modify_date}")
        st.markdown(f"**약속 날짜:** {meeting_date if meeting_date else '설정되지 않음'}")
        st.markdown(f"**약속 시간:** {meeting_time if meeting_time else '설정되지 않음'}")

        # 그룹원 정보 가져오기 (그룹장이면 왕관 아이콘 추가)
        cursor.execute("""
            SELECT u.user_id, gm.role
            FROM group_member gm
            JOIN user u ON gm.user_id = u.user_id
            WHERE gm.group_id = ?
        """, (group_id,))
        members = cursor.fetchall()

        # 그룹원 표시
        if members:
            st.write("**그룹원:**")
            for idx, (member_name, role) in enumerate(members, start=1):
                is_admin = role == 'admin'  # 그룹장이면 True
                display_member_box(member_name, is_admin, idx)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"그룹 삭제", key=f"delete_group_{group_id}"):
                # 그룹 ID를 세션에 저장하고 삭제 페이지 호출
                st.session_state["group_id_to_delete"] = group_id
                group_delete_page()  # 그룹 삭제 함수 호출
        with col2:
            if st.button(f"그룹 수정", key=f"edit_group_{group_id}"):
                st.session_state["group_id_to_edit"] = group_id  # 수정할 그룹 ID 세션에 저장
                group_update_page()  # 그룹 수정 페이지 호출

    except sqlite3.Error as e:
        st.error(localization.get_text("db_error").format(e)) 
    finally:
        conn.close()

#그룹 생성 페이지
@st.dialog("그룹 생성")
def group_creation_page():
    """그룹 생성 페이지"""
    # GroupAndLocationApp 인스턴스를 생성합니다.
    kakao_api_key = "393132b4dfde1b54fc18b3bacc06eb3f"  # 실제 API 키로 대체
    app = group.GroupAndLocationApp(db_name="zip.db", kakao_api_key=kakao_api_key)  # 인스턴스를 생성합니다.

    # 이제 인스턴스를 통해 group_creation_page 메서드를 호출합니다.
    st.header("그룹 생성")
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("로그인이 필요합니다.")
        return

    # 그룹 이름 입력
    group_name = st.text_input("그룹 이름", placeholder="그룹 이름을 입력하세요", key="group_name_input")
    max_members = st.number_input("최대 인원 수", min_value=2, max_value=10, step=1, value=10, key="max_members_input")

    # 약속 날짜와 시간 추가 여부
    add_schedule = st.checkbox("약속 날짜와 시간 설정", key="add_schedule_checkbox")

    # 약속 날짜와 시간 입력 (체크박스 선택 시 활성화)
    meeting_date = None
    meeting_time_str = None
    if add_schedule:
        meeting_date = st.date_input("약속 날짜 선택", key="meeting_date_input")
        meeting_time = st.time_input("약속 시간 선택", key="meeting_time_input")
        meeting_time_str = meeting_time.strftime("%H:%M:%S")  # 시간 문자열로 변환

    # 카테고리 선택
    dao = group.CategoryDAO()
    categories = dao.get_all_categories()
    if categories:
        category = st.selectbox("카테고리 선택", options=categories, format_func=lambda x: x[1], key="category_selectbox")
    else:
        st.error("등록된 카테고리가 없습니다.")
        return

    # 장소 검색 필드와 지도
    location_search = app.location_search  # LocationSearch 객체
    conn = app.create_connection()
    # 세션 상태 초기화
    if "query" not in st.session_state:
        st.session_state["query"] = ""
    if "locations" not in st.session_state:
        st.session_state["locations"] = []
    if "selected_location" not in st.session_state:
        # 기본 위치 설정: 노브랜드버거 영남대점
        st.session_state["selected_location"] = {
            "place_name": "노브랜드버거 영남대점",
            "address_name": "경북 경산시 대학로 302",
            "latitude": 35.883778,
            "longitude": 128.608934,
        }

    # 검색 입력 필드 (항상 표시)
    st.subheader("장소 검색")
    query = st.text_input("검색할 장소를 입력하세요:", value=st.session_state["query"], key="query_input")
    if st.button("검색", key="search_button"):
        st.session_state["query"] = query
        results = location_search.search_location(query)

        if results:
            # 장소 정보 리스트 생성
            st.session_state["locations"] = [
                {
                    "place_name": place["place_name"],
                    "address_name": place["address_name"],
                    "latitude": float(place["y"]),
                    "longitude": float(place["x"]),
                }
                for place in results
            ]
        else:
            st.warning("검색 결과가 없습니다.")
            st.session_state["locations"] = []

    # 검색 결과 선택 필드 (항상 표시)
    selected_place = st.selectbox(
        "검색 결과를 선택하세요:",
        [loc["place_name"] for loc in st.session_state["locations"]],
        key="selected_place",
    )

    # 선택한 장소 업데이트
    for loc in st.session_state["locations"]:
        if loc["place_name"] == selected_place:
            st.session_state["selected_location"] = loc
            break

    # 지도 및 선택된 장소 정보 표시 (항상 표시)
    if st.session_state["selected_location"]:
        selected_location = st.session_state["selected_location"]
        st.map(
            pd.DataFrame(
                [{"latitude": selected_location["latitude"], "longitude": selected_location["longitude"]}]
            )
        )
        st.write(f"**선택된 장소:** {selected_location['place_name']}, {selected_location['address_name']}")

    # 그룹 생성 버튼
    if st.button("그룹 생성", key="create_group_button"):
        if not group_name or not st.session_state["selected_location"]:
            st.error("모든 필수 입력 항목을 입력해주세요.")
        else:
            current_date = group.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # datetime 모듈로 수정
            conn = app.create_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()

                # 약속 날짜와 시간이 있는 경우와 없는 경우의 INSERT 문
                if add_schedule:
                    cursor.execute(
                        """
                        INSERT INTO "group" (group_name, group_creator, category, location, meeting_date, meeting_time, update_date, modify_date, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, '진행 중')
                        """,
                        (group_name, user_id, category[0], selected_location["place_name"], meeting_date,
                         meeting_time_str,
                         current_date, current_date),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO "group" (group_name, group_creator, category, location, update_date, modify_date, status)
                        VALUES (?, ?, ?, ?, ?, ?, '진행 중')
                        """,
                        (group_name, user_id, category[0], selected_location["place_name"], current_date,
                         current_date),
                    )

                group_id = cursor.lastrowid  # 생성된 그룹의 ID 가져오기

                # 그룹 생성자를 group_member 테이블에 추가
                cursor.execute(
                    """
                    INSERT INTO group_member (group_id, user_id, role, joined_at)
                    VALUES (?, ?, 'admin', ?)
                    """,
                    (group_id, user_id, current_date),
                )

                conn.commit()
                st.success(f"'{group_name}' 그룹이 성공적으로 생성되었습니다!")
            except sqlite3.Error as e:
                st.error(localization.get_text("db_error").format(e)) 
            finally:
                conn.close()

def join_group(group_name):
    """그룹 참여"""
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("로그인이 필요합니다.")
        return

    conn = sqlite3.connect("zip.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT group_id FROM "group" WHERE group_name = ?
        """, (group_name,))
        group_id = cursor.fetchone()
        if not group_id:
            st.error("그룹을 찾을 수 없습니다.")
            return

        cursor.execute("""
            INSERT INTO group_member (group_id, user_id, role)
            VALUES (?, ?, 'member')
        """, (group_id[0], user_id))
        conn.commit()
        st.success(f"'{group_name}' 그룹에 성공적으로 참여하였습니다.")
    except sqlite3.IntegrityError:
        st.warning("이미 해당 그룹의 멤버입니다.")
    except sqlite3.Error as e:
        st.error(f"DB 오류: {e}")
    finally:
        conn.close()

#그룹 검색 페이지
@st.dialog("그룹 검색")
def search_groups_page():
    # 검색 기준 선택
    search_criteria = st.selectbox(
        "검색 기준을 선택하세요",
        ["이름", "날짜", "카테고리"],
        index=0
    )

    user_input = None
    if search_criteria == "이름":
        user_input = st.text_input("그룹 이름을 입력하세요")
    elif search_criteria == "날짜":
        user_input = st.date_input("약속 날짜를 선택하세요")
    elif search_criteria == "카테고리":
        dao = group.CategoryDAO()
        categories = dao.get_all_categories()
        if not categories:
            st.error("등록된 카테고리가 없습니다.")
            return
        user_input = st.selectbox(
            "카테고리를 선택하세요",
            options=categories,
            format_func=lambda x: x[1]
        )

    if st.button("검색"):
        conn = sqlite3.connect("zip.db")
        try:
            cursor = conn.cursor()
            query = ""
            params = ()

            # 검색 기준별 쿼리 작성
            if search_criteria == "이름":
                query = """
                    SELECT g.group_name, g.group_creator, g.meeting_date, g.meeting_time, c.category, l.location_name, COUNT(gm.user_id) as current_members
                    FROM "group" g
                    LEFT JOIN food_categories c ON g.category = c.category_id
                    LEFT JOIN locations l ON g.location = l.location_id
                    LEFT JOIN group_member gm ON g.group_id = gm.group_id
                    WHERE g.group_name LIKE ?
                    GROUP BY g.group_id
                """
                params = (f"%{user_input}%",)

            elif search_criteria == "날짜":
                query = """
                    SELECT g.group_name, g.group_creator, g.meeting_date, g.meeting_time, c.category, l.location_name, COUNT(gm.user_id) as current_members
                    FROM "group" g
                    LEFT JOIN food_categories c ON g.category = c.category_id
                    LEFT JOIN locations l ON g.location = l.location_id
                    LEFT JOIN group_member gm ON g.group_id = gm.group_id
                    WHERE g.meeting_date = ?
                    GROUP BY g.group_id
                """
                params = (user_input,)

            elif search_criteria == "카테고리":
                query = """
                    SELECT g.group_name, g.group_creator, g.meeting_date, g.meeting_time, c.category, l.location_name, COUNT(gm.user_id) as current_members
                    FROM "group" g
                    LEFT JOIN food_categories c ON g.category = c.category_id
                    LEFT JOIN locations l ON g.location = l.location_id
                    LEFT JOIN group_member gm ON g.group_id = gm.group_id
                    WHERE g.category = ?
                    GROUP BY g.group_id
                """
                params = (user_input[0],)

            # 쿼리 실행
            cursor.execute(query, params)
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(localization.get_text("db_error").format(e)) 
            return
        finally:
            conn.close()

        # 결과 표시
        if not groups:
            st.warning("검색 결과가 없습니다.")
        else:
            for group_name, group_creator, meeting_date, meeting_time, category, location_name, current_members in groups:
                st.markdown(f"**그룹 이름:** {group_name}")
                st.markdown(f"**그룹장:** {group_creator}")
                st.markdown(f"**현재 인원수:** {current_members}")
                st.markdown(f"**약속 날짜:** {meeting_date}")
                st.markdown(f"**약속 시간:** {meeting_time}")
                st.markdown(f"**카테고리:** {category}")
                st.markdown(f"**장소:** {location_name}")
                # 그룹 참여 버튼 추가
                if st.button(f"그룹 참여", key=f"join_{group_name}"):
                    join_group(group_name)

@st.dialog("그룹 삭제")
def group_delete_page():
    # 그룹 ID 가져오기 (세션에 저장된 그룹 ID)
    group_id = st.session_state.get("group_id_to_delete")
    if not group_id:
        st.error("삭제할 그룹 ID를 찾을 수 없습니다.")
        return

    # DB 연결하여 그룹명 가져오기
    conn = sqlite3.connect('zip.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM \"group\" WHERE group_id = ?", (group_id,))
        group_name = cursor.fetchone()
        if not group_name:
            st.error("그룹을 찾을 수 없습니다.")
            return
        group_name = group_name[0]  # 첫 번째 컬럼인 group_name 가져오기
    except sqlite3.Error as e:
        st.error(localization.get_text("db_error").format(e)) 
        return
    finally:
        conn.close()

    # 선택된 그룹 이름을 가져와서 확인 메시지 표시
    st.markdown(f"**정말 '{group_name}' 그룹을 삭제하시겠습니까?**")

    # 예 버튼
    if st.button("예", key=f"delete_yes_{group_id}"):
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인 정보가 없습니다.")
            return

        # DB 연결하여 그룹 삭제
        try:
            conn = sqlite3.connect('zip.db')
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM \"group\" WHERE group_id = ? AND group_creator = ?",
                (group_id, user_id),
            )
            if cursor.rowcount == 0:
                st.error("그룹장만 그룹을 삭제할 수 있습니다.")
            else:
                conn.commit()
                st.success(f"'{group_name}' 그룹이 삭제되었습니다!")
        except sqlite3.Error as e:
            st.error(localization.get_text("db_error").format(e)) 
        finally:
            conn.close()

    # 아니오 버튼
    if st.button("아니오", key=f"delete_no_{group_id}"):
        st.info("그룹 삭제가 취소되었습니다.")
        del st.session_state["group_id_to_delete"]  # 세션에서 그룹 ID 삭제

@st.dialog("그룹 수정")
def group_update_page():
    # 그룹 ID 가져오기 (세션에 저장된 그룹 ID)
    group_id = st.session_state.get("group_id_to_edit")
    if not group_id:
        st.error("수정할 그룹 ID를 찾을 수 없습니다.")
        return

    # DB 연결하여 그룹명 가져오기
    conn = sqlite3.connect('zip.db')
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT group_name FROM \"group\" WHERE group_id = ?", (group_id,))
        group_name = cursor.fetchone()
        if not group_name:
            st.error("그룹을 찾을 수 없습니다.")
            return
        group_name = group_name[0]  # 첫 번째 컬럼인 group_name 가져오기
    except sqlite3.Error as e:
        st.error(localization.get_text("db_error").format(e)) 
        return
    finally:
        conn.close()

    # 그룹 수정 폼 바로 표시
    st.markdown(f"**'{group_name}' 그룹을 수정합니다.**")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("로그인 정보가 없습니다.")
        return

    try:
        conn = sqlite3.connect('zip.db')
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT group_name, category, status, meeting_date, meeting_time
            FROM "group"
            WHERE group_id = ? 
            """,
            (group_id,),
        )
        group_data = cursor.fetchone()
        if not group_data:
            st.error("그룹 정보를 불러올 수 없습니다.")
            return

        group_name = st.text_input("그룹 이름", value=group_data[0])
        dao = group.CategoryDAO()
        categories = dao.get_all_categories()
        selected_category = st.selectbox(
            "카테고리 선택",
            options=categories,
            index=[cat[0] for cat in categories].index(group_data[1]),
            format_func=lambda x: x[1],
        )

        # 약속 날짜와 시간 추가
        if group_data[3] is not None:
            meeting_date = st.date_input("약속 날짜", value=group.datetime.strptime(group_data[3], "%Y-%m-%d").date())
        else:
            meeting_date = st.date_input("약속 날짜", value=group.datetime.today().date())  # 기본값: 오늘 날짜

        if group_data[4] is not None:
            meeting_time = st.time_input("약속 시간", value=group.datetime.strptime(group_data[4], "%H:%M:%S").time())
        else:
            meeting_time = st.time_input("약속 시간", value=group.datetime.now().time())  # 기본값: 현재 시간

        status_choices = ["진행 중", "완료", "취소"]
        selected_status = st.selectbox("그룹 상태", options=status_choices, index=status_choices.index(group_data[2]))

        # 그룹 수정 버튼
        if st.button("그룹 수정"):
            try:
                conn = sqlite3.connect('zip.db')
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE "group"
                    SET group_name = ?, category = ?, status = ?, meeting_date = ?, meeting_time = ?, modify_date = ?
                    WHERE group_id = ? 
                    """,
                    (
                        group_name,
                        selected_category[0],
                        selected_status,
                        meeting_date.strftime("%Y-%m-%d"),
                        meeting_time.strftime("%H:%M:%S"),
                        group.datetime.now(),
                        group_id,
                    ),
                )
                conn.commit()
                st.success(f"'{group_name}' 그룹이 성공적으로 수정되었습니다!")
            except sqlite3.Error as e:
                st.error(localization.get_text("db_error").format(e)) 
            finally:
                conn.close()

    except sqlite3.Error as e:
        st.error(localization.get_text("db_error").format(e)) 
        return
    finally:
        conn.close()




 

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
    'Group page' : my_groups_page,
    'ID PW 변경': id_pw_change_page,
    'Detail group' : detail_group,
}

page_functions.update({ 
    "FriendList": lambda: friend.show_friend_list(st.session_state["user_id"]),
    "AddFriend": lambda: friend.add_friend(
        st.session_state["user_id"],
        st.text_input("추가할 친구 ID", key="add_friend_id")
    ),
    "FriendRequests": lambda: friend.show_friend_requests_page(st.session_state["user_id"]),
    "BlockedList": lambda: friend.show_blocked_list(st.session_state["user_id"]),
    "DeleteFriend": lambda: friend.delete_friend(
        st.session_state["user_id"], 
        st.text_input("삭제할 친구 ID", key="delete_friend_id")
    ),
})


# 현재 페이지 렌더링
if st.session_state.current_page in page_functions:
    page_functions[st.session_state.current_page]()  # 매핑된 함수 호출
else:
    st.error("페이지를 찾을 수 없습니다.")  # 잘못된 페이지 처리
