import pandas as pd
import streamlit as st
import sqlite3
import bcrypt
import database
import login
import posting
import friend
import setting

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
    col1, col2 = st.columns(2)
    with col1:
        st.title("맛ZIP")
    with col2:
        col3, col4 = st.columns(2)
        with col3:
            if st.button("로그인", use_container_width=True):
                change_page('Login')
        with col4:
            if st.button("회원가입", use_container_width=True):
                change_page('Signup')

    # 중앙 포스팅 리스트
    st.title("추천 맛집 포스트")

    # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
    post_manager = posting.PostManager()  # 인스턴스 생성
    post_manager.display_posts_on_home()  # display_posts_on_home 메서드 호출


#로그인 페이지
def login_page():

    st.title("로그인")
    user_id = st.text_input("아이디")
    if 'user_id' not in st.session_state:
        st.session_state.user = user_id
    user_password = st.text_input("비밀번호", type='password')

    if st.button("로그인"):
        # 입력 값 검증
        if not user_id or not user_password:
            st.error("아이디와 비밀번호를 입력해 주세요.")
        else:
            sign_in = login.SignIn(user_id, user_password)
            sign_in.sign_in_event()
    if st.button("ID/PW 찾기"):
        change_page()

#회원가입 페이지
def signup_page():
    st.title("회원가입")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')
    email = st.text_input("이메일")

    if st.button("회원가입"):
        # 입력 값 검증 (간단한 예시)
        if not user_id or not user_password or not email:
            st.error("모든 필드를 입력해 주세요.")
        else:
            signup = login.SignUp(user_id, user_password, email)
            signup.sign_up_event()

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
        st.image(profile_image_url, use_container_width=100)
    with col2:
        st.write(f"**{user_id}**")
    with col3:
        if st.button("로그아웃"):
            st.warning("로그아웃 되었습니다.")
            st.session_state.user.clear()  # 세션 초기화
            change_page('Home')
    with col4:
        if st.button("내 프로필"):
            change_page("Setting")

    # 중앙 포스팅 리스트
    st.title("추천 맛집 포스트")

    # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
    post_manager = posting.PostManager()  # 인스턴스 생성
    post_manager.display_posts_on_home()  # display_posts_on_home 메서드 호출
    if st.button("더보기"):
        change_page("View Post")

    # 사이드바 제목
    st.sidebar.title('친구 목록')

    # 사이드바에 사용자 프로필과 버튼들을 한 줄에 배치
    st.sidebar.markdown(
        """
        <div class="friend-buttons">
            <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #4CAF50; color: white; border: none; cursor: pointer;">친구찾기</button>
            <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #FFA500; color: white; border: none; cursor: pointer;">친구 대기</button>
            <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #FF6347; color: white; border: none; cursor: pointer;">차단/해제</button>
            <button style="padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #DC143C; color: white; border: none; cursor: pointer;">삭제</button>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 친구 목록 섹션
    st.sidebar.markdown("## 친구 목록")

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

# 게시물 등록 페이지
def upload_post() :
    st.header("게시물 등록")
    title = st.text_input("게시물 제목")
    content = st.text_area("게시물 내용")
    image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'])
    file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'])


    # 카테고리 선택을 위한 Selectbox
    post_manager = posting.PostManager('zip.db')  # DB 경로 설정
    category_names = post_manager.get_category_names()  # 카테고리 이름만 가져옴


    # Selectbox에서 카테고리 선택
    selected_category_name = st.selectbox("카테고리", category_names)


   # 선택한 카테고리 이름에 해당하는 category_id 구하기
    categories = post_manager.get_category_options()
    category_dict = {category[1]: category[0] for category in categories}
    selected_category_id = category_dict[selected_category_name]


    location_search = posting.LocationSearch()
    location_search.display_location_on_map()


    if st.button("게시물 등록"):
       if title and content:
           post_manager.add_post(title, content, image_file, file_file,selected_category_id)
           st.success("게시물이 등록되었습니다.")
       else:
           st.error("제목과 내용을 입력해 주세요.")

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
}

# 현재 페이지 렌더링
if st.session_state.current_page in page_functions:
    page_functions[st.session_state.current_page]()  # 매핑된 함수 호출
else:
    st.error("페이지를 찾을 수 없습니다.")  # 잘못된 페이지 처리
