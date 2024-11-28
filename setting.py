import streamlit as st
import sqlite3
from typing import Dict
import os
from localization import Localization

# 초기화
if 'localization' not in st.session_state:
    st.session_state.localization = Localization(lang ='ko')  # 기본 언어는 한국어로 설정됨
# 현재 언어 설정 초기화
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'ko'  # 기본값으로 한국어 설정

localization = st.session_state.localization

def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # results as dictionary-like
    return conn

class LikeButton:
   def __init__(self):
       self.lk = st.session_state
       if "like" not in self.lk:
           self.lk.like = {
               "current_like": "not_like",
               "refreshed": True,
               "not_like": {
                   "theme.base": "like",
                   "button_face": "좋아요 취소"
               },
               "like": {
                   "theme.base": "not_like",
                   "button_face": "좋아요"
               },
           }
       if "posts" not in st.session_state:
           st.session_state.posts = []
           self.fetch_and_store_posts()


   def create_connection(self):
       conn = sqlite3.connect('zip.db')
       conn.row_factory = sqlite3.Row  # Return results as dictionaries
       return conn


   def fetch_and_store_posts(self):
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT p_id, p_title FROM posting")
       posts = cursor.fetchall()
       conn.close()


       # Store the posts in session state
       st.session_state.posts = posts


   def fetch_liked_posts(self):
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT p_id, p_title FROM posting WHERE like_num > 0")
       liked_posts = cursor.fetchall()
       conn.close()


       return liked_posts


   def display_liked_posts(self):
       liked_posts = self.fetch_liked_posts()


       # Display liked posts with the like button
       if liked_posts:
           for post in liked_posts:
               post_id, post_title = post
               st.write(f"Liked Post ID: {post_id}, Title: {post_title}")
       else:
           st.write("좋아요를 누른 포스팅이 없습니다.")

class Account:
    def __init__(self, user_id, user_email):
        self.user_id = user_id
        self.user_email = user_email

    def get_user_info(self) -> Dict:
        return {"user_id": self.user_id, "user_email": self.user_email}

    def update_email(self, new_email: str):
        # 실제 데이터베이스에서 이메일 업데이트
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET user_email = ? WHERE user_id = ?", (new_email, self.user_id))
        conn.commit()


class ThemeManager:
    def __init__(self):
        self.th = st.session_state
        if "themes" not in self.th:
            self.th.themes = {
                "current_theme": self.get_saved_theme(),  # Load saved theme from DB or default to light
            }

    def get_saved_theme(self):
        # 저장된 테마 가져오기
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT current_theme FROM settings WHERE id=1')
        theme = cursor.fetchone()
        conn.close()
        return theme[0] if theme else 'dark'

    def save_theme(self, theme):
        # 현재 테마를 데이터베이스에 저장
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE settings SET current_theme=? WHERE id=1', (theme,))
        conn.commit()
        conn.close()

    def change_theme(self):
        # 테마 변경
        previous_theme = self.th.themes["current_theme"]
        new_theme = "light" if previous_theme == "dark" else "dark"

        # 테마 적용
        theme_dict = self.th.themes[new_theme]
        for key, value in theme_dict.items():
            if key.startswith("theme"):
                st._config.set_option(key, value)

        # 데이터베이스 저장 및 세션 상태 업데이트
        self.save_theme(new_theme)
        self.th.themes["current_theme"] = new_theme
        st.rerun()  # UI 새로고침

    def render_button(self):
        # 동적으로 버튼 텍스트 가져오기
        current_theme = self.th.themes["current_theme"]
        button_label = (
            localization.get_text("dark_mode")
            if current_theme == "light"
            else localization.get_text("light_mode")
        )

        # 버튼 렌더링 및 클릭 이벤트 처리
        if st.button(button_label, use_container_width=True):
            self.change_theme()

    def select_language(self):
        lang_options = ['ko', 'en', 'jp']  # 지원하는 언어 목록

        # 드롭다운을 왼쪽에 배치
        selected_lang = st.selectbox(
            localization.get_text("select_language"),  # "언어 선택" 문자열을 로컬라이제이션에서 가져옴
            lang_options,
            index=lang_options.index(st.session_state.current_language),  # 현재 언어에 맞게 기본값 설정
            key="language_select",
            help=localization.get_text("choose_language")  # 툴팁 문자열
        )

        if st.session_state.current_language != selected_lang:
            st.session_state.current_language = selected_lang  # 선택한 언어로 변경
            st.session_state.localization.lang = selected_lang  # Localization 객체의 언어도 변경
            st.rerun()  # 페이지를 다시 로드


class UserProfile:
    def __init__(self, upload_folder="profile_pictures"):
        self.db_name = 'zip.db'
        self.upload_folder = upload_folder
        self.default_profile_picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        os.makedirs(self.upload_folder, exist_ok=True)

    def create_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
        return conn

    def save_file(self, uploaded_file):
        # 이미지 저장 후 경로 반환
        if uploaded_file is not None:
            file_path = os.path.join(self.upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        return None

    # 사용자 이미지 가져오기
    def get_user_profile(self, user_id):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        connection.close()
        return user

    # 프로필 업데이트
    def update_profile_picture(self, user_id, image_path):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE user
        SET profile_picture_path = ?
        WHERE user_id = ?
        """, (image_path, user_id))
        connection.commit()
        connection.close()

    def display_profile(self, user_id):
        user = self.get_user_profile(user_id)
        if user:
            st.write(f"User Email: {user['user_email']}")
            profile_picture = user['profile_picture_path']

            # 파일이 없거나 경로가 잘못된 경우 기본 이미지로 대체
            if not profile_picture or not os.path.exists(profile_picture):
                profile_picture = self.default_profile_picture

            st.image(profile_picture, caption=user_id, width=300)
        else:
            st.error("사용자 정보를 찾을 수 없습니다.")

    def upload_new_profile_picture(self, user_id):
        st.button("프로필 사진 변경", use_container_width=True)
        uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])

        if st.button("업로드"):
            if uploaded_file is not None:
                image_path = self.save_file(uploaded_file)
                self.update_profile_picture(user_id, image_path)
                st.success("프로필 사진이 성공적으로 업데이트되었습니다.")
                st.rerun()
            else:
                st.error("파일을 업로드해주세요.")


# SetView class to handle UI rendering
class SetView:
    def __init__(self, user_id, user_email):
        self.account = Account(user_id=user_id, user_email=user_email)
        self.user_profile = UserProfile()
        self.theme_manager = ThemeManager()

    def render_user_profile(self):
        user_info = self.account.get_user_info()
        # Display user profile
        self.user_profile.display_profile(user_info["user_id"])

        # Edit Profile Button (popup simulation)
        with st.expander(localization.get_text("edit_my_info")):
            # Change Email
            new_email = st.text_input(localization.get_text("new_email_address"), value=user_info["user_email"])
            if st.button(localization.get_text("change_email")):
                self.account.update_email(new_email)
                st.success(localization.get_text("email_updated"))
                st.rerun()

            # Profile Picture Upload
            uploaded_file = st.file_uploader(localization.get_text("upload_new_profile_picture"), type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image_path = self.user_profile.save_file(uploaded_file)
                self.user_profile.update_profile_picture(user_info["user_id"], image_path)
                st.success(localization.get_text("profile_picture_updated"))
                st.rerun()

    def render_alarm_settings(self):
        alarm_enabled = st.button(localization.get_text("set_alarm"), use_container_width=True)
        if alarm_enabled:
            st.write(localization.get_text("alarm_set"))
        else:
            st.write(localization.get_text("alarm_disabled"))

    def render_posts(self):
        # Display liked posts toggle button
        with st.expander(localization.get_text("favorites"), icon='💗'):
            st.write(localization.get_text("no_liked_posts"))




# 페이지 전환 함수
def change_page(page_name):
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.session_state["current_page"] != page_name:
        st.session_state["history"].append(st.session_state["current_page"])
    st.session_state["current_page"] = page_name
    st.session_state.localization = st.session_state.localization  # 언어 변경 후 localization 업데이트

    st.rerun()


# Main function
def main():
    st.title("My Page")

    # Create the SetView object and render the views
    view = SetView()
    view.render_user_profile()
    view.render_alarm_settings()
    theme_manager = ThemeManager()
    theme_manager.render_button()
    theme_manager.select_language()
    view.render_posts()


if __name__ == "__main__":

        self.theme_manager = ThemeManager()

def render_user_profile(self):
        user_info = self.account.get_user_info()
        # Display user profile
        self.user_profile.display_profile(user_info["user_id"])

        # Edit Profile Button (popup simulation)
        with st.expander(localization.get_text("edit_my_info")):
            # Change Email
            new_email = st.text_input(localization.get_text("new_email_address"), value=user_info["user_email"])
            if st.button(localization.get_text("change_email")):
                self.account.update_email(new_email)
                st.success(localization.get_text("email_updated"))
                st.rerun()

            # Profile Picture Upload
            uploaded_file = st.file_uploader(localization.get_text("upload_new_profile_picture"), type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image_path = self.user_profile.save_file(uploaded_file)
                self.user_profile.update_profile_picture(user_info["user_id"], image_path)
                st.success(localization.get_text("profile_picture_updated"))
                st.rerun()

def render_alarm_settings(self):
        alarm_enabled = st.button(localization.get_text("set_alarm"), use_container_width=True)
        if alarm_enabled:
            st.write(localization.get_text("alarm_set"))
        else:
            st.write(localization.get_text("alarm_disabled"))

def render_posts(self):
        # Display liked posts toggle button
        with st.expander(localization.get_text("favorites"), icon='💗'):
            st.write(localization.get_text("no_liked_posts"))




# 페이지 전환 함수
def change_page(page_name):
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.session_state["current_page"] != page_name:
        st.session_state["history"].append(st.session_state["current_page"])
    st.session_state["current_page"] = page_name
    st.session_state.localization = st.session_state.localization  # 언어 변경 후 localization 업데이트

    st.rerun()


