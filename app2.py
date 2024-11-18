import streamlit as st
import os
from database import create_post, update_post, delete_post, get_posts, get_post

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 파일 업로드 처리
def save_file(uploaded_file, folder):
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


# 글 등록 UI
def create_post_ui():
    st.header("새 글 작성")

    title = st.text_input("제목")
    content = st.text_area("내용")
    image = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
    file = st.file_uploader("파일 업로드", type=["pdf", "docx", "txt"])

    if st.button("등록"):
        if title and content:
            image_path = save_file(image, UPLOAD_FOLDER) if image else None
            file_path = save_file(file, UPLOAD_FOLDER) if file else None
            create_post(title, content, image_path, file_path)
            st.success("글이 등록되었습니다.")
        else:
            st.error("제목과 내용을 입력해주세요.")


# 글 수정 UI
def update_post_ui():
    st.header("글 수정")

    post_id = st.number_input("글 ID", min_value=1)
    post = get_post(post_id)

    if post:
        title = st.text_input("제목", post[1])
        content = st.text_area("내용", post[2])
        image = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"], key="image_upload")
        file = st.file_uploader("파일 업로드", type=["pdf", "docx", "txt"], key="file_upload")

        if st.button("수정"):
            image_path = save_file(image, UPLOAD_FOLDER) if image else post[3]
            file_path = save_file(file, UPLOAD_FOLDER) if file else post[4]
            update_post(post_id, title, content, image_path, file_path)
            st.success("글이 수정되었습니다.")
    else:
        st.error("해당 ID의 글을 찾을 수 없습니다.")


# 글 삭제 UI
def delete_post_ui():
    st.header("글 삭제")

    post_id = st.number_input("글 ID", min_value=1)
    if st.button("삭제"):
        delete_post(post_id)
        st.success("글이 삭제되었습니다.")


# 글 목록 UI
def display_posts():
    posts = get_posts()
    if posts:
        for post in posts:
            st.subheader(post[1])  # 제목
            st.write(post[2])  # 내용
            if post[3]:
                st.image(post[3])  # 이미지
            if post[4]:
                st.download_button("파일 다운로드", data=open(post[4], 'rb'), file_name=os.path.basename(post[4]),
                                   mime="application/octet-stream")
            st.write(f"작성일: {post[5]}")
            st.write(f"수정일: {post[6]}")
            st.markdown("---")
    else:
        st.write("등록된 글이 없습니다.")


# Streamlit 앱 UI
st.title("게시판 시스템")

menu = st.sidebar.selectbox("메뉴", ["글 목록", "새 글 작성", "글 수정", "글 삭제"])

if menu == "글 목록":
    display_posts()
elif menu == "새 글 작성":
    create_post_ui()
elif menu == "글 수정":
    update_post_ui()
elif menu == "글 삭제":
    delete_post_ui()
