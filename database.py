import streamlit as st
import pymysql


# MySQL 데이터베이스 연결 설정
def get_db_connection():
    return pymysql.connect(
        host='localhost',  # MySQL 서버 호스트
        user='zip',  # MySQL 사용자
        password='12zipzip34',  # MySQL 비밀번호
        database='zip',  # 사용할 데이터베이스
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


# 카테고리 목록 가져오기 (category_id와 category_name을 모두 가져옴)
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT category_id, category FROM food_categories"
    cursor.execute(query)
    categories = cursor.fetchall()

    conn.close()
    return categories


# 포스팅 등록
def register_posting(p_name, selected_category_ids, file):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 파일이 업로드되지 않으면 None으로 처리
    file_data = file.read() if file else None

    # 포스팅 등록 쿼리
    query = """
        INSERT INTO posting (p_name, p_category, file)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (p_name, selected_category_ids[0], file_data))  # 카테고리 ID를 사용
    conn.commit()
    conn.close()


# Streamlit 앱 UI
def main():
    st.title("포스팅 관리 시스템")

    # 카테고리 가져오기
    categories = get_categories()

    # 카테고리 이름만 추출하여 multiselect에 사용
    category_names = [category['category'] for category in categories]

    # 포스팅 등록
    st.header("포스팅 등록")
    with st.form("post_form"):
        p_name = st.text_input("포스팅 이름")
        selected_categories = st.multiselect("카테고리 선택", options=category_names)
        file = st.file_uploader("파일 업로드", type=["jpg", "png", "pdf", "docx"])

        submit_button = st.form_submit_button(label="등록")

        if submit_button:
            if p_name and selected_categories:
                # 선택된 카테고리 이름을 category_id로 변환
                selected_category_ids = [category['category_id'] for category in categories if
                                         category['category'] in selected_categories]
                register_posting(p_name, selected_category_ids, file)
                st.success("포스팅이 등록되었습니다!")
            else:
                st.error("모든 필드를 채워주세요.")


if __name__ == "__main__":
    main()
