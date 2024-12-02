import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, func, CheckConstraint, Date, Time,
)
from sqlalchemy.orm import sessionmaker,relationship
import string
import bcrypt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from datetime import datetime
import secrets
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import os
import requests

# SQLAlchemy Base 선언
Base = declarative_base()

# 데이터베이스 URL 설정
DATABASE_URL = "sqlite:///zip.db"

# 데이터베이스 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

class Localization:
    def __init__(self, lang='ko'):

        self.lang = lang
        self.translations = self.load_translations()

    def load_translations(self):

        return {
            "ko": {
                "dark_mode": "어두운 모드 🌜",
                "light_mode": "밝은 모드 🌞",
                "select_language": "언어 선택 🌐",
                "choose_language": "언어를 선택하세요.",
                "edit_my_info": "내 정보 수정",
                "new_email_address": "새 이메일 주소",
                "change_email": "이메일 변경",
                "email_updated": "이메일이 변경되었습니다.",
                "upload_new_profile_picture": "새 프로필 사진 업로드",
                "profile_picture_updated": "프로필 사진이 성공적으로 업데이트되었습니다.",
                "set_alarm": "알람 설정",
                "alarm_set": "알람이 설정되었습니다.",
                "alarm_disabled": "알람이 해제되었습니다.",
                "favorites": "관심목록",
                "no_liked_posts": "좋아요를 누른 포스팅이 없습니다.",
                "my_page": "나의 페이지",
                "user_email": "사용자 이메일",
                "user_info_not_found": "사용자 정보를 찾을 수 없습니다.",
                "upload": "업로드",
                "upload_file_error": "파일을 업로드해주세요.",
                "email_in_use_error": "이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.",
                "id_in_use_error": "이미 사용 중인 아이디입니다. 다른 아이디를 사용해주세요.",
                "signup_unknown_error": "회원가입 중 알 수 없는 오류가 발생했습니다.",
                "signup_success": "회원가입이 완료되었습니다!",
                "db_error": "DB 오류: {error}",
                "password_min_length_error": "비밀번호는 최소 8자 이상이어야 합니다.",
                "invalid_email_error": "유효하지 않은 이메일 주소입니다.",
                "wrong_password_error": "비밀번호가 잘못되었습니다.",
                "id_not_found_error": "아이디가 존재하지 않습니다.",
                "login_button": "로그인",
                "signup_button": "회원가입",
                "forgot_button": "ID/PW 찾기",
                "id_pw_change_title": "ID/PW 변경",
                "no_user_error": "사용자 정보가 없습니다. 다시 로그인해주세요.",
                "select_change_action": "변경할 항목을 선택하세요",
                "change_id": "ID 변경",
                "change_pw": "비밀번호 변경",
                "next_button": "다음",
                "enter_new_value": "새로 사용할 {action}를 입력하세요",
                "save_button": "저장",
                "id_change_success": "ID가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.",
                "pw_change_success": "비밀번호가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.",
                "login_title": "로그인",
                "user_id_input": "아이디",
                "password_input": "비밀번호",
                "login_error_empty": "아이디와 비밀번호를 입력해 주세요.",
                "login_error_failed": "로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.",
                "signup_title": "회원가입",
                "email_input": "이메일",
                "signup_error_empty": "모든 필드를 입력해 주세요.",
                "logout_button": "로그아웃",
                "logout_success": "로그아웃 되었습니다.",
                "profile_button": "내 프로필",
                "view_post_button": "게시물 보기",
                "group_management": "그룹 관리",
                "group_management_button": "그룹 관리",
                "friend_management": "친구 관리",
                "my_friend_list_button": "내 친구 리스트",
                "my_friend_list_title": "내 친구 리스트",
                "back_button": "뒤로가기 ↩️",
                "enter_id_prompt": "ID를 입력하세요:",
                "send_friend_request_button": "친구 요청 보내기",
                "friend_requests_button": "친구 대기",
                "block_button": "차단",
                "unblock_button": "차단 해제",
                "delete_button": "삭제",
                "upload_post_header": "게시물 등록",
                "post_title_input": "게시물 제목",
                "post_content_input": "게시물 내용",
                "image_file_upload": "이미지 파일",
                "general_file_upload": "일반 파일",
                "category_select": "카테고리",
                "post_register_button": "게시물 등록",
                "post_register_success": "게시물이 등록되었습니다.",
                "post_register_error": "제목과 내용을 입력해 주세요.",
                "edit_post_header": "게시물 수정",
                "edit_post_id_input": "수정할 게시물 ID",
                "location_id_input": "위치 ID",
                "category_id_input": "카테고리 ID",
                "edit_post_button": "게시물 수정",
                "edit_post_success": "게시물이 수정되었습니다.",
                "edit_post_not_found_error": "해당 게시물이 존재하지 않습니다.",
                "delete_post_header": "게시물 삭제",
                "delete_post_id_input": "삭제할 게시물 ID",
                "delete_post_button": "게시물 삭제",
                "delete_post_success": "게시물이 삭제되었습니다.",
                "delete_post_not_found_error": "해당 게시물이 존재하지 않습니다.",
                "view_post_header": "게시물 목록",
                "upload_post_button": "글 작성",
                "my_page_header": "내 페이지",
                "user_manager_page_title": "사용자 관리 페이지",
                "email_input_prompt": "이메일을 입력하세요:",
                "confirm_button": "확인",
                "password_recovery_email_sent": "비밀번호 복구 메일을 전송했습니다",
                "email_not_registered_warning": "등록되지 않은 이메일입니다.",
                "Recommended Restaurant Posts": "추천 맛집 포스트",
                "group_button": "그룹",
                "login_title1": "로그인",
                "group_page_title": "그룹 페이지",
                "create_group_button": "그룹 생성 🧑‍🤝‍🧑",
                "search_group_button": "그룹 검색 🔍",
                "login_required_error": "로그인이 필요합니다.",
                "no_joined_groups": "참여 중인 그룹이 없습니다."
        
        
            },
            "en": {
                "dark_mode": "Dark Mode 🌜",
                "light_mode": "Light Mode 🌞",
                "select_language": "Select Language 🌐",
                "choose_language": "Choose a language.",
                "edit_my_info": "Edit My Info",
                "new_email_address": "New Email Address",
                "change_email": "Change Email",
                "email_updated": "Email has been updated.",
                "upload_new_profile_picture": "Upload New Profile Picture",
                "profile_picture_updated": "Profile picture updated successfully.",
                "set_alarm": "Set Alarm",
                "alarm_set": "Alarm has been set.",
                "alarm_disabled": "Alarm has been disabled.",
                "favorites": "Favorites",
                "no_liked_posts": "No liked posts found.",
                "my_page": "My Page",
                "user_email": "User Email",
                "user_info_not_found": "User information could not be found.",
                "upload": "Upload",
                "upload_file_error": "Please upload a file.",
                "email_in_use_error": "This email is already in use. Please use another email.",
                "id_in_use_error": "This ID is already in use. Please use another ID.",
                "signup_unknown_error": "An unknown error occurred during signup.",
                "signup_success": "Signup completed successfully!",
                "db_error": "DB Error: {error}",
                "password_min_length_error": "Password must be at least 8 characters.",
                "invalid_email_error": "Invalid email address.",
                "wrong_password_error": "Incorrect password.",
                "id_not_found_error": "The ID does not exist.",
                "logout_button": "Logout",
                "logout_success": "Logout successful",
                "login_button": "Login",
                "signup_button": "Sign Up",
                "forgot_button": "Find ID/PW",
                "id_pw_change_title": "ID/PW Change",
                "no_user_error": "User information not found. Please log in again.",
                "select_change_action": "Select an item to change",
                "change_id": "Change ID",
                "change_pw": "Change Password",
                "next_button": "Next",
                "enter_new_value": "Enter a new {action}",
                "save_button": "Save",
                "id_change_success": "ID successfully changed. Logging out and returning to the home page.",
                "pw_change_success": "Password successfully changed. Logging out and returning to the home page.",
                "login_title": "Login",
                "user_id_input": "User ID",
                "password_input": "Password",
                "login_error_empty": "Please enter your user ID and password.",
                "login_error_failed": "Login failed. Please check your user ID and password.",
                "signup_title": "Sign Up",
                "email_input": "Email",
                "signup_error_empty": "Please fill in all fields.",
                "profile_button": "My Profile",
                "view_post_button": "View Post",
                "group_management": "Group Management",
                "group_management_button": "Manage Groups",
                "friend_management": "Friend Management",
                "my_friend_list_button": "My Friend List",
                "my_friend_list_title": "My Friend List",
                "enter_id_prompt": "Enter ID:",
                "send_friend_request_button": "Send Friend Request",
                "friend_requests_button": "Friend Requests",
                "block_button": "Block",
                "unblock_button": "Unblock",
                "delete_button": "Delete",
                "upload_post_header": "Upload Post",
                "post_title_input": "Post Title",
                "post_content_input": "Post Content",
                "image_file_upload": "Image File",
                "general_file_upload": "General File",
                "category_select": "Category",
                "post_register_button": "Register Post",
                "post_register_success": "Post has been registered.",
                "post_register_error": "Please enter both title and content.",
                "back_button": "Back ↩️",
                "edit_post_header": "Edit Post",
                "edit_post_id_input": "Edit Post ID",
                "location_id_input": "Location ID",
                "category_id_input": "Category ID",
                "edit_post_button": "Update Post",
                "edit_post_success": "Post has been updated.",
                "edit_post_not_found_error": "Post not found.",
                "delete_post_header": "Delete Post",
                "delete_post_id_input": "Delete Post ID",
                "delete_post_button": "Delete Post",
                "delete_post_success": "Post has been deleted.",
                "delete_post_not_found_error": "Post not found.",
                "view_post_header": "Post List",
                "upload_post_button": "Create Post",
                "my_page_header": "My Page",
                "user_manager_page_title": "User Management Page",
                "email_input_prompt": "Enter your email:",
                "confirm_button": "Confirm",
                "password_recovery_email_sent": "Password recovery email has been sent.",
                "email_not_registered_warning": "The email is not registered.",
                "Recommended Restaurant Posts": "Recommended Restaurant Posts",
                "group_button": "Group",
                "login_title1": "login",
                "group_page_title": "Group Page",
                "create_group_button": "Create Group 🧑‍🤝‍🧑",
                "search_group_button": "Search Groups 🔍",
                "login_required_error": "Login is required.",
                "no_joined_groups": "You are not part of any groups."
        
        
            },
            "jp": {
                "dark_mode": "ダークモード 🌜",
                "light_mode": "ライトモード 🌞",
                "select_language": "言語を選択 🌐",
                "choose_language": "言語を選んでください。",
                "edit_my_info": "情報を編集",
                "new_email_address": "新しいメールアドレス",
                "change_email": "メールを変更",
                "email_updated": "メールが更新されました。",
                "upload_new_profile_picture": "新しいプロフィール写真をアップロード",
                "profile_picture_updated": "プロフィール写真が正常に更新されました。",
                "set_alarm": "アラームを設定",
                "alarm_set": "アラームが設定されました。",
                "alarm_disabled": "アラームが無効になりました。",
                "favorites": "お気に入り",
                "no_liked_posts": "いいねした投稿がありません。",
                "my_page": "マイページ",
                "user_email": "ユーザーのメールアドレス",
                "user_info_not_found": "ユーザー情報が見つかりませんでした。",
                "change_profile_picture": "プロフィール写真を変更",
                "upload": "アップロード",
                "upload_file_error": "ファイルをアップロードしてください。",
                "email_in_use_error": "このメールアドレスは既に使用されています。他のメールアドレスを使用してください。",
                "id_in_use_error": "このIDは既に使用されています。他のIDを使用してください。",
                "signup_unknown_error": "サインアップ中に不明なエラーが発生しました。",
                "signup_success": "サインアップが完了しました！",
                "db_error": "データベースエラー: {error}",
                "password_min_length_error": "パスワードは8文字以上である必要があります。",
                "wrong_password_error": "パスワードが間違っています。",
                "id_not_found_error": "IDが存在しません。",
                "logout_button": "ログアウト",
                "logout_success": "ログアウト完了",
                "forgot_button": "ID/PW検索",
                "id_pw_change_title": "ID/PW 変更",
                "no_user_error": "ユーザー情報が見つかりません。再度ログインしてください。",
                "select_change_action": "変更する項目を選択してください",
                "change_id": "IDを変更する",
                "change_pw": "パスワードを変更する",
                "next_button": "次へ",
                "enter_new_value": "新しい{action}を入力してください",
                "save_button": "保存",
                "id_change_success": "IDが正常に変更されました。ログアウトしてホームページに戻ります。",
                "pw_change_success": "パスワードが正常に変更されました。ログアウトしてホームページに戻ります。",        
                "login_title": "ログイン",
                "user_id_input": "ユーザーID",
                "password_input": "パスワード",
                "login_button": "ログイン",
                "login_error_empty": "ユーザーIDとパスワードを入力してください。",
                "login_error_failed": "ログインに失敗しました。ユーザーIDまたはパスワードを確認してください。",
                "signup_title": "サインアップ",
                "email_input": "メールアドレス",
                "signup_button": "サインアップ",
                "signup_error_empty": "すべてのフィールドに入力してください。",
                "invalid_email_error": "有効なメールアドレスを入力してください。",
                "profile_button": "私のプロフィール",
                "view_post_button": "投稿を見る",
                "group_management": "グループ管理",
                "group_management_button": "グループ管理",
                "friend_management": "友達管理",
                "my_friend_list_button": "マイフレンドリスト",
                "my_friend_list_title": "マイフレンドリスト",
                "back_button": "戻る ↩️",
                "enter_id_prompt": "IDを入力してください:",
                "send_friend_request_button": "友達リクエストを送る",
                "friend_requests_button": "友達リクエスト",
                "block_button": "ブロック",
                "unblock_button": "ブロック解除",
                "delete_button": "削除",
                "upload_post_header": "投稿の登録",
                "post_title_input": "投稿タイトル",
                "post_content_input": "投稿内容",
                "image_file_upload": "画像ファイル",
                "general_file_upload": "一般ファイル",
                "category_select": "カテゴリー",
                "post_register_button": "投稿登録",
                "post_register_success": "投稿が登録されました。",
                "post_register_error": "タイトルと内容を入力してください。",
                "my_page_header": "マイページ",
                "edit_post_header": "投稿編集",
                "edit_post_id_input": "編集する投稿ID",
                "location_id_input": "位置ID",
                "category_id_input": "カテゴリーID",
                "edit_post_button": "投稿更新",
                "edit_post_success": "投稿が更新されました。",
                "edit_post_not_found_error": "投稿が見つかりません。",
                "delete_post_header": "投稿削除",
                "delete_post_id_input": "削除する投稿ID",
                "delete_post_button": "投稿削除",
                "delete_post_success": "投稿が削除されました。",
                "delete_post_not_found_error": "投稿が見つかりません。",
                "view_post_header": "投稿一覧",
                "upload_post_button": "投稿",
                "user_manager_page_title": "ユーザー管理ページ",
                "email_input_prompt": "メールアドレスを入力してください:",
                "confirm_button": "確認",
                "password_recovery_email_sent": "パスワード復旧メールが送信されました。",
                "email_not_registered_warning": "登録されていないメールアドレスです。",
                "Recommended Restaurant Posts": "おすすめレストランの投稿",
                "group_button": "グループ",
                "login_title1": "ログイン",
                "group_page_title": "グループページ",
                "create_group_button": "グループ作成 🧑‍🤝‍🧑",
                "search_group_button": "グループ検索 🔍",
                "login_required_error": "ログインが必要です。",
                "no_joined_groups": "参加中のグループがありません。"
        
            }
                
            
        }
    def get_text(self, key):

        try:
            return self.translations[self.lang][key]
        except KeyError:
            st.warning(f"'{key}' not found in language '{self.lang}'.")
            return key

    def switch_language(self, new_lang):

        if new_lang in self.translations:
            self.lang = new_lang
        else:
            st.error(f"Language '{new_lang}' is not supported.")

    def show_translations(self):
        """
        현재 선택된 언어의 번역 데이터를 Streamlit에서 시각화합니다.
        """
        st.json(self.translations.get(self.lang, {}))
session = SessionLocal()

# Streamlit 상태 초기화
if 'localization' not in st.session_state:
    st.session_state.localization = Localization(lang='ko')  # 기본값으로 한국어 설정
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'ko'  # 현재 언어 상태 관리

# Localization 객체 가져오기
localization = st.session_state.localization
if st.button("Switch to English"):
    localization.switch_language('en')
    st.session_state.current_language = 'en'

if st.button("한국어로 변경"):
    localization.switch_language('ko')
    st.session_state.current_language = 'ko'

if st.button("일본어로 변경"):
    localization.switch_language('jp')
    st.session_state.current_language = 'jp'

# 현재 언어 표시
st.write(f"Current Language: {st.session_state.current_language}")

class Page:

    def __init__(self):
        # 세션 상태 초기화
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'Home'  # Default to Home if not set
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        # TurnPages 클래스 인스턴스 생성
        self.turn_pages = TurnPages(self)
        self.group_page=GroupPage(self)
        self.friend_page=FriendPage(self)


    def render_page(self):
        # 페이지 렌더링
        page_functions = {
            'Home': self.home_page,
            'Login': self.turn_pages.login_page,
            'Signup': self.turn_pages.signup_page,
            'after_login': self.turn_pages.after_login,
            'View Post': self.turn_pages.view_post,
            'Setting': self.turn_pages.setting_page,
            'User manager': self.turn_pages.usermanager_page,
            'ID PW 변경': self.turn_pages.id_pw_change_page,
            'Upload Post': self.turn_pages.upload_post,
            'Group page': self.group_page.my_groups_page,
            'Detail group': self.group_page.detail_group,
            'GroupBlockList': self.group_page.group_block_list_page,
            'Group Update Page': self.group_page.group_update_page,  # 그룹 수정 페이지 등록
            'Group Request Page': self.group_page.group_request_page,  # Group Request Page 매핑 추가
            'Friend List Page': self.friend_page.FriendList_page,


        }


        # 현재 페이지 렌더링
        if st.session_state.current_page in page_functions:
            page_functions[st.session_state.current_page]()  # 매핑된 함수 호출
        else:
            st.warning(f"페이지 '{st.session_state.current_page}'을 찾을 수 없습니다.")  # 잘못된 페이지 처리

    # 페이지 전환 함수
    def change_page(self, page_name: str):
        # 방문 기록을 세션에 저장
        if st.session_state["current_page"] != page_name:
            st.session_state["history"].append(st.session_state["current_page"])
            st.session_state["current_page"] = page_name
            st.rerun()

    # 뒤로가기 함수
    def go_back(self):
        # 세션에 기록된 이전 페이지로 돌아가기
        if 'history' in st.session_state and st.session_state.history:
            st.session_state.current_page = st.session_state.history.pop()  # 이전 페이지로 이동
            st.rerun()  # 재귀 문제를 피할 수 있는 안정적인 rerun 방식
        else:
            st.warning("이전 페이지가 없습니다.")  # 방문 기록이 없을 경우 처리
            st.rerun()  # 재귀 문제를 피할 수 있는 안정적인 rerun 방식

    # 홈 페이지 함수 (로그인 전)
    def home_page(self):
        col1, col2 = st.columns(2)  # 동일한 너비의 세 개 열 생성
        with col1:
            st.title("맛ZIP")

        with col2:
            col3, col4, col5 = st.columns(3)
            with col3:
                if st.button("로그인", key="home_login_button",use_container_width=True):
                    self.change_page('Login')  # 로그인 페이지로 이동
            with col4:
                if st.button("회원가입", key="home_signup_button",use_container_width=True):
                    self.change_page('Signup')  # 회원가입 페이지로 이동
            with col5:
                if st.button("ID/PW 찾기", key="home_forgot_button",use_container_width=True):
                    self.change_page('User manager')  # ID/PW 찾기 페이지로 이동
        post_manager = PostManager()  # 인스턴스 생성
        post_manager.display_posts_on_home(None)  # display_posts_on_home 메서드 호출

class TurnPages:
    def __init__(self, page: Page):

        self.page = page
        self.friend_page=FriendPage


    def id_pw_change_page(self):
        st.title("<ID/PW 변경>")

        # 현재 로그인된 사용자 ID 가져오기
        user_id = st.session_state.get('logged_in_user')
        if not user_id:
            st.error("사용자 정보가 없습니다. 다시 로그인해주세요.")
            self.page.change_page('Login')  # 로그인 페이지로 이동
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
                change = ChangeIDPW(
                    user_id=st.session_state['current_user_id'],
                    new_value=new_value
                )
                if st.session_state['action'] == "ID 변경" and change.update_id():
                    st.success("ID가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                    st.session_state.user.clear()  # 세션 초기화로 로그아웃 처리
                    self.page.change_page("Home")  # 첫 페이지로 이동
                elif st.session_state['action'] == "비밀번호 변경" and change.update_password():
                    st.success("비밀번호가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                    st.session_state.user.clear()  # 세션 초기화로 로그아웃 처리
                    self.page.change_page("Home")  # 첫 페이지로 이동

    @st.dialog('로그인 페이지')
    def login_page(self):
        user_id = st.text_input("아이디", key="login_user_id_input")
        user_password = st.text_input("비밀번호", type='password', key="login_password_input")

        if st.button("로그인", key="login_submit_button"):
            if not user_id or not user_password:
                st.error("아이디와 비밀번호를 입력해 주세요.")
            else:
                # UserVO 객체 생성 (일단 최소 정보로 생성)
                user_vo = UserVO(user_id=user_id, user_password=user_password, user_email="")

                # SignIn 객체 생성
                sign_in = SignIn(user_vo)

                if sign_in.sign_in_event():  # 로그인 성공 시
                    dao = UserDAO()
                    user_vo = dao.get_user_vo(user_id)  # UserVO 객체를 반환

                    if user_vo:
                        # user_vo가 정상적으로 반환되면 처리
                        st.session_state['user_data'] = {
                            "user_id": user_vo.user_id,
                            "user_name": user_vo.user_id,  # 여기서는 user_id로 대체 (이름 컬럼 추가 시 수정 필요)
                            "profile_picture": user_vo.user_profile_picture if user_vo.user_profile_picture else "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
                            "user_email": user_vo.user_email,  # 추가 정보 포함
                        }
                    else:
                        st.error("사용자 정보를 불러오는데 실패했습니다.")
                        self.page.change_page('Login')

                    # 이후 user_data 사용하여 UI 처리
                    user_data = st.session_state.get('user_data')
                    # 이메일을 포함한 추가 정보를 UserVO에 업데이트
                    user_vo.user_email = user_data['user_email']
                    user_vo.profile_picture_path = user_data['profile_picture']

                    # 로그인 후 홈화면으로 이동
                    self.page.change_page('after_login')
                else:
                    st.error("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.")
        if st.button("뒤로가기↩️", use_container_width=True):
            self.page.go_back()

    @st.dialog('회원가입 페이지')
    def signup_page(self):
        # 사용자 입력 받기
        user_id = st.text_input("아이디")
        user_password = st.text_input("비밀번호", type='password')
        email = st.text_input("이메일")

        if st.button("회원가입", key="signup_submit_button"):
            if not user_id or not user_password or not email:
                st.error("모든 필드를 입력해 주세요.")
            else:
                # UserVO 객체 생성
                user_vo = UserVO(user_id=user_id, user_password=user_password, user_email=email)

                # SignUp 객체 생성
                signup = SignUp(user_vo)

                # 회원가입 이벤트 처리
                if signup.sign_up_event():
                    st.success("회원가입이 완료되었습니다!")
                    self.page.change_page('Home')
                else:
                    st.error("회원가입에 실패하였습니다.")
        if st.button("뒤로가기↩️", use_container_width=True):
            self.page.go_back()

    def after_login(self):
        # 타이틀을 중앙에 크게 배치
        st.markdown("<h1 style='text-align: center;'>맛ZIP</h1>", unsafe_allow_html=True)
        # 사용자 정보
        user_id = st.session_state.get("user_id")
        # 로그인 정보 없을 시 처리
        if not user_id:
            st.error("로그인 정보가 없습니다. 다시 로그인해주세요.")
            self.page.change_page('Login')

        dao = UserDAO()
        user_vo = dao.get_user_vo(user_id)  # UserVO 객체를 반환

        if user_vo:
            # user_vo가 정상적으로 반환되면 처리
            st.session_state['user_data'] = {
                "user_id": user_vo.user_id,
                "user_name": user_vo.user_id,  # 여기서는 user_id로 대체 (이름 컬럼 추가 시 수정 필요)
                "profile_picture": user_vo.user_profile_picture if user_vo.user_profile_picture else "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
                "user_email": user_vo.user_email,  # 추가 정보 포함
            }
        else:
            st.error("사용자 정보를 불러오는데 실패했습니다.")
            self.page.change_page('Login')

        # 이후 user_data 사용하여 UI 처리
        user_data = st.session_state.get('user_data')

        # 사용자 ID 표시 및 로그아웃 버튼
        col1, col2, col3, col4 = st.columns([1, 4, 2, 1])
        if user_data:
            user_name = user_data['user_name']
            with col1:
                profile_picture = user_data['profile_picture']
                st.image(profile_picture, use_container_width=True)
            with col2:
                st.write(f"**{user_name}**")
            with col3:
                if st.button("로그아웃", key="logout_button",use_container_width=True):
                    st.session_state.clear()
                    st.warning("로그아웃 성공")
            with col4:
                if st.button("프로필", key="profile_button",use_container_width=True):
                    self.page.change_page("Setting")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("게시물 보기", key='view_post_button',use_container_width=True):
                    self.page.change_page('View Post')
            with col2:
                if st.button("그룹 페이지", key='group_button',use_container_width=True):
                    self.page.change_page("Group page")
        else:
            st.error("사용자 정보가 없습니다.")

        # 중앙 포스팅 리스트
        st.title("추천 맛집 게시물")
        # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
        post_manager = PostManager()  # 인스턴스 생성
        post_manager.display_posts_on_home(user_id)  # display_posts_on_home 메서드 호출
        self.sidebar()

    # 친구 표시 함수
    def display_friend(self, name, online):
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


    def upload_post(self):
            user_id = st.session_state.get("user_id")
            st.header("게시물 등록")
            title = st.text_input("게시물 제목")
            content = st.text_area("게시물 내용")
            image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'])
            file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'])

            # 카테고리 선택을 위한 Selectbox
            post_manager = PostManager('uploads')  # DB 경로 설정
            category_manager = CategoryManager()
            category_names = category_manager.get_category_names()  # 카테고리 이름만 가져옴

            # Selectbox에서 카테고리 선택
            selected_category_name = st.selectbox("카테고리", category_names)

            # 선택한 카테고리 이름에 해당하는 category_id 구하기
            categories = category_manager.get_category_options()
            category_dict = {category.category: category.category_id for category in categories}
            selected_category_id = category_dict[selected_category_name]

            location_search = LocationSearch()
            location_search.display_location_on_map()
            col1, col2 = st.columns([6, 2])
            with col1:
                if st.button("게시물 등록"):
                    location_search.add_post(user_id, title, content, image_file, file_file, selected_category_id)
                    st.success("게시물이 등록되었습니다.")
            with col2:
                if st.button("뒤로가기↩️", use_container_width=True):
                    self.page.go_back()  # 뒤로가기 로직 호출

    def setting_page(self):
        # 로그인 정보 가져오기
        user_id = st.session_state.get("user_id")

        if not user_id:
            st.error("로그인 정보가 없습니다. 다시 로그인해주세요.")
            self.page.change_page('Login')
            return

        # 세션 상태에서 캐시된 사용자 정보 확인
        user_vo = st.session_state.get("user_vo")

        if not user_vo or user_vo.user_id != user_id:
            # 캐시된 사용자 정보가 없거나 로그인한 사용자와 일치하지 않으면
            # DB에서 새로 가져오기
            dao = UserDAO()
            user_vo = dao.get_user_vo(user_id)

            if not user_vo:
                st.error("사용자 정보를 찾을 수 없습니다.")
                return

            # 세션에 사용자 정보를 캐시
            st.session_state["user_vo"] = user_vo

        # 페이지 UI 구성
        col1, col2 = st.columns([8, 2])
        with col1:
            st.title("내 페이지")
        with col2:
            if st.button("뒤로가기↩️", use_container_width=True):
                self.page.go_back()

                # 사용자 프로필, 알림 설정 및 테마 버튼을 렌더링하는 뷰 클래스
        view = SetView(user_vo)  # UserVO 객체 전달
        view.render_user_profile()
        view.render_alarm_settings()

        # 테마 관리 버튼
        theme_manager = ThemeManager(user_id)
        theme_manager.render_button(user_id)

        # 사용자의 게시물 렌더링
        view.render_posts()
        self.view_my_group()
        # 친구 및 그룹 관리 사이드바

    def sidebar(self):

        # 사이드바에는 친구만 존재
        st.sidebar.title("친구 관리")

        # 친구 리스트
        if st.sidebar.button("내 친구 리스트"):
            self.page.change_page("Friend List Page")

        # 친구 대기 버튼
        if st.sidebar.button("친구 대기"):
            st.session_state["current_page"] = "FriendRequests"
            st.rerun()
        # 친구 대기 페이지
        if st.session_state.get("current_page") == "FriendRequests":
            st.title("친구 대기")
            self.show_friend_requests_page()
            # 작업 결과 또는 상태 표시
        if "action" in st.session_state:
            st.write(st.session_state["action"])
            del st.session_state["action"]


    def usermanager_page(self):

        st.title("사용자 관리 페이지")
        email = st.text_input('이메일을 입력하세요: ')

        if st.button("확인", key="forgot_confirm_button"):
            smtp_email = "kgus0203001@gmail.com"  # 발신 이메일 주소
            smtp_password = "pwhj fwkw yqzg ujha"  # 발신 이메일 비밀번호
            user_manager = UserManager(smtp_email, smtp_password)

            # 이메일 등록 여부 확인
            user_info = user_manager.is_email_registered(email)
            if user_info:
                st.success(f"비밀번호 복구 메일을 전송했습니다")
                # 복구 이메일 전송
                user_manager.send_recovery_email(email)
            else:
                st.warning("등록되지 않은 이메일입니다.")

        if st.button("뒤로가기↩️", use_container_width=True):
            self.page.go_back()

            # 게시글 목록
    def view_post(self):
        user_id = st.session_state.get("user_id")
        col1, col2, col3 = st.columns([6, 2, 2])  # 비율 6 : 2 : 2
        with col1:
            st.title("게시물 목록")  # 제목을 왼쪽에 배치
        with col2:
            if st.button("뒤로가기↩️",use_container_width=True):
                self.page.go_back()  # 뒤로가기 로직 호출
        with col3:
            if st.button("글 작성",use_container_width=True):
                self.page.change_page('Upload Post')
        # PostManager 인스턴스를 생성
        post_manager = PostManager()
        # display_posts 메서드를 호출
        post_manager.display_posts(user_id)

        # 내그룹 보기
    def view_my_group(self):
        user_id = st.session_state.get("user_id")
        with st.expander('내가 만든 그룹 목록', icon='🍙'):
            group_manager=GroupManager(user_id)
            groups =group_manager.get_my_groups(user_id)
            if not groups:
                st.info("생성한 그룹이 없습니다.")
                return

            for group in groups:
                st.markdown(f"**그룹 이름:** {group['group_name']}")
                st.markdown(f"**카테고리:** {group['category']}")
                st.markdown(f"**상태:** {group['status']}")
                st.markdown(f"**약속 날짜:** {group['meeting_date']}")
                st.markdown(f"**약속 시간:** {group['meeting_time']}")

                # 수정 버튼
                if st.button(f"수정", key=f"edit_{group['group_id']}"):
                    st.session_state["group_id"] = group['group_id']
                    self.page.change_page('Group Update Page')

                # 삭제 버튼
                if st.button(f"삭제", key=f"delete_{group['group_id']}"):
                    if group_manager.is_group_creator(group['group_id']):
                        group_manager.delete_group(group['group_id'])
                        st.success(f"'{group['group_name']}' 그룹이 삭제되었습니다.")
                        st.rerun()


    # 대기 중인 친구 요청을 표시하는 함수
    def show_friend_requests_page(self):
        user_id = st.session_state.get("user_id")
        friend_request = FriendRequest(user_id)
        received_requests = friend_request.get_received_requests()
        st.title("친구 요청 관리")

        # 내가 보낸 요청 목록
        st.subheader("내가 보낸 친구 요청")
        sent_requests = friend_request.get_my_sent_requests()
        if sent_requests:
            for req in sent_requests:
                st.write(f"- {req['requested_user_id']}")
        else:
            st.write("보낸 친구 요청이 없습니다.")

        # 내가 받은 요청 목록
        st.subheader("다른 사람이 보낸 친구 요청")
    
        if received_requests:
            for req in received_requests:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"- {req['requester_user_id']}")
                with col2:
                    if st.button(f"수락 ({req['requester_user_id']})", key=f"accept_{req['requester_user_id']}"):
                        friend_request.accept_friend_request(req['requester_user_id'])
                    if st.button(f"거절 ({req['requester_user_id']})", key=f"reject_{req['requester_user_id']}"):
                        friend_request.reject_friend_request(req['requester_user_id'])
        else:
            st.write("받은 친구 요청이 없습니다.")

        # 뒤로 가기 버튼 추가
        if st.button("뒤로 가기"):
            st.session_state["current_page"] = "after_login"  # 이전 페이지로 설정
            st.session_state["refresh"] = True  # 새로고침 플래그 설정
            st.rerun()

#-----------------------------------------------------그룹 페이지--------------------------------------------

class GroupPage():
    def __init__(self,page: Page):
        self.user_id = st.session_state.get("user_id")
        self.page=page
        self.request_dao=GroupRequestDAO
        self.category_manager = CategoryManager()
        self.group_manager=GroupManager(self.user_id)
        self.location_manager=LocationSearch

    #내 그룹 페이지
    def my_groups_page(self):
        # 상단 제목 설정 (좌측 정렬)
        col1, col2 = st.columns([3, 5])  # 버튼을 위한 공간 추가
        with col1:
            st.markdown(
                f"<h1 class='centered-title'>{'그룹페이지'}</h1>",
                unsafe_allow_html=True,
            )
        with col2:
            button_col1, button_col2, button_col3, button_col4 = st.columns(4)
            #그룹생성 버튼
            with button_col1:
                if st.button("그룹생성", use_container_width=True):
                    self.group_creation_page()
            #그룹차단 버튼
            with button_col2:
                if st.button("차단 목록"):  # 여기에 추가
                    st.session_state["current_page"] = "GroupBlockList"
                    st.rerun()
            #뒤로가기 버튼
            with button_col3:
                if st.button("뒤로가기↩️"):
                    self.page.go_back()
            #그룹검색 버튼
            with button_col4:
                if st.button("그룹검색", use_container_width=True):
                    self.search_groups_page()

        #유저의 그룹을 가져온다
        group_manager = GroupManager(self.user_id)
        groups = group_manager.get_user_groups()

        #그룹이 없을때
        if not groups:
            st.error("그룹이 없습니다")

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

        for group in groups:
            members = group_manager.get_group_member_count(group.group_id)
            category_name=self.category_manager.category_id_to_name(group.category)
            st.markdown(
                f"""
                        <div class="group-box">
                            <h2>{group.group_name}</h2>
                            <p><strong>카테고리:</strong> {category_name if category_name else 'Not set'}</p>
                            <p><strong>상태:</strong> {group.status}</p>
                            <p><strong>약속 날짜:</strong> {group.meeting_date if group.meeting_date else 'Not set'}</p>
                            <p><strong>약속 시간:</strong> {group.meeting_time if group.meeting_time else 'Not set'}</p>
                            <p><strong>인원수:</strong> {members if members else 'No members'}</p>
                        </div>
                        """,
                unsafe_allow_html=True
            )

            st.markdown("---")
            #그룹을 클릭하면 그룹id를 세션에 저장한다
            if st.button(f"세부 정보", key=f"open_group_{group.group_id}"):
                st.session_state["group_id"] = group.group_id  # 그룹 ID를 세션에 저장
                self.page.change_page('Detail group')  # 세부 정보 페이지 호출

            # 그룹들 사이에 구분선
            st.markdown("---")

    def group_block_list_page(self):
        st.title("그룹 차단 목록")

        # 로그인 확인
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        block_dao = GroupBlockDAO()  # GroupBlockDAO 인스턴스 생성
        blocked_groups = block_dao.get_blocked_groups(user_id)  # 차단된 그룹 ID 목록 가져오기
        #차단된 그룹이 있으면 정보를 반환함
        if not blocked_groups:
            st.warning("차단된 그룹이 없습니다.")
        else:
            for group_id in blocked_groups:
                st.markdown(f"**차단된 그룹 ID:** {group_id}")
                if st.button(f"차단 해제 (그룹 ID: {group_id})", key=f"unblock_group_{group_id}"):
                    if block_dao.unblock_group(user_id, group_id):
                        st.success(f"그룹 {group_id} 차단을 해제했습니다.")
                    else:
                        st.error("차단 해제 중 오류가 발생했습니다.")
        if st.button("뒤로가기"):
            self.page.go_back()

    def group_request_page(self, group_id):
        st.title("그룹 대기 목록")

        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return


        requests = self.request_dao.get_requests(group_id)

        if not requests:
            st.warning("대기 중인 요청이 없습니다.")
        else:
            for requester_id in requests:
                st.markdown(f"**요청자 ID:** {requester_id}")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"승인 (ID: {requester_id})", key=f"approve_request_{requester_id}"):
                        if self.request_dao.approve_request(group_id, requester_id):  # 요청 승인
                            st.success(f"{requester_id}님을 그룹에 추가했습니다.")

                with col2:
                    if st.button(f"거절 (ID: {requester_id})", key=f"reject_request_{requester_id}"):
                        if self.request_dao.reject_request(group_id, requester_id):  # 요청 거절
                            st.success(f"{requester_id}님의 요청을 거절했습니다.")

        # Back to the previous page
        if st.button("뒤로 가기", key="back_to_groups_button"):
            self.page.go_back()

    # 멤버 박스 출력 함수 (그룹장은 왕관 아이콘만 표시하고, 다른 멤버는 번호만 표시)
    def display_member_box(self,member_name, is_admin, member_number):
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
    def detail_group(self):
        col1, col2 = st.columns([6, 2])  # 비율 6 : 2
        with col1:
            st.title("그룹 세부 정보")  # 제목을 왼쪽에 배치
        with col2:
            if st.button("뒤로가기 ↩️"):
                self.page.go_back()  # 뒤로가기 로직 호출

        # 그룹 ID 가져오기 (열기 버튼 클릭 시 해당 그룹 ID가 넘어옴)
        group_id = st.session_state.get("group_id")
        if not group_id:
            st.error("그룹 정보가 없습니다.")
            return


        group_info = self.group_manager.get_group_info(group_id)
        members = self.group_manager.get_group_member_count(group_id)

        if not group_info:
            st.error("그룹 정보를 찾을 수 없습니다.")
            return

        group_name, modify_date, meeting_date, meeting_time = group_info[1], group_info[3], group_info[4], group_info[5]

        # Display group information
        st.markdown(f"### {group_name}")
        st.markdown(f"**현재 인원수:** {members} / 10")
        st.markdown(f"**마지막 수정일:** {modify_date}")
        st.markdown(f"**약속 날짜:** {meeting_date if meeting_date else '설정되지 않음'}")
        st.markdown(f"**약속 시간:** {meeting_time if meeting_time else '설정되지 않음'}")

        members= self.group_manager.get_group_members(group_id)

        # 그룹원 표시
        if members:
            st.write("**그룹원:**")
            for idx, (member_name, role) in enumerate(members, start=1):
                is_admin = role == 'admin'  # 그룹장이면 True
                self.display_member_box(member_name, is_admin, idx)
        else:
            st.warning("이 그룹에 소속된 멤버가 없습니다.")

        # GroupBlockDAO 초기화
        if "block_dao" not in st.session_state:
            st.session_state["block_dao"] = GroupBlockDAO()  # zip.db를 기본값으로 사용
        block_dao = st.session_state["block_dao"]

        # 그룹 차단/해제 기능
        if st.button("그룹 차단", key=f"block_group_{group_id}"):
            success = block_dao.block_group(st.session_state.get("user_id"), group_id)
            if success:
                st.success("그룹이 차단되었습니다.")
            else:
                st.error("차단 중 오류가 발생했습니다.")

        if st.button("차단 해제", key=f"unblock_group_{group_id}"):
            success = block_dao.unblock_group(st.session_state.get("user_id"), group_id)
            if success:
                st.success("차단이 해제되었습니다.")
            else:
                st.error("해제 중 오류가 발생했습니다.")

        if st.button("뒤로가기"):
            self.page.go_back()

        if st.button("그룹 초대", key=f"invite_group_{group_id}"):
            # 입력 필드 상태를 세션 상태에 저장해서 유지
            if 'invitee_id' not in st.session_state:
                st.session_state['invitee_id'] = ''  # 초기 값 설정

            invitee_id = st.text_input("초대할 사용자 ID를 입력하세요", key=f"invite_input_{group_id}",
                                       value=st.session_state['invitee_id'])

            if st.button("초대 요청 보내기", key=f"send_invite_{group_id}"):
                if invitee_id:
                    request_dao = GroupRequestDAO()
                    success = self.request_dao.send_request(invitee_id, group_id)  # 초대 요청 저장
                    if success:
                        st.success(f"{invitee_id}님에게 초대 요청을 보냈습니다.")
                        st.info("그룹 초대가 되었습니다.")  # 그룹 초대 확인 메시지
                        st.session_state['invitee_id'] = ''  # 성공적으로 보냈으면 필드 초기화
                    else:
                        st.error("초대 요청을 보내는 데 실패했습니다.")
                else:
                    st.error("초대할 사용자 ID를 입력하세요.")  # ID 입력 안 했을 때 에러 메시지

    def group_block_list_page(self):

        st.title("그룹 차단 목록")

        # 로그인 확인
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        block_dao = GroupBlockDAO()  # GroupBlockDAO 인스턴스 생성
        blocked_groups = block_dao.get_blocked_groups(user_id)  # 차단된 그룹 ID 목록 가져오기

        if not blocked_groups:
            st.warning("차단된 그룹이 없습니다.")
        else:
            for group_id in blocked_groups:
                st.markdown(f"**차단된 그룹 ID:** {group_id}")
                if st.button(f"차단 해제 (그룹 ID: {group_id})", key=f"unblock_group_{group_id}"):
                    if block_dao.unblock_group(user_id, group_id):
                        st.success(f"그룹 {group_id} 차단을 해제했습니다.")
                    else:
                        st.error("차단 해제 중 오류가 발생했습니다.")
        if st.button("뒤로가기"):
            self.page.go_back()

    #그룹 생성 페이지
    @st.dialog("그룹 생성")
    def group_creation_page(self):

        # 이제 인스턴스를 통해 group_creation_page 메서드를 호출합니다.
        st.header("그룹 생성")

        # 그룹 이름 입력
        group_name = st.text_input("그룹 이름", placeholder="그룹 이름을 입력하세요", key="group_name_input")
        max_members = st.number_input("최대 인원 수", min_value=2, max_value=10, step=1, value=10, key="max_members_input")


        meeting_date = st.date_input("약속 날짜 선택", key="meeting_date_input")
        meeting_time = st.time_input("약속 시간 선택", key="meeting_time_input")

        # 카테고리 선택

        categories = self.category_manager.category_selector()


        # 장소 검색 필드와 지도
        location_search = LocationSearch()
        location_search.display_location_on_map()

        group_manager=GroupManager(self.user_id)
        # 그룹 생성 버튼
        if st.button("그룹 생성", key="create_group_button"):
            group_id = location_search.add_group(group_name, self.user_id, categories, meeting_date, meeting_time)
            group_manager.add_group_member(group_id)

    def join_group(self,group_name):
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        try:
            # 그룹 조회
            group = session.query(Group).filter(Group.group_name == group_name).first()
            if not group:
                st.error("그룹을 찾을 수 없습니다.")
                return

            # 이미 멤버인지 확인
            existing_member = session.query(GroupMember).filter(
                GroupMember.group_id == group.id, GroupMember.user_id == user_id).first()
            if existing_member:
                st.warning("이미 해당 그룹의 멤버입니다.")
                return

            # 그룹 멤버 추가
            new_member = GroupMember(
                group_id=group.id,
                user_id=user_id,
                role="member"
            )
            session.add(new_member)
            session.commit()

            st.success(f"'{group_name}' 그룹에 성공적으로 참여하였습니다.")
        finally:
            session.close()  # 세션 종료


    @st.dialog("그룹 수정")
    def group_update_page(self):
        # 그룹 ID 가져오기 (세션에 저장된 그룹 ID)
        group_id = st.session_state.get("group_id_to_edit")
        if not group_id:
            st.error("수정할 그룹 ID를 찾을 수 없습니다.")
            return

        group_info = self.group_manager.get_group_info(group_id)
        # 그룹 수정 폼 바로 표시
        st.markdown(f"**'{group_info[1]}' 그룹을 수정합니다.**")

        group_name = st.text_input("그룹 이름", value=group_info[1])
        # 카테고리 선택
        category_manager = CategoryManager()
        categories = category_manager.category_selector()


        # 약속 날짜와 시간 추가
        if group_info[4] is not None:
            meeting_date = st.date_input("약속 날짜", value=group_info[4])
        else:
            meeting_date = st.date_input("약속 날짜", value=datetime.today().date())  # 기본값: 오늘 날짜

        if group_info[5] is not None:
            meeting_time = st.time_input("약속 시간", value=group_info[5])
        else:
            meeting_time = st.time_input("약속 시간", value=datetime.now().time())  # 기본값: 현재 시간

        status_choices = ["진행 중", "완료", "취소"]
        group_status = group_info[2]

        # group_status 값이 유효하지 않을 경우 기본값 설정
        if group_status not in status_choices:
            group_status = "진행 중"  # 기본값

        # selectbox로 상태 선택
        selected_status = st.selectbox("그룹 상태", options=status_choices, index=status_choices.index(group_status))
        # 그룹 수정 버튼
        if st.button("그룹 수정"):
            self.group_manager.update_group(group_id,group_name, categories, selected_status, meeting_date, meeting_time)

        if st.button("뒤로가기"):
            self.page.go_back()

    @st.dialog('그룹 검색')
    def search_groups_page(self):
       st.header("그룹 검색 및 참여")
       search_group = GroupSearch()
       # 검색 기준 선택
       search_criteria = st.selectbox(
           "검색 기준을 선택하세요",
           ["이름", "날짜", "카테고리"],
           index=0
       )
       user_input = None
       groups = []


       # 그룹 검색 처리
       if search_criteria == "이름":
           user_input = st.text_input("그룹 이름을 입력하세요")
       elif search_criteria == "날짜":
           user_input = st.date_input("약속 날짜를 선택하세요")
       elif search_criteria == "카테고리":
           user_input=self.category_manager.category_selector()

       # 검색 버튼
       if st.button("검색"):
           # 검색 실행
           if user_input:
               groups = search_group.search_groups(user_input,search_criteria)

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

class FriendPage:
    def __init__(self,page:Page):
        self.user_id = st.session_state.get("user_id")
        self.page = page
        self.friend_manager=FriendManager(self.user_id )
        self.friend_request=FriendRequest

    @st.dialog("친구 추가 창")
    def add_friend_page(self):

        # 상호작용할 ID 입력창
        target_id = st.text_input("친구 요청을 보낼 ID를 입력하세요:", key="friend_action_input")

        if st.button("친구 요청"):
            if target_id:
                # 친구 추가 함수 호출 (user_id와 target_id)
                self.friend_request.add_friend(self.user_id, target_id)
            else:
                st.warning("친구 요청할 ID를 입력해주세요.")

    @st.dialog("친구 차단 해제 창")
    def unblock_friend_page(self):

        # 상호작용할 ID 입력창
        target_id = st.text_input("차단 해제할 친구의 ID를 입력하세요:", key="friend_action_input")

        if st.button("친구 차단 해제"):
            if target_id:
                # 친구 차단 해제 함수 호출 (user_id와 target_id)
                self.friend_manager.unblock_friend( target_id)
            else:
                st.warning("친구 차단 해제할 ID를 입력해주세요.")

        st.title("차단 목록")
        self.show_blocked_list_page()

    def show_blocked_list_page(self):

        blocked_users = self.friend_manager.show_blocked_list()  # 차단된 유저 목록 가져오기
        if blocked_users:
            st.subheader("현재 차단된 사용자:")
            for user in blocked_users:
                st.write(f"- {user['blocked_user_id']}")
        else:
            st.write("차단된 사용자가 없습니다.")

    def friend_posts_page(self):
        # 현재 선택된 친구 ID
        friend_id = st.session_state.get('current_friend_id')
        if not friend_id:
            st.error("친구 ID가 없습니다.")
            return

        # 세션 시작
        session = SessionLocal()
        try:
            # 친구의 포스팅 가져오기
            posts = session.query(Posting).filter(Posting.p_user == friend_id).all()

            if posts:
                st.title(f"{friend_id}님의 작성한 포스팅")
                for post in posts:
                    st.subheader(post.p_title)
                    st.write(post.p_content)

                    # 이미지 경로가 존재하고 실제로 파일이 있으면 이미지를 표시
                    if post.p_image_path and os.path.exists(post.p_image_path):
                        st.image(post.p_image_path, width=200)
                    else:
                        st.write("이미지가 없습니다.")
            else:
                st.warning("작성한 포스팅이 없습니다.")
        except Exception as e:
            st.error(f"DB 오류: {e}")
        finally:
            session.close()  # 세션 종료

    @st.dialog("친구 삭제 창")
    def delete_friend(self):
        # 상호작용할 ID 입력창
        target_id = st.text_input("삭제할 친구의 ID를 입력하세요:", key="friend_action_input")

        if st.button("친구 삭제"):
            if target_id:
                # 친구 차단 해제 함수 호출 (user_id와 target_id)
                self.friend_manager.delete_friend(target_id)
            else:
                st.warning("삭제할 친구의 ID를 입력해주세요.")

    # 친구 상태 표시 함수
    def display_friend(self,name, online):
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



    @st.dialog("친구 차단 창")
    def block_friend_page(self):
        # 상호작용할 ID 입력창
        target_id = st.text_input("차단할 친구의 ID를 입력하세요:", key="friend_action_input")

        if st.button("친구 차단"):
            if target_id:
                # 친구 차단 함수 호출 (user_id와 target_id)
                self.friend_manager.block_friend(target_id)
            else:
                st.warning("친구 차단할 ID를 입력해주세요.")

    @st.dialog("친구 대기 창")
    def Request_friend_page(self):
        turn_pages=TurnPages
        turn_pages.show_friend_requests_page()

    def FriendList_page(self):
        st.title("내 친구 리스트")  # 제목을 왼쪽에 배치
        col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 3, 2])  # 비율 4 : 2 : 2
        with col1:
            if st.button("뒤로가기↩️", use_container_width=True,key='friendlist key'):
                self.page.go_back()
        with col2:
            if st.button("친구 요청 보내기", key="add_friend_button"):
                self.add_friend_page()
        with col3:
            if st.button("친구 차단", key="block_friend_button"):
                self.block_friend_page()
        with col4:
            if st.button("친구 차단 해제", key="unblock_friend_button"):
                self.unblock_friend_page()
        with col5:
            if st.button("친구 삭제", key="delete_friend_button"):
                self.delete_friend()



# -------------------------------------디비-----------------------------------------------------------------------------

class User(Base):
    __tablename__ = 'user'
    user_seq = Column(Integer, primary_key=True, autoincrement=True)  # 고유 시퀀스
    user_id = Column(String, unique=True, nullable=False)  # 사용자 ID
    user_password = Column(String, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_is_online = Column(Boolean, default=False)
    user_mannerscore = Column(Integer, default=0)
    profile_picture_path = Column(String, nullable=True)

    def to_dict(self):
        """
        User 객체를 딕셔너리 형태로 변환하는 메서드.
        :return: 딕셔너리 형태의 데이터
        """
        return {
            'user_id': self.user_id,
            'user_password': self.user_password,
            'user_email': self.user_email,
            'user_seq': self.user_seq,
            'user_is_online': self.user_is_online,
            'profile_picture_path': self.profile_picture_path
        }


class Friend(Base):
    __tablename__ = 'friend'
    friend_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    friend_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)

class Group(Base):
    __tablename__ = 'group'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, unique=True, nullable=False)
    group_creator = Column(String, ForeignKey('user.user_id'), nullable=False)
    category = Column(Integer, nullable=True)
    date = Column(DateTime, default=func.now())
    location = Column(Integer, nullable=True)
    meeting_date = Column(Date, server_default=func.current_date())  # Default: CURRENT_DATE
    meeting_time = Column(Time, server_default=func.current_time())  # Default: CURRENT_TIME
    status = Column(String, default='진행 중')
    update_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modify_date = Column(DateTime, default=func.now(), onupdate=func.now())

class Block(Base):
    __tablename__ = 'block'
    block_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    blocked_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)

# myFriendrequest 테이블 (내가 보낸 친구 신청 목록)
class MyFriendRequest(Base):
    __tablename__ = 'myFriendrequest'
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    requested_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)

# otherRequest 테이블 (다른 사람이 보낸 친구 신청 목록)
class OtherRequest(Base):
    __tablename__ = 'otherRequest'
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    requester_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)

class GroupBlock(Base):
    __tablename__ = 'group_block'

    block_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    blocked_group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)

    # Optional: Define relationships if you want to access related data easily
    user = relationship("User", backref="blocked_groups")
    blocked_group = relationship("Group", backref="blocked_by")

# MyGroupRequest Table (Requests Sent by User to Join a Group)
class MyGroupRequest(Base):
    __tablename__ = 'myGroupRequest'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    requested_group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)

    # Optional: Define relationships if you want to access related data easily
    user = relationship("User", backref="sent_group_requests")
    requested_group = relationship("Group", backref="group_requests")

# OtherGroupRequest Table (Requests Sent by Other Users to Join a Group)
class OtherGroupRequest(Base):
    __tablename__ = 'otherGroupRequest'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)
    requester_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)

    # Optional: Define relationships if you want to access related data easily
    group = relationship("Group", backref="received_group_requests")
    requester_user = relationship("User", backref="received_requests_from_others")

class GroupMember(Base):
    __tablename__ = 'group_member'
    group_member_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    role = Column(
        String,
        CheckConstraint("role IN ('admin', 'member')"),  # 위치 인수 대신 키워드로 전달
        default='member'
    )
    joined_at = Column(DateTime, default=func.now())


class FoodCategory(Base):
    __tablename__ = 'food_categories'
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, unique=True, nullable=False)


class Location(Base):
    __tablename__ = 'locations'
    location_id = Column(Integer, primary_key=True, autoincrement=True)
    location_name = Column(String, nullable=False)
    address_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)
    sender_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    message_text = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=func.now())


class Posting(Base):
    __tablename__ = 'posting'
    p_id = Column(Integer, primary_key=True, autoincrement=True)
    p_user = Column(String, ForeignKey('user.user_id'), nullable=False)
    p_title = Column(String, nullable=False)
    p_content = Column(Text, nullable=False)
    p_image_path = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    p_location = Column(Integer, ForeignKey('locations.location_id'), nullable=True)
    p_category = Column(Integer, ForeignKey('food_categories.category_id'), nullable=True)
    like_num = Column(Integer, default=0)
    total_like_num = Column(Integer, default=0)
    file = Column(Text, nullable=True)  # Adjust as needed
    upload_date = Column(DateTime, default=func.now())
    modify_date = Column(DateTime, default=func.now(), onupdate=func.now())


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    user = Column(String, ForeignKey('user.user_id'), nullable=False)
    current_theme = Column(String, nullable=True, default='dark')


class PasswordRecovery(Base):
    __tablename__ = 'password_recovery'
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



# 데이터베이스 초기화 및 기본 데이터 삽입
def initialize_database():
    try:
        # 테이블 생성 (앱 실행 시 한 번만)
        Base.metadata.create_all(engine, checkfirst=True)

        # 기본 데이터 삽입 (기본 데이터가 없다면 삽입)
        if not session.query(User).filter_by(user_id="default_user").first():
            default_user = User(
                user_id="default_user",
                user_password="default_password",  # 실제로는 비밀번호 해싱 필요
                user_email="default@example.com",
                profile_picture_path="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
            )
            session.add(default_user)

        # Food Categories 기본값 삽입
        default_categories = ["한식", "중식", "양식", "일식", "디저트", "패스트푸드"]
        for category in default_categories:
            if not session.query(FoodCategory).filter_by(category=category).first():
                session.add(FoodCategory(category=category))

        session.commit()

    except Exception as e:
        session.rollback()  # 예외 발생 시 롤백
        print(f"Error initializing database: {e}")

    finally:
        session.close()  # 세션 닫기


# ---------------------------------------------------------------로그인 ----------------------------
class UserVO:
    def __init__(self, user_id: str, user_password: str, user_email: str, user_seq: int = None,
                 user_is_online: bool = False, user_profile_picture: str = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email
        self.user_seq = user_seq
        self.user_is_online = user_is_online
        self.user_profile_picture = user_profile_picture

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get('user_id', ''),
            user_password=data.get('user_password', ''),
            user_email=data.get('user_email', ''),
            user_seq=data.get('user_seq', None),
            user_is_online=data.get('user_is_online', False),
            user_profile_picture=data.get('user_profile_picture', "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png")
        )

class UserManager:
    def __init__(self, smtp_email, smtp_password, db_url="sqlite:///zip.db"):
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.db_url = db_url
        Base.metadata.create_all(self.engine)

    def is_email_registered(self, email):
        session = self.create_session()
        user = session.query(User).filter_by(user_email=email).first()
        session.close()
        return user is not None

    def generate_token(self, length=16):
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def send_recovery_email(self, email, token):
        subject = "Password Recovery Token"
        body = (
            f"안녕하세요,\n\n"
            f"비밀번호 복구 요청이 접수되었습니다. 아래의 복구 토큰을 사용하세요:\n\n"
            f"{token}\n\n"
            f"이 요청을 본인이 하지 않은 경우, 이 이메일을 무시해 주세요."
        )

        # MIME 메시지 생성
        msg = MIMEMultipart()
        msg['From'] = Header(self.smtp_email, 'utf-8')
        msg['To'] = Header(email, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()  # 암호화 시작
                connection.login(user=self.smtp_email, password=self.smtp_password)  # 로그인
                connection.sendmail(from_addr=self.smtp_email, to_addrs=email, msg=msg.as_string())  # 이메일 전송
            print(f"Recovery email sent to {email}.")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def save_recovery_token(self, email, token):
        """토큰을 데이터베이스에 저장"""
        session = self.create_session()
        recovery = PasswordRecovery(user_email=email, token=token)
        session.add(recovery)
        session.commit()
        session.close()

    def verify_token(self, email, token):
        """사용자가 입력한 토큰 검증"""
        session = self.create_session()
        recovery = session.query(PasswordRecovery).filter_by(user_email=email, token=token).first()
        session.close()
        # 토큰이 1시간 이내에 생성된 경우에만 유효
        if recovery and (datetime.utcnow() - recovery.created_at).seconds < 3600:
            return True
        return False

    def reset_password(self, email, new_password):
        """비밀번호를 새로 설정"""
        session = self.create_session()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user = session.query(User).filter_by(user_email=email).first()
        if user:
            user.user_password = hashed_password
            session.commit()
        session.close()

    def recover_password(self, email, new_password, token):
        """토큰을 통해 비밀번호 복구"""
        if not self.verify_token(email, token):
            print("유효하지 않은 토큰입니다.")
            return
        self.reset_password(email, new_password)
        print("비밀번호가 성공적으로 복구되었습니다.")


# DAO 클래스
class UserDAO:

    def check_user_id_exists(self, user_id):
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return UserVO.from_dict(user.to_dict()) if user else None
        except Exception as e:
            st.error(f"DB 오류: {e}")
            return None

    def insert_user(self, user_vo: UserVO):

        #UserVO를 상속받아 정보를 저장함
        hashed_password = bcrypt.hashpw(user_vo.user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            user_id=user_vo.user_id,
            user_password=hashed_password,
            user_email=user_vo.user_email
        )
        try:
            session.add(new_user)
            session.commit()

        except Exception as e:
            session.rollback()
            st.error(f"DB 오류: {e}")

    def check_password(self, hashed_password, plain_password):
        # hashed_password가 문자열이라면 bytes로 변환
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def get_user_vo(self, user_id):
        user = session.query(User).filter(User.user_id == user_id).first()
        session.close()

        if user:
            return UserVO(
                user_id=user.user_id,
                user_password=user.user_password,
                user_email=user.user_email,
                user_seq=user.user_seq,
                user_is_online=user.user_is_online,
                user_profile_picture=user.profile_picture_path
            )
        return None

    def update_user_field(self, user_id, field_name, field_value):

        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            setattr(user, field_name, field_value)
            session.commit()
            return True

# 회원가입 클래스
class SignUp:
    def __init__(self, user_vo: UserVO):
        self.user_vo = user_vo

    def sign_up_event(self):
        dao = UserDAO()  # UserDAO 인스턴스 생성
        if not self.check_length():
            return False
        if not self.check_user():
            return False
        dao.insert_user(self.user_vo)  # UserVO를 DAO에 전달
        return True

    def check_length(self):
        if len(self.user_vo.user_password) < 8:
            st.error("비밀번호는 최소 8자 이상이어야 합니다.")
            return False
        return True

    def check_user(self):
        dao = UserDAO()
        if dao.check_user_id_exists(self.user_vo.user_id):
            st.error("이미 사용 중인 아이디입니다.")
            return False
        return True


# 로그인 처리 클래스
class SignIn:
    def __init__( self, user_vo: UserVO):
        self.user_vo = user_vo
        self.page = Page()

    def sign_in_event(self):
        dao = UserDAO()
        user = dao.check_user_id_exists(self.user_vo.user_id)  # UserVO 반환
        if user:
            if dao.check_password(user.user_password, self.user_vo.user_password):
                st.session_state["user_id"] = self.user_vo.user_id
                dao.update_user_field(self.user_vo.user_id, "user_is_online", True)

                st.success(f"{self.user_vo.user_id}님, 로그인 성공!")
                return True
            else:
                st.error("비밀번호가 틀렸습니다.")
        else:
            st.error("아이디가 존재하지 않습니다.")
        return False


# ------------------------------------------포스팅---------------------------------

class LocationGet:
    # locations 테이블에 저장
    def save_location(self, location_name, address_name, latitude, longitude):
        new_location = Location(
            location_name=location_name,
            address_name=address_name,
            latitude=latitude,
            longitude=longitude
        )
        session.add(new_location)
        session.commit()

    # 저장된 장소들 가져오기
    def get_all_locations(self):
        locations = session.query(Location).all()
        return locations

    def get_location_names(self):
        locations = session.query(Location).all()
        location_dict = {location.location_name: location.location_id for location in locations}
        return location_dict


class LocationSearch:
    def __init__(self):
        self.selected_location_id = None

    def search_location(self, query):
        url = f"https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {
            "Authorization": "KakaoAK 6c1cbbc51f7ba2ed462ab5b62d3a3746"  # API 키를 헤더에 포함
        }
        params = {
            "query": query,  # 검색할 장소 이름
            "category_group_code": "SW8,FD6,CE7"  # 카테고리 코드 (예: 음식점, 카페 등)
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            if documents:
                return documents
            else:
                st.error("검색 결과가 없습니다.")
                return None
        else:
            st.error(f"API 요청 오류: {response.status_code}")
            return None

    def save_or_get_location(self, name, address, latitude, longitude):
        location = session.query(Location).filter_by(location_name=name, address_name=address).first()

        if location:
            return location.location_id  # 이미 존재하면 location_id 반환

        # 새로운 위치 저장
        new_location = Location(
            location_name=name,
            address_name=address,
            latitude=latitude,
            longitude=longitude
        )
        session.add(new_location)
        session.commit()
        return new_location.location_id

    def display_location_on_map(self):
        col1, col2 = st.columns([8, 1])
        with col1:
            query = st.text_input("검색할 장소를 입력하세요:", "영남대역", key='place')  # 기본값: 영남대역
        with col2:
            st.button("검색")

        if query:
            # 카카오 API로 장소 검색
            results = self.search_location(query)

        if results:
            # 지역 정보 추출
            locations = [(place["place_name"], place["address_name"], float(place["y"]), float(place["x"]))
                         for place in results]

            # 지역 이름 선택
            selected_place = st.selectbox("검색 결과를 선택하세요:", [name for name, _, _, _ in locations])
            location_data = []
            # 선택된 장소의 정보 찾기
            for place in locations:
                if place[0] == selected_place:
                    name, address, latitude, longitude = place

                    # Append to location data
                    location_data.append({
                        'name': name,
                        'address': address,
                        'latitude': latitude,
                        'longitude': longitude
                    })

                    # Display place details
                    col3, col4 = st.columns([4, 1])
                    with col3:
                        st.write(f"장소 이름: {name}")
                        st.write(f"주소: {address}")
                        # 여기서 데이터베이스에 저장
                        self.selected_location_id = self.save_or_get_location(
                            name, address, latitude, longitude)
            if location_data:
                df = pd.DataFrame(location_data)
                st.map(df[['latitude', 'longitude']])

    def get_selected_location_id(self):
        return self.selected_location_id

    def add_post(self, user_id, title, content, image_file, file_file, category):
        location_id = self.get_selected_location_id()  # Get the selected location_id
        post_manager = PostManager()
        image_path = post_manager.save_file(image_file) if image_file else ''
        file_path = post_manager.save_file(file_file) if file_file else ''
        upload_date = modify_date = datetime.now()

        # Create a new post object
        new_post = Posting(
            p_user = user_id,
            p_title=title,
            p_content=content,
            p_image_path=image_path,
            file_path=file_path,
            p_location=location_id,  # Foreign key to the location_id
            p_category=category,
            upload_date=upload_date,
            modify_date=modify_date
        )

        # Add the new post to the session and commit the transaction
        session.add(new_post)
        session.commit()

    def add_group(self, group_name, user_id, category, meeting_date, meeting_time):
        location_id = self.get_selected_location_id()
        # 그룹 생성 버튼
        current_date = modify_date = datetime.now()
        if not group_name or not location_id or not meeting_date or not meeting_time:
            st.error("모든 필수 입력 항목을 입력해주세요.")
        else:

            # 그룹 모델 인스턴스 생성
            new_group = Group(
                group_name=group_name,
                group_creator=user_id,
                category=category,  # category[0]은 ID 값
                location=location_id,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                update_date=current_date,
                modify_date=current_date,
                status="진행 중"
            )
            # 세션에 그룹 추가
            session.add(new_group)
            session.commit()
            session.refresh(new_group)  # 새로운 그룹 객체에 자동 생성된 group_id가 반영됨

            # 성공 메시지
            st.success(f"'{group_name}' 그룹이 성공적으로 생성되었습니다!")

            # 생성된 그룹 ID 반환
            return new_group.group_id  # 생성된 그룹의 ID를 반환



class PostManager:
    def __init__(self, upload_folder='uploaded_files'):
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        self.locations_df = None
        if "posts" not in st.session_state:
            st.session_state.posts = []
        self.category_manager = CategoryManager()

    def save_file(self, file):
        if file:
            file_path = os.path.join(self.upload_folder, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            return file_path
        return ''

    def update_post(self, post_id, title, content, image_file, file_file, category):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            image_path = self.save_file(image_file) if image_file else post.p_image_path
            file_path = self.save_file(file_file) if file_file else post.file_path
            post.p_title = title
            post.p_content = content
            post.p_image_path = image_path
            post.file_path = file_path
            post.p_category = category
            post.modify_date = datetime.now()
            session.commit()

    def delete_post(self, p_id):
        post = session.query(Posting).filter_by(p_id=p_id).first()
        if post:
            session.delete(post)
            session.commit()

    def get_all_posts(self):
        return session.query(Posting).all()

    def get_my_posts(self,user_id):
        try:
            # 데이터베이스에서 user_id에 해당하는 사용자의 게시물 조회
            posts = session.query(Posting).filter(Posting.p_user == user_id).all()

            # 사용자가 작성한 게시물이 없을 경우 처리
            if not posts:
                st.warning(f"사용자 ID '{user_id}'로 작성된 게시물이 없습니다.")
                return []

            # 게시물 데이터를 리스트로 변환하여 반환
            post_list = []
            for post in posts:
                post_data = {
                    "post_id": post.post_id,
                    "title": post.p_title,
                    "content": post.p_content,
                    "image_path": post.p_image_path,
                    "file_path": post.file_path,
                    "category_id": post.p_category,
                    "location_id": post.p_location,
                    "upload_date": post.upload_date,
                    "modify_date": post.modify_date,
                }
                post_list.append(post_data)

            return post_list

        except Exception as e:
            st.error(f"게시물 조회 중 오류가 발생했습니다: {e}")
            return []
        finally:
            session.close()  # 세션 닫기

    def toggle_like(self, post_id,user_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post.like_num==1:
            # 이미 좋아요를 눌렀다면 취소
            post.like_num = 0
            post.total_like_num -= 1  # 총 좋아요 수 감소
            st.warning("좋아요를 취소했습니다.")
        elif post.like_num ==0:
            post.like_num = 1
            post.total_like_num += 1  # 총 좋아요 수 증가
            st.success("좋아요를 추가했습니다!")

        session.commit()  # 세션 커밋


    def display_like_button(self, post_id,user_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            total_likes = post.total_like_num
            st.write(f"총 좋아요 수: {total_likes}")

            btn_label = "좋아요 취소" if post.like_num == 1 else "좋아요"
            if st.button(btn_label, key=post_id, use_container_width=True):
                self.toggle_like(post_id,user_id)

    def create_location_name(self):
        # Check if the DataFrame is empty
        if self.locations_df is None or self.locations_df.empty:
            st.error("위치가 존재하지 않습니다")
            return

        # Display place details
        for index, row in self.locations_df.iterrows():
            name = row['location_name']
            address = row['address_name']
            st.write(f"장소 이름: {name}")
            st.write(f"주소: {address}")

    def display_map(self):

        if self.locations_df is None or self.locations_df.empty:
            st.error("위치 데이터가 없습니다.")
            return

        # Use the latitude and longitude columns to display the map
        st.map(self.locations_df[['latitude', 'longitude']], use_container_width=True)

    def edit_post(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            title = st.text_input("게시물 제목", value=post.p_title, key=f"post_title_{post.p_id}")
            content = st.text_area("게시물 내용", value=post.p_content, key=f"post_content_{post.p_id}")
            image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'], key=f"image_upload_{post.p_id}")
            file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'],
                                         key=f"file_upload_{post.p_id}")

            selected_category_name = st.selectbox(
                "카테고리", [category.category for category in self.category_manager.get_category_options()],
                key=f"category_selectbox_{post.p_id}"
            )
            categories = self.category_manager.get_category_options()
            category_dict = {category.category: category.category_id for category in categories}
            selected_category_id = category_dict[selected_category_name]

            if st.button("게시물 수정", key=f"button_{post.p_id}", use_container_width=True):
                self.update_post(post_id, title, content, image_file, file_file, selected_category_id)
                st.success("게시물이 수정되었습니다.")

        else:
            st.error("해당 게시물이 존재하지 않습니다.")

    def fetch_location_data(self, post_id):
        # Query the database using SQLAlchemy
        location_data = session.query(
            Location.location_name,
            Location.address_name,
            Location.latitude,
            Location.longitude
        ).join(Posting, Posting.p_location == Location.location_id).filter(Posting.p_id == post_id).all()

        # Convert the result to a Pandas DataFrame
        if location_data:
            self.locations_df = pd.DataFrame(location_data,
                                             columns=['location_name', 'address_name', 'latitude', 'longitude'])
        else:
            self.locations_df = pd.DataFrame(columns=['location_name', 'address_name', 'latitude', 'longitude'])

        return self.locations_df

    #user_id를 검사하고 가져옴
    def display_posts(self,user_id):
        posts = session.query(Posting).filter_by(p_user=user_id).all()

        for post in posts:
            st.write(f"Post ID: {post.p_id}, Title: {post.p_title}")
            st.write(f"Content: {post.p_content}")
            if post.p_image_path and os.path.exists(post.p_image_path):
                st.image(post.p_image_path, width=200)


            # 게시물 삭제 버튼
            if st.button(f"삭제", key=f"delete_{post.p_id}", use_container_width=True):
                self.delete_post(post.p_id)
                st.success(f"게시물 '{post.p_title}'가 삭제되었습니다.")
                return self.display_posts(user_id)

            # 게시물 수정 버튼
            with st.expander("수정"):
                self.edit_post(post.p_id)

            self.fetch_location_data(post.p_id)

            # 위치 데이터가 존재할 때만 지도 생성
            if self.locations_df is not None and not self.locations_df.empty:
                self.create_location_name()
                st.title("Location Map")
                self.display_map()

            st.write(f"**등록 날짜**: {post.upload_date}, **수정 날짜**: {post.modify_date}")
            st.write("---")

    def display_post(self, post_id):
        # 특정 게시물 가져오기
        post = self.get_post_by_id(post_id)

        if post:
            # 게시물 정보 출력
            st.write(f"**creator ID**: {post['p_user']}")
            st.write(f"**Title**: {post['p_title']}")
            st.write(f"**Content**: {post['p_content']}")

            # 이미지 출력
            if post.get('p_image_path') and os.path.exists(post['p_image_path']):
                st.image(post['p_image_path'], width=200)

            # 파일 출력
            if post.get('file_path') and os.path.exists(post['file_path']):
                st.write("**Filename**:", os.path.basename(post['file_path']))
                st.write(f"**File size**: {os.path.getsize(post['file_path'])} bytes")
                st.markdown(
                    f"[Download File]({post['file_path']})",
                    unsafe_allow_html=True
                )

        else:
            st.error("해당 게시물을 찾을 수 없습니다.")

    def get_post_by_id(self, post_id):
        # Query the Posting table using SQLAlchemy's ORM query
        post = session.query(Posting).filter_by(p_id=post_id).first()

        # If the post exists, convert it to a dictionary, else return None
        if post:
            return {
                "p_id": post.p_id,
                "p_user" : post.p_user,
                "p_title": post.p_title,
                "p_content": post.p_content,
                "p_image_path": post.p_image_path,
                "file_path": post.file_path,
                "p_location": post.p_location,
                "p_category": post.p_category,
                "like_num": post.like_num,
                "file": post.file,
                "upload_date": post.upload_date,
                "modify_date": post.modify_date
            }
        else:
            return None

    def display_posts_on_home(self,user_id):

        # 정렬 방식 선택
        sort_by = st.selectbox("정렬 방식", ["최신순", "인기순"])

        # 정렬 기준 설정
        if sort_by == "인기순":
            posts = session.query(Posting).order_by(Posting.like_num.desc()).all()  # 인기순으로 정렬
        else:
            posts = session.query(Posting).order_by(Posting.upload_date.desc()).all()  # 최신순으로 정렬

        if not posts:
            st.write("현재 추천 포스팅이 없습니다.")
            return

        # 포스트를 두 개씩 나열
        for i in range(0, len(posts), 2):
            cols = st.columns(2)  # 두 개의 컬럼 생성
            for j, col in enumerate(cols):
                if i + j < len(posts):
                    post = posts[i + j]  # 현재 포스트 데이터
                    with col:
                        st.subheader(post.p_title)

                        if user_id:
                            self.display_like_button(post.p_id, user_id)
                        self.fetch_location_data(post.p_id)

                        # 이미지 출력 (있는 경우)
                        if post.p_image_path:
                            self.create_location_name()
                            st.image(post.p_image_path, use_container_width=True)

                        with st.expander('더보기'):
                            self.display_post(post.p_id)




# ----------------------------------------------------카테고리 -----------------------------
class CategoryManager:
    def get_category_options(self):
        return session.query(FoodCategory).all()

    def get_category_names(self):
        categories = self.get_category_options()
        category_dict = {category.category: category.category_id for category in categories}
        return category_dict

    def category_selector(self):
        categories = self.get_category_names()
        if categories:
            category = st.selectbox(
                "카테고리 선택",
                options=list(categories.keys()),  # category names as options
                format_func=lambda x: x,  # Display the category name (the key of the dictionary)
                key="category_selectbox"
            )
            return categories[category]  # Return the category ID corresponding to the selected category
        else:
            st.error("등록된 카테고리가 없습니다. 관리자에게 문의하세요.")

    def category_id_to_name(self, category_id):
        categories = self.get_category_options()
        for category in categories:
            if category.category_id == category_id:
                return category.category
        return None

# -------------------------------------------------테마----------------------------------------------


class ThemeManager:
    def __init__(self, user_id):
        self.th = st.session_state
        self.user_id = user_id

        if "themes" not in self.th:
            saved_theme = self.get_saved_theme(user_id)  # Load saved theme from DB or default to dark
            self.th.themes = {
                "current_theme": saved_theme,  # Load saved theme (light/dark) for the user
                "light": {
                    "theme.base": "dark",
                    "theme.backgroundColor": "black",
                    "theme.textColor": "white",
                    "button_face": "어두운 모드 🌜"
                },
                "dark": {
                    "theme.base": "light",
                    "theme.backgroundColor": "white",
                    "theme.textColor": "#0a1464",
                    "button_face": "밝은 모드 🌞"
                }
            }

    def get_saved_theme(self, user_id):
        setting = session.query(Settings).filter(Settings.user == user_id).first()
        session.close()

        # Return the theme if valid, otherwise default to 'dark'
        return setting.current_theme if setting and setting.current_theme in ["light", "dark"] else 'dark'

    def save_theme(self, user_id, theme):
        """Save the selected theme for a user."""
        setting = session.query(Settings).filter(Settings.user == user_id).first()

        if setting:
            setting.current_theme = theme  # Update existing theme
        else:
            # Create new entry for the user if no settings exist
            setting = Settings(user=user_id, current_theme=theme)
            session.add(setting)

        session.commit()
        session.close()

    def change_theme(self, user_id):
        previous_theme = self.get_saved_theme(user_id)
        new_theme = "light" if previous_theme == "dark" else "dark"

        # Ensure the new theme exists in the themes dictionary
        if new_theme not in self.th.themes:
            st.error(f"Theme '{new_theme}' not found in theme dictionary")
            return

        # Apply the new theme settings
        theme_dict = self.th.themes[new_theme]
        for key, value in theme_dict.items():
            if key.startswith("theme"):
                st._config.set_option(key, value)

        # Save the new theme for the user
        self.save_theme(user_id, new_theme)

    def render_button(self, user_id):
        current_theme = self.get_saved_theme(user_id)
        button_label = self.th.themes.get(current_theme, {}).get("button_face",
                                                                 "Unknown theme")

        # Render the theme toggle button and handle the click event
        if st.button(button_label, use_container_width=True, key='change_theme'):
            self.change_theme(user_id)
            st.rerun()

# ----------------------------------------------------- 유저 프로필 ---------------------------------
class UserProfile:
    def __init__(self, upload_folder="profile_pictures"):
        self.upload_folder = upload_folder
        self.user_dao =  UserDAO()
        # Default profile picture URL
        self.default_profile_picture = (
            "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        )

        # Attempt to create the directory
        os.makedirs(self.upload_folder, exist_ok=True)

    def save_file(self, uploaded_file):
        # 이미지 저장 후 경로 반환
        if uploaded_file is not None:
            file_path = os.path.join(self.upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        return None

    def update_profile_picture(self, user_id, image_path):
        if image_path:
            success = self.user_dao.update_user_field(user_id, "profile_picture_path", image_path)
            return success, image_path
        return False, None

    def display_profile(self, user_id):

        user_vo = self.user_dao.get_user_vo(user_id)
        if user_vo:
            st.write(f"User Email: {user_vo.user_email}")
            profile_picture = user_vo.user_profile_picture

            # 프로필 사진 경로가 없거나 파일이 존재하지 않으면 기본 이미지 사용
            if not profile_picture or not os.path.exists(profile_picture):
                profile_picture = self.default_profile_picture

            st.image(profile_picture, caption=user_id, width=300)
        else:
            st.error("사용자 정보를 찾을 수 없습니다.")

    def upload_new_profile_picture(self, user_id):
        st.button("프로필 사진 변경", use_container_width=True, key='change_profile')
        uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])


        if st.button("업로드", key='upload'):

            image_path = self.save_file(uploaded_file)
            if image_path:
                # 프로필 사진 업데이트
                self.update_profile_picture(user_id, image_path)
                st.success("프로필 사진이 성공적으로 업데이트되었습니다.")
            else:
                st.error("파일 저장에 실패했습니다.")



class SetView:
    def __init__(self, user_vo):
        self.user_vo = user_vo
        self.theme_manager = ThemeManager(user_vo.user_id)
        self.like_button = Like()
        self.user_profile = UserProfile()
        self.user_dao = UserDAO()

    def update_user_field(self, field_name, field_value):
        # DB에서 업데이트한 후 user_vo 객체 동기화
        dao = UserDAO()
        if dao.update_user_field(self.user_vo.user_id, field_name, field_value):
            # DB 업데이트 후 새로운 UserVO 객체를 가져와서 세션에 업데이트
            updated_user = dao.get_user_vo(self.user_vo.user_id)
            if updated_user:
                self.user_vo = updated_user  # 세션에 저장된 user_vo 갱신
                st.session_state["user_vo"] = updated_user  # 세션 상태 갱신
                st.success(f"{field_name}이(가) 성공적으로 업데이트되었습니다.")
            else:
                st.error("업데이트 후 사용자 정보를 가져오는 데 실패했습니다.")
        else:
            st.error("사용자 정보를 업데이트하는 데 실패했습니다.")

    def render_alarm_settings(self):

        alarm_enabled = st.button("알람 설정", use_container_width=True, key='alarm')
        if alarm_enabled:
            st.write("알람이 설정되었습니다.")
        else:
            st.write("알람이 해제되었습니다.")

    def render_user_profile(self):
        st.write(f"**{self.user_vo.user_id}**")
        st.write(f"**Email:** {self.user_vo.user_email}")

        # Check if user_profile_picture is None or an empty string
        profile_picture = self.user_vo.user_profile_picture or "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

        # Display the image (use fallback if None or empty)
        st.image(profile_picture, width=100)

        with st.expander("내 정보 수정하기"):
            # 이메일 변경
            new_email = st.text_input("새 이메일 주소", value=self.user_vo.user_email)
            if st.button("이메일 변경", key='change_email'):
                self.update_user_field("user_email", new_email)

            # 프로필 사진 업로드
            uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image_path = self.user_profile.save_file(uploaded_file)
                self.update_user_field("profile_picture_path", image_path)

                st.success('포르필 사진이 변경되었습니다.')
                st.rerun()

    def render_posts(self):
        with st.expander('관심목록', icon='💗'):
            self.like_button.display_liked_posts()


# -----------------------------------------------------좋아요 목록 --------------------------------------------------

class Like:
    def __init__(self):
        if "posts" not in st.session_state:
            st.session_state.posts = []

    def fetch_liked_posts(self):
        liked_posts = session.query(Posting.p_user,Posting.p_content, Posting.p_title, Posting.p_image_path).filter(Posting.like_num > 0).all()
        session.close()
        return liked_posts

    def display_liked_posts(self):
        liked_posts = self.fetch_liked_posts()
        # Display liked posts with the like button
        if liked_posts:
            for post in liked_posts:
                post_user,post_content, post_title,p_image = post
                st.write(f"**Creator ID**: {post_user}")
                st.write(f"Title: {post_title}, content : {post_content}")
                if p_image:
                    st.image(p_image, width=100)
                st.write('--------')
        else:
            st.write("좋아요를 누른 포스팅이 없습니다.")

#----------------------------------------------채팅----------------------------------------------

class Chatting:
    def __init__(self, session):
        self.session = session

    def save_message(self, group_id, sender_id, message_text):
        new_message = Message(
            group_id=group_id,
            sender_id=sender_id,
            message_text=message_text,
            sent_at=datetime.now()
        )
        self.session.add(new_message)
        self.session.commit()
        return f"{sender_id}님의 메세지가 저장되었습니다. "

    def load_messages(self, group_id):
        messages = self.session.query(Message).filter_by(group_id=group_id).all()
        return messages


    def get_group_name(self, group_id):
        """Retrieve the group name by group_id."""
        group = self.session.query(Group).filter_by(group_id=group_id).first()
        if group:
            return group.group_name
        else:
            return "그룹이 존재하지 않습니다."

    def display_chat_interface(self, group_id):
        group_name = self.get_group_name(group_id)
        st.subheader(f"채팅: {group_name}")

        sender_id = st.session_state.get("user_id")
        if not sender_id:
            st.error("로그인이 필요합니다.")
            return

        # Initialize the message history for the group if it doesn't exist
        if f"messages_{group_id}" not in st.session_state:
            st.session_state[f"messages_{group_id}"] = self.load_messages(group_id)

        # Display the chat messages
        st.markdown("### 채팅 기록")
        for msg in st.session_state[f"messages_{group_id}"]:
            st.write(f"**{msg.sender_id}** ({msg.sent_at}): {msg.message_text}")

        # Initialize or retrieve the new message input field state
        if f"new_message_{group_id}" not in st.session_state:
            st.session_state[f"new_message_{group_id}"] = ""

        # Input field for new messages
        new_message = st.text_input(
            "메시지 입력",
            value=st.session_state[f"new_message_{group_id}"],
            key=f"chat_input_{group_id}"
        )
        st.session_state[f"new_message_{group_id}"] = new_message  # Maintain state

        # Send button logic
        if st.button("보내기", key=f"send_button_{group_id}"):
            if new_message.strip():
                self.save_message(group_id, sender_id, new_message)
                st.session_state[f"new_message_{group_id}"] = ""  # Clear the input field
                st.session_state[f"messages_{group_id}"] = self.load_messages(group_id)  # Refresh messages
            else:
                st.warning("메시지를 입력해주세요.")

        # Optionally, return chat history as a string
        chat_interface = ""
        for msg in st.session_state[f"messages_{group_id}"]:
            chat_interface += f"{msg.sent_at} - {msg.sender_id}: {msg.message_text}\n"

        return chat_interface

#--------------------------------------그룹 요청 데이터 관리 ----------------------------------------------

class GroupRequestDAO:

    #그룹 요청들을 반환한다.
    def get_request(self, group_id):
        requests = (
            session.query(OtherGroupRequest.requester_user_id)
            .filter(OtherGroupRequest.group_id == group_id)
            .all()
        )
        return [request.requester_user_id for request in requests]
    #그룹 요청을 승인한다
    def approve_request(self, group_id, requester_user_id):
        try:
            new_member = GroupMember(group_id=group_id, user_id=requester_user_id, role='member')
            session.add(new_member)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False

    #그룹 요청을 거절한다.
    def reject_request(self, group_id, requester_user_id):
        try:
            # Remove the request from the OtherGroupRequest table
            request_to_delete = (
                session.query(OtherGroupRequest)
                .filter(OtherGroupRequest.group_id == group_id, OtherGroupRequest.requester_user_id == requester_user_id)
                .first()
            )
            session.delete(request_to_delete)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False

    #유저가 보낸 요청
    def get_sent_request(self, user_id):
        sent_requests = (
            session.query(OtherGroupRequest.group_id, OtherGroupRequest.requester_user_id, Group.group_name)
            .join(Group, Group.group_id == OtherGroupRequest.group_id)
            .filter(OtherGroupRequest.requester_user_id == user_id)
            .all()
        )

        return [(group_id, group_name) for group_id, requester_user_id, group_name in sent_requests]



#-----------------------------------------------그룹관리 ----------------------------------------------------
class GroupManager:
    def __init__(self,user_id):
        self.user_id=user_id

    def get_user_groups(self):
        groups = (session.query(Group).all())
        return groups

    #그룹에 속해있는 멤버들의 아이디를 반환한다
    def get_group_members(self, group_id):
        # Query to get user_id, name, and role for the given group_id
        members = (
            session.query(User.user_id, GroupMember.role)  # Select user_name and role
            .join(GroupMember, User.user_id == GroupMember.user_id)  # Join User and GroupMember tables
            .filter(GroupMember.group_id == group_id)  # Filter by group_id
            .all()  # Fetch all results as a list of tuples
        )

        return members


    #그룹 정보 반환
    def get_group_info(self, group_id):
        # Query to get the basic group information
        group_info = (
            session.query(
                Group.group_id,
                Group.group_name,
                Group.status,
                Group.modify_date,
                Group.meeting_date,
                Group.meeting_time
            )
            .filter(Group.group_id == group_id)  # Filter by group_id
            .first()  # Get the first result (similar to fetchone)
        )

        return group_info

        # 그룹에 속한 멤버 수를 반환

    #그룹 멤버 수 반환
    def get_group_member_count(self, group_id):
        members = self.get_group_members(group_id)  # Use get_group_members to get the member list
        return len(members)

    #그룹멤버 추가 함수
    def add_group_member(self, group_id, role="admin"):
        current_date = datetime.now()

        try:
            # 멤버 추가
            new_member = GroupMember(
                group_id=group_id,
                user_id=self.user_id,
                role=role,
                joined_at=current_date
            )
            session.add(new_member)
            session.commit()
            st.success("그룹 멤버가 성공적으로 추가되었습니다!")
        except Exception as e:
            session.rollback()
            st.error(f"멤버 추가 중 오류 발생: {e}")

    #그룹의 상세정보를 반환함
    def show_group_details(self, group_id, group_name):
        st.subheader(f"그룹: {group_name}")

        # 컨테이너로 세부 정보와 채팅 표시
        with st.container():
            self.display_chat_interface(group_name, group_id)

    def get_group_name(self,group_id):
        group = session.query(Group).filter_by(group_id=group_id).first()
        return group.group_name if group else None

    #그룹의 creator인지 확인하는 함수
    def is_group_creator(self, group_id):

        group = session.query(Group).filter_by(group_id=group_id).first()
        return group and group.group_creator == self.user_id

    #그룹 삭제
    def delete_group(self,group_id):

        try:
            # 그룹 삭제
            group = session.query(Group).filter_by(id=group_id).first()
            if group:
                session.delete(group)
                session.commit()
        except Exception as e:
            session.rollback()
            st.error(f"그룹 삭제 중 오류 발생: {e}")

        finally:
            session.close()  # 세션 종료

    def update_group(self, group_id,group_name, category, status, meeting_date, meeting_time):
       try:
           # 그룹 레코드를 조회
           group = session.query(Group).filter(Group.group_id == group_id).first()


           if not group:
               st.error("그룹을 찾을 수 없습니다.")
               return

           # 수정할 데이터 설정
           group.group_name = group_name
           group.category = category  # selected_category는 튜플 형태로 가정
           group.status = status
           group.meeting_date = meeting_date
           group.meeting_time = meeting_time
           group.modify_date = datetime.now()


           # 세션 커밋
           session.commit()


           st.success(f"'{group_name}' 그룹이 성공적으로 수정되었습니다!")


       except Exception as e:
           st.error(f"DB 오류: {e}")
           session.rollback()  # 오류 발생 시 롤백


       finally:
           session.close()  # 세션 종료

    def get_my_groups(self,user_id):

        groups = session.query(Group).filter_by(group_creator=user_id).all()
        return [
            {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "category": group.category,
                "location": group.location,
                "status": group.status,
                "meeting_date" : group.meeting_date,
                "meeting_time" : group.meeting_time,
            }
            for group in groups
        ]

#--------------------------------------------------그룹 차단 데이터관리 -----------------------------------

class GroupBlockDAO:
   #사용자가 그룹을 차단함
   def block_group(self, user_id, group_id):
       try:
           # 그룹 차단 추가
           block = GroupBlock(user_id=user_id, blocked_group_id=group_id)


           # 세션에 추가하고 커밋
           session.add(block)
           session.commit()
           session.close()
           return True
       except Exception as e:
           print(f"그룹 차단 오류: {e}")
           session.rollback()  # 예외가 발생한 경우 롤백
       return False


   def unblock_group(self, user_id, group_id):
       try:
           # 그룹 차단 레코드 삭제
           block = session.query(GroupBlock).filter_by(user_id=user_id, blocked_group_id=group_id).first()


           if block:
               session.delete(block)  # 해당 레코드를 삭제
               session.commit()  # 커밋
               session.close()  # 세션 종료
               return True
           else:
               print("차단된 그룹이 존재하지 않습니다.")
               return False
       except Exception as e:
           print(f"그룹 차단 해제 오류: {e}")
           session.rollback()  # 예외가 발생한 경우 롤백
           session.close()
       return False


   #차단된 그룹을 조회하여 리스트로 반환함
   def get_blocked_groups(self, user_id):
       try:
           # 차단된 그룹 조회
           blocked_groups = session.query(GroupBlock.blocked_group_id).filter_by(user_id=user_id).all()


           session.close()  # 세션 종료


           # 결과를 리스트로 반환
           return [group[0] for group in blocked_groups]


       except Exception as e:
           print(f"차단된 그룹 조회 오류: {e}")
           session.close()  # 세션 종료
       return []


   #사용자가 그룹을 차단했는지 확인함
   def is_group_blocked(self, user_id, group_id):
       try:
           # 조건에 맞는 차단된 그룹 레코드 존재 여부 확인
           result = session.query(GroupBlock).filter_by(user_id=user_id, blocked_group_id=group_id).first()


           session.close()  # 세션 종료


           # 결과가 있으면 True, 없으면 False 반환
           return result is not None


       except Exception as e:
           print(f"그룹 차단 확인 오류: {e}")
           session.close()  # 세션 종료
       return False
#------------------------------------------그룹 검색 ---------------------------------

class GroupSearch:
    #input을 받은 것으로 검색
   def search_groups(self, user_input, search_criteria):

       # 기본적인 Group 쿼리 시작
       query = session.query(Group.group_name, Group.group_creator, Group.meeting_date, Group.meeting_time,
                             FoodCategory.category, Location.location_name, func.count(GroupMember.user_id).label('current_members')) \
                      .join(FoodCategory, Group.category == FoodCategory.category_id, isouter=True) \
                      .join(Location, Group.location == Location.location_id, isouter=True) \
                      .join(GroupMember, Group.group_id == GroupMember.group_id, isouter=True)


       # 검색 기준에 따른 조건 추가
       if search_criteria == "이름":
           query = query.filter(Group.group_name.like(f"%{user_input}%"))
       elif search_criteria == "날짜":
           query = query.filter(Group.meeting_date == user_input)
       elif search_criteria == "카테고리":
           query = query.filter(Group.category == user_input)


       # 그룹 데이터 조회 실행
       groups = query.group_by(Group.group_id).all()


       session.close()


       return groups


#--------------------------------------------------친구 관리 --------------------------------------------------

class FriendManager():
    def __init__(self,user_id):
        self.user_id=user_id

    #친구 리스트
    def show_friend_list(self):
        try:
            # 친구 목록 가져오기
            friends = session.query(Friend.friend_user_id).filter(Friend.user_id == self.user_id).all()

            if friends:
                st.title("내 친구 리스트")
                for friend in friends:
                    st.write(f"- {friend.friend_user_id}")
            else:
                st.write("친구가 없습니다.")

        finally:
            session.close()  # 세션 종료

    # 차단 리스트 출력
    def show_blocked_list(self):

        try:
            # 차단된 사용자 목록 가져오기
            blocked_users = session.query(Block.blocked_user_id).filter(Block.user_id == self.user_id).all()

            if blocked_users:
                st.title("차단 목록")
                for blocked in blocked_users:
                    st.write(f"- {blocked.blocked_user_id}")
            else:
                st.write("차단된 사용자가 없습니다.")


        finally:
            session.close()  # 세션 종료

    # 차단
    def block_friend(self, friend_id):

        if self.user_id == friend_id:
            st.error("자신을 차단할 수 없습니다.")
            return

        try:
            # user 테이블에서 해당 ID 존재 여부 확인
            user_exists = session.query(User).filter(User.user_id == friend_id).first()
            if not user_exists:
                st.error("없는 ID입니다.")  # 해당 ID가 user 테이블에 없을 경우
                return

            # 이미 차단되었는지 확인
            already_blocked = session.query(Block).filter(
                Block.user_id == self.user_id,
                Block.blocked_user_id == friend_id
            ).first()
            if already_blocked:
                st.error("이미 차단된 사용자입니다.")
                return

            # 친구 목록에서 삭제 (차단된 경우 친구에서 제거)
            session.query(Friend).filter(
                Friend.user_id == self.user_id,
                Friend.friend_user_id == friend_id
            ).delete()

            session.query(Friend).filter(
                Friend.user_id == friend_id,
                Friend.friend_user_id == self.user_id
            ).delete()

            # 차단 테이블에 추가
            new_block = Block(user_id=self.user_id, blocked_user_id=friend_id)
            session.add(new_block)

            # 커밋하여 변경사항 저장
            session.commit()

            st.success(f"{friend_id}님을 차단하였습니다.")

        finally:
            session.close()  # 세션 종료

    # 차단 해제
    def unblock_friend(self, friend_id):

        try:
            # 차단된 사용자인지 확인
            blocked = session.query(Block).filter(
                Block.user_id == self.user_id,
                Block.blocked_user_id == friend_id
            ).first()

            if not blocked:
                st.error("차단된 사용자가 아닙니다.")
                return

            # 차단 해제
            session.delete(blocked)
            session.commit()

            st.success(f"{friend_id}님을 차단 해제하였습니다.")

        finally:
            session.close()  # 세션 종료

    # 친구 삭제
    def delete_friend(self, friend_id):

        if self.user_id  == friend_id:
            st.error("자신을 삭제할 수 없습니다.")
            return

        try:
            # 친구 관계 확인
            is_friend = session.query(Friend).filter(
                Friend.user_id == self.user_id,
                Friend.friend_user_id == friend_id
            ).first()

            if not is_friend:
                st.error("해당 유저는 내 친구 리스트에 없는 유저입니다.")
                return

            # 친구 삭제
            session.delete(is_friend)
            session.commit()

            st.success(f"{friend_id}님을 친구 목록에서 삭제하였습니다.")


        finally:
            session.close()  # 세션 종료


#------------------------------------------------------친구 요청 관리 --------------------------------------------------

class FriendRequest:
    def __init__(self, user_id):
        self.user_id = user_id

    # 친구 신청 함수
    def add_friend(self, friend_id):

        if self.user_id== friend_id:
            st.error("자신을 친구로 추가할 수 없습니다.")
            return

        try:
            # 차단 여부 확인
            blocked_user = session.query(Block).filter(Block.user_id == self.user_id,
                                                       Block.blocked_user_id == friend_id).first()
            if blocked_user:
                st.error("먼저 차단을 해제해주세요.")
                return

            # 상대방 존재 확인
            user_exists = session.query(User).filter(User.user_id == friend_id).first()
            if not user_exists:
                st.error("없는 ID입니다.")
                return

            # 이미 친구인지 확인
            already_friends = session.query(FriendRequest).filter(FriendRequest.user_id == self.user_id,
                                                                  FriendRequest.friend_user_id == friend_id).first()
            if already_friends:
                st.error("이미 친구입니다.")
                return

            # 이미 요청을 보냈는지 확인
            already_requested = session.query(FriendRequest).filter(FriendRequest.user_id == self.user_id,
                                                                    FriendRequest.requested_user_id == friend_id).first()
            if already_requested:
                st.error("이미 친구 요청을 보냈습니다.")
                return

            # 친구 요청 등록
            new_friend_request = FriendRequest(user_id=self.user_id, requested_user_id=friend_id)
            new_other_request = FriendRequest(user_id=friend_id, requested_user_id=self.user_id)

            session.add(new_friend_request)
            session.add(new_other_request)

            session.commit()

            # 디버깅 로그 (데이터 저장 확인)
            DEBUG_MODE = True
            if DEBUG_MODE:
                friend_requests = session.query(FriendRequest).filter(FriendRequest.user_id == self.user_id,
                                                                      FriendRequest.requested_user_id == friend_id).all()
                st.write("My Friend Requests:", friend_requests)

            st.success(f"{friend_id}님에게 친구 요청을 보냈습니다. 상대방이 수락할 때까지 기다려주세요.")


        finally:
            session.close()  # 세션 종료

    # 내가 보낸 요청 목록
    def get_my_sent_requests(self):

        try:
            # 내가 보낸 친구 요청 목록을 가져오기
            sent_requests = session.query(MyFriendRequest.requested_user_id).filter(
                MyFriendRequest.user_id == self.user_id).all()

            # 결과가 없으면 빈 리스트 반환
            if not sent_requests:
                return []

            return [request[0] for request in sent_requests]  # 튜플에서 요청한 user_id만 반환


        finally:
            session.close()  # 세션 종료

    # 내가 받은 친구 요청
    def get_received_requests(self):

        try:
            # 내가 받은 친구 요청 목록을 가져오기
            received_requests = session.query(OtherRequest.requester_user_id).filter(
                OtherRequest.user_id == self.user_id).all()

            # 결과가 없으면 빈 리스트 반환
            if not received_requests:
                return []

            return [request[0] for request in received_requests]  # 튜플에서 요청한 user_id만 반환


        finally:
            session.close()  # 세션 종료

    # 친구 신청 받기
    def accept_friend_request(self, requester_id):

        try:
            # 친구 관계 추가
            new_friend_1 = Friend(user_id=self.user_id, friend_user_id=requester_id)
            new_friend_2 = Friend(user_id=requester_id, friend_user_id=self.user_id)
            session.add(new_friend_1)
            session.add(new_friend_2)

            # 요청 삭제 (수락된 경우)
            # 내가 받은 친구 요청 삭제
            request_to_delete = session.query(MyFriendRequest).filter(
                MyFriendRequest.requested_user_id == self.user_id,
                MyFriendRequest.user_id == requester_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            # 상대방이 보낸 요청 삭제
            request_to_delete = session.query(OtherRequest).filter(
                OtherRequest.user_id == self.user_id,
                OtherRequest.requester_user_id == requester_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            # 상대방의 요청 리스트에서도 삭제 (반대 방향)
            request_to_delete = session.query(MyFriendRequest).filter(
                MyFriendRequest.requested_user_id == requester_id,
                MyFriendRequest.user_id == self.user_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            request_to_delete = session.query(OtherRequest).filter(
                OtherRequest.user_id == requester_id,
                OtherRequest.requester_user_id == self.user_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            # 커밋하여 변경사항 저장
            session.commit()
            st.success(f"{requester_id}님과 친구가 되었습니다.")


        finally:
            session.close()  # 세션 종료

    # 친구 신청 거절
    def reject_friend_request(self, requester_id):

        try:
            # 내가 받은 친구 요청 삭제
            request_to_delete = session.query(MyFriendRequest).filter(
                MyFriendRequest.requested_user_id == self.user_id,
                MyFriendRequest.user_id == requester_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            # 내가 받은 요청 리스트에서 삭제
            request_to_delete = session.query(OtherRequest).filter(
                OtherRequest.user_id == self.user_id,
                OtherRequest.requester_user_id == requester_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            # 상대방의 요청 리스트에서도 삭제
            request_to_delete = session.query(MyFriendRequest).filter(
                MyFriendRequest.requested_user_id == requester_id,
                MyFriendRequest.user_id == self.user_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            request_to_delete = session.query(OtherRequest).filter(
                OtherRequest.user_id == requester_id,
                OtherRequest.requester_user_id == self.user_id
            ).first()
            if request_to_delete:
                session.delete(request_to_delete)

            # 커밋하여 변경사항 저장
            session.commit()
            st.success(f"{requester_id}님의 친구 요청을 거절했습니다.")

        finally:
            session.close()  # 세션 종료


app = Page()
app.render_page()




