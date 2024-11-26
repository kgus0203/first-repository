import streamlit as st
import sqlite3

# 데이터베이스 연결 함수
def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형식으로 반환
    return conn

class Group:
    def __init__(self, group_id, group_name, group_creator, category, location):
        self.group_id = group_id
        self.group_name = group_name
        self.group_creator = group_creator
        self.category = category
        self.location = location

    # 그룹 생성
    def create_group(self):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO "group" (group_id, group_name, group_creator, category, location, update_date, modify_date)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (self.group_id, self.group_name, self.group_creator, self.category, self.location))
            conn.commit()
            st.success("그룹이 생성되었습니다!")
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            conn.close()
class GroupDAO:
    # 그룹 검색 (카테고리 이름 포함)
    def search_group_by_name(self, group_name):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            query = """
            SELECT g.*, fc.category
            FROM "group" g
            LEFT JOIN food_categories fc ON g.category = fc.category_id
            WHERE g.group_name LIKE ?
            """
            cursor.execute(query, ('%' + group_name + '%',))
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            conn.close()

    def get_groups_by_member_count(self):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            query = """
               SELECT g.group_id, g.group_name, g.group_creator, g.category, g.location, g.date, g.modify_date,
                      COUNT(gm.user_id) AS member_count
               FROM "group" g
               LEFT JOIN group_member gm ON g.group_id = gm.group_id
               GROUP BY g.group_id
               ORDER BY member_count DESC
               """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            conn.close()

    # 카테고리로 그룹 검색 (카테고리 이름 포함)
    def search_group_by_category(self, category_id):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            query = """
            SELECT g.*, fc.category
            FROM "group" g
            LEFT JOIN food_categories fc ON g.category = fc.category_id
            WHERE g.category = ?
            """
            cursor.execute(query, (category_id,))
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            conn.close()


class FoodCategoryDAO:
    def get_all_categories(self):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT category_id, category FROM food_categories"
            cursor.execute(query)
            categories = cursor.fetchall()
            return categories
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            conn.close()

    # 카테고리로 그룹 검색
    def search_group_by_category(self, category_id):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM \"group\" WHERE category = ?"
            cursor.execute(query, (category_id,))
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            conn.close()
def display_group_info(groups):
    for group in groups:
        st.write(f"**그룹 이름**: {group['group_name']}")
        st.write(f"**그룹 ID**: {group['group_id']}")
        st.write(f"**그룹 생성자**: {group['group_creator']}")
        st.write(f"**카테고리**: {group['category']}")  # 카테고리 이름 표시
        st.write(f"**위치 ID**: {group['location']}")
        st.write(f"**등록 날짜**: {group['date']}, **수정 날짜**: {group['modify_date']}")
        st.write("---")


# 그룹 생성
# 그룹 생성 페이지에서 카테고리 이름을 선택할 수 있도록 수정
def create_group_page():
    st.title("그룹 생성")

    group_id = st.text_input("그룹 ID")
    group_name = st.text_input("그룹 이름")
    group_creator = st.text_input("그룹 생성자 (사용자 ID)")

    # 카테고리 목록 가져오기
    food_category_dao = FoodCategoryDAO()
    categories = food_category_dao.get_all_categories()

    # 카테고리 이름을 표시하고, 해당 카테고리의 ID를 선택
    category_options = [category['category'] for category in categories]
    category_dict = {category['category']: category['category_id'] for category in categories}

    selected_category_name = st.selectbox("카테고리 선택", category_options)
    selected_category_id = category_dict.get(selected_category_name)

    location = st.selectbox("위치 선택", [1, 2, 3])  # 예시 위치 ID 목록 (1, 2, 3)

    if st.button("그룹 생성"):
        if not group_id or not group_name or not group_creator or not selected_category_id:
            st.error("모든 필드를 입력해 주세요.")
        else:
            new_group = Group(group_id, group_name, group_creator, selected_category_id, location)
            new_group.create_group()


# 그룹 검색
def search_group_page():
    st.title("그룹 검색")

    search_term = st.text_input("그룹 이름으로 검색")
    if st.button("검색"):
        if not search_term:
            st.error("검색어를 입력해 주세요.")
        else:
            group_dao = GroupDAO()
            result = group_dao.search_group_by_name(search_term)
            if result:
                display_group_info(result)
            else:
                st.write("검색된 그룹이 없습니다.")


# 인기순으로 그룹을 표시하는 페이지 (인원 수 기준)
def display_groups_by_member_count():
    st.title("인원 많은 그룹 열람")

    # 그룹 DAO를 사용하여 인원 수 기준으로 그룹을 가져옵니다.
    group_dao = GroupDAO()
    groups = group_dao.get_groups_by_member_count()

    if groups:
        for group in groups:
            st.write(f"**그룹 이름**: {group['group_name']}")
            st.write(f"**그룹 ID**: {group['group_id']}")
            st.write(f"**그룹 생성자**: {group['group_creator']}")
            st.write(f"**참여자 수**: {group['member_count']}명")  # 참여자 수 표시
            st.write(f"**카테고리 ID**: {group['category']}")
            st.write(f"**위치 ID**: {group['location']}")
            st.write(f"**등록 날짜**: {group['date']}, **수정 날짜**: {group['modify_date']}")
            st.write("---")
    else:
        st.write("참여자가 많은 그룹이 없습니다.")

# 페이지 선택
page = st.sidebar.selectbox("페이지 선택", ["인원 많은 그룹 열람", "그룹 생성", "그룹 검색"])

if page == "인원 많은 그룹 열람":
    display_groups_by_member_count()
elif page == "그룹 생성":
    create_group_page()
elif page == "그룹 검색":
    search_group_page()


