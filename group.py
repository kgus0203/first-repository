import streamlit as st
import sqlite3
import requests
import pandas as pd
from datetime import datetime



# 카테고리 DAO
class CategoryDAO:
    def __init__(self, db_name="zip.db"):
        self.db_name = db_name

    def create_connection(self):
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            st.error(f"DB 연결 실패: {e}")
            return None

    def get_all_categories(self):
        conn = self.create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT category_id, category FROM food_categories")
            return cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return []
        finally:
            conn.close()
class LocationSearch:
    def __init__(self, kakao_api_key):
        self.kakao_api_key = kakao_api_key

    def search_location(self, query):
        """카카오 API를 사용하여 장소 검색"""
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {
            "Authorization": f"KakaoAK {self.kakao_api_key}"
        }
        params = {
            "query": query,
            "category_group_code": "SW8,FD6,CE7"  # 음식점, 카페 등
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get("documents", [])
            else:
                st.error(f"API 요청 오류: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"요청 실패: {e}")
            return None

    def display_location_on_map(self):
        """장소 검색 및 지도 표시"""
        query = st.text_input("검색할 장소를 입력하세요:", "영남대역")
        search_button = st.button("검색")

        if search_button and query:
            results = self.search_location(query)
            if results:
                # 검색 결과 데이터프레임 생성
                locations = [
                    {"name": place["place_name"],
                     "address": place["address_name"],
                     "latitude": float(place["y"]),
                     "longitude": float(place["x"])}
                    for place in results
                ]
                df = pd.DataFrame(locations)

                # st.map으로 지도 표시
                st.map(df[["latitude", "longitude"]])

                # 결과 선택
                selected_place = st.selectbox(
                    "검색 결과를 선택하세요:",
                    [loc["name"] for loc in locations]
                )

                # 선택된 장소 정보 표시
                location_data = next((loc for loc in locations if loc["name"] == selected_place), None)
                if location_data:
                    st.write(f"**장소 이름:** {location_data['name']}")
                    st.write(f"**주소:** {location_data['address']}")
                    return location_data
        return None

# 그룹 생성
class GroupAndLocationApp:
    def __init__(self, db_name="zip.db", kakao_api_key="393132b4dfde1b54fc18b3bacc06eb3f"):
        self.db_name = db_name
        self.kakao_api_key = kakao_api_key
        self.location_search = LocationSearch(kakao_api_key)
        self.init_chat_db()  # 메시지 테이블 초기화

    def create_connection(self):
        """데이터베이스 연결 생성"""
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            st.error(f"DB 연결 실패: {e}")
            return None

    def my_groups_page(self):
        """내가 속한 그룹을 조회하는 페이지"""
        st.header("내가 속한 그룹")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        if not conn:
            st.error("데이터베이스 연결 실패")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.group_id, g.group_name, g.modify_date, COUNT(gm.user_id) AS current_members
                FROM "group" g
                JOIN group_member gm ON g.group_id = gm.group_id
                WHERE gm.user_id = ?
                GROUP BY g.group_id
            """, (user_id,))
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("참여 중인 그룹이 없습니다.")
            return

        for group_id, group_name, modify_date, current_members in groups:
            st.write(f"**그룹 이름:** {group_name}")
            st.write(f"**현재 인원수:** {current_members}명")
            st.write(f"**마지막 수정일:** {modify_date}")
            if st.button(f"열기", key=f"open_group_{group_id}"):
                self.show_group_details(group_id)
            st.markdown("---")

    def show_group_details(self, group_id):
        """선택한 그룹의 세부 정보 및 채팅 기능 표시"""
        conn = self.create_connection()
        if not conn:
            st.error("데이터베이스 연결 실패")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.group_name, g.group_creator, COUNT(gm.user_id) AS current_members
                FROM "group" g
                JOIN group_member gm ON g.group_id = gm.group_id
                WHERE g.group_id = ?
            """, (group_id,))
            group_info = cursor.fetchone()

            if not group_info:
                st.error("그룹 정보를 불러올 수 없습니다.")
                return

            group_name, group_creator, current_members = group_info

            cursor.execute("""
                SELECT gm.user_id, CASE WHEN gm.role = 'admin' THEN '방장' ELSE '멤버' END AS role
                FROM group_member gm
                WHERE gm.group_id = ?
            """, (group_id,))
            members = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        # 그룹 세부 정보와 채팅 인터페이스
        with st.expander(f"{group_name} - 채팅", expanded=True):
            st.write(f"**현재 인원수:** {current_members}명")
            st.write(f"**방장:** {group_creator}")
            st.markdown("### 멤버 목록")
            for user_id, role in members:
                st.write(f"- {user_id} ({role})")

            self.display_chat_interface(group_name)
    def init_chat_db(self):
        """채팅 데이터베이스 초기화"""
        conn = sqlite3.connect('chatroom.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            room_name TEXT,
                            username TEXT,
                            message TEXT,
                            timestamp DATETIME)''')
        conn.commit()
        conn.close()

    def save_message(self, room_name, username, message):
        """메시지 저장"""
        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            timestamp = datetime.now()
            cursor.execute(
                "INSERT INTO messages (room_name, username, message, timestamp) VALUES (?, ?, ?, ?)",
                (room_name, username, message, timestamp)
            )
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"메시지 저장 오류: {e}")
        finally:
            conn.close()

    def load_messages(self, group_id):
        """메시지 불러오기"""
        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sender_id, message_text, sent_at FROM messages WHERE group_id = ? ORDER BY sent_at ASC",
                (group_id,)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"메시지 불러오기 오류: {e}")
            return []
        finally:
            conn.close()

    def display_chat_interface(self, group_name, group_id):
        """채팅 UI"""
        st.subheader(f"채팅: {group_name}")

        # 로그인 상태 확인
        sender_id = st.session_state.get("user_id")
        if not sender_id:
            st.error("로그인이 필요합니다.")
            return

        # 메시지 상태 초기화
        if f"messages_{group_id}" not in st.session_state:
            st.session_state[f"messages_{group_id}"] = self.load_messages(group_id)

        # 메시지 기록 출력
        st.markdown("### 채팅 기록")
        for sender_id, message_text, sent_at in st.session_state[f"messages_{group_id}"]:
            formatted_time = datetime.strptime(sent_at, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
            st.write(f"**{sender_id}** ({formatted_time}): {message_text}")

        # 메시지 입력
        new_message = st.text_input("메시지 입력", key=f"chat_input_{group_id}")

        if st.button("보내기", key=f"send_button_{group_id}"):
            if new_message.strip():
                self.save_message(group_id, sender_id, new_message)
                # 메시지 상태 업데이트
                st.session_state[f"messages_{group_id}"] = self.load_messages(group_id)
                st.experimental_rerun()  # 채팅 UI 새로고침
            else:
                st.warning("메시지를 입력해주세요.")

    def save_message(self, group_id, sender_id, message):
        """메시지 저장"""
        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO messages (group_id, sender_id, message_text, sent_at) VALUES (?, ?, ?, ?)",
                (group_id, sender_id, message, timestamp)
            )
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"메시지 저장 오류: {e}")
        finally:
            conn.close()


    def my_groups_page(self):
        """내가 속한 그룹을 조회하는 페이지"""
        st.header("내가 속한 그룹")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        if not conn:
            st.error("데이터베이스 연결 실패")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT g.group_id, g.group_name, g.modify_date, COUNT(gm.user_id) AS current_members
                FROM "group" g
                JOIN group_member gm ON g.group_id = gm.group_id
                WHERE gm.user_id = ?
                GROUP BY g.group_id
            """, (user_id,))
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("참여 중인 그룹이 없습니다.")
            return

        for group_id, group_name, modify_date, current_members in groups:
            st.write(f"**그룹 이름:** {group_name}")
            st.write(f"**현재 인원수:** {current_members}명")
            st.write(f"**마지막 수정일:** {modify_date}")
            if st.button(f"열기", key=f"open_group_{group_id}"):
                self.show_group_details(group_id, group_name)
            st.markdown("---")

    def show_group_details(self, group_id, group_name):
        """선택한 그룹의 세부 정보 및 채팅 기능 표시"""
        st.subheader(f"그룹: {group_name}")

        # 컨테이너로 세부 정보와 채팅 표시
        with st.container():
            self.display_chat_interface(group_name, group_id)





    # 장소 검색 및 저장
    def location_page(self):
        st.header("장소 검색 및 저장")

        # 장소 검색 및 지도 표시
        location_data = self.location_search.display_location_on_map()

        # 장소 저장
        if location_data and st.button("저장"):
            self.save_location(
                location_data["name"],
                location_data["address"],
                location_data["latitude"],
                location_data["longitude"]
            )
            st.success("장소가 저장되었습니다!")



    def save_location(self, location_name, address_name, latitude, longitude):
        conn = self.create_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO locations (location_name, address_name, latitude, longitude)
                VALUES (?, ?, ?, ?)
            """, (location_name, address_name, latitude, longitude))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"DB 저장 실패: {e}")
        finally:
            conn.close()

    def search_location(self, query):
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {
            "Authorization": f"KakaoAK {self.kakao_api_key}"
        }
        params = {
            "query": query,
            "category_group_code": "SW8,FD6,CE7,AT4"  # 음식점, 카페, 관광 명소
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get("documents", [])
            elif response.status_code == 401:
                st.error("API 인증 실패: REST API 키를 확인하세요.")
            else:
                st.error(f"API 요청 오류: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"요청 실패: {e}")
        return None

    def group_creation_page(self):
        """그룹 생성 페이지"""
        st.header("그룹 생성")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        # 그룹 이름 입력
        group_name = st.text_input("그룹 이름", placeholder="그룹 이름을 입력하세요")
        max_members = st.number_input("최대 인원 수", min_value=2, max_value=10, step=1, value=10)

        # 약속 날짜와 시간 추가 여부
        add_schedule = st.checkbox("약속 날짜와 시간 설정")

        # 약속 날짜와 시간 입력 (체크박스 선택 시 활성화)
        meeting_date = None
        meeting_time_str = None
        if add_schedule:
            meeting_date = st.date_input("약속 날짜 선택")
            meeting_time = st.time_input("약속 시간 선택")
            meeting_time_str = meeting_time.strftime("%H:%M:%S")  # 시간 문자열로 변환

        # 카테고리 선택
        dao = CategoryDAO()
        categories = dao.get_all_categories()
        if categories:
            category = st.selectbox("카테고리 선택", options=categories, format_func=lambda x: x[1])
        else:
            st.error("등록된 카테고리가 없습니다.")
            return

        # 장소 선택
        conn = self.create_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT location_id, location_name FROM locations")
            locations = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if locations:
            location_id = st.selectbox("장소 선택", options=locations, format_func=lambda x: x[1])
        else:
            st.error("등록된 장소가 없습니다.")
            return

        # 그룹 생성 버튼
        if st.button("그룹 생성"):
            if not group_name or not location_id:
                st.error("모든 필수 입력 항목을 입력해주세요.")
            else:
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = self.create_connection()
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
                            (group_name, user_id, category[0], location_id[0], meeting_date, meeting_time_str,
                             current_date, current_date),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO "group" (group_name, group_creator, category, location, update_date, modify_date, status)
                            VALUES (?, ?, ?, ?, ?, ?, '진행 중')
                            """,
                            (group_name, user_id, category[0], location_id[0], current_date, current_date),
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
                    st.error(f"DB 오류: {e}")
                finally:
                    conn.close()

    # 그룹 생성 페이지 수정

    def group_update_page(self):
        st.header("그룹 수정")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT group_id, group_name FROM "group"
                WHERE group_creator = ?
                """,
                (user_id,),
            )
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("수정 가능한 그룹이 없습니다.")
            return

        selected_group = st.selectbox("수정할 그룹을 선택하세요:", groups, format_func=lambda x: x[1])
        group_id = selected_group[0]

        # 현재 그룹 데이터 가져오기
        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT group_name, category, location, status, meeting_date, meeting_time
                FROM "group"
                WHERE group_id = ?
                """,
                (group_id,),
            )
            group_data = cursor.fetchone()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        group_name = st.text_input("그룹 이름", value=group_data[0])
        dao = CategoryDAO()
        categories = dao.get_all_categories()
        selected_category = st.selectbox(
            "카테고리 선택",
            options=categories,
            index=[cat[0] for cat in categories].index(group_data[1]),
            format_func=lambda x: x[1],
        )

        conn = sqlite3.connect("zip.db")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT location_id, location_name FROM locations")
            locations = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        selected_location = st.selectbox(
            "장소 선택",
            options=locations,
            index=[loc[0] for loc in locations].index(group_data[2]),
            format_func=lambda x: x[1],
        )

        # 약속 날짜와 시간 추가
        if group_data[4] is not None:
            meeting_date = st.date_input("약속 날짜", value=datetime.strptime(group_data[4], "%Y-%m-%d").date())
        else:
            meeting_date = st.date_input("약속 날짜", value=datetime.today().date())  # 기본값: 오늘 날짜

        if group_data[5] is not None:
            meeting_time = st.time_input("약속 시간", value=datetime.strptime(group_data[5], "%H:%M:%S").time())
        else:
            meeting_time = st.time_input("약속 시간", value=datetime.now().time())  # 기본값: 현재 시간


        status_choices = ["진행 중", "완료", "취소"]
        selected_status = st.selectbox("그룹 상태", options=status_choices, index=status_choices.index(group_data[3]))

        if st.button("그룹 수정"):
            try:
                conn = self.create_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE "group"
                    SET group_name = ?, category = ?, location = ?, status = ?, meeting_date = ?, meeting_time = ?, modify_date = ?
                    WHERE group_id = ?
                    """,
                    (
                        group_name,
                        selected_category[0],
                        selected_location[0],
                        selected_status,
                        meeting_date.strftime("%Y-%m-%d"),
                        meeting_time.strftime("%H:%M:%S"),
                        datetime.now(),
                        group_id,
                    ),
                )
                conn.commit()
                st.success(f"'{group_name}' 그룹이 성공적으로 수정되었습니다!")
            except sqlite3.Error as e:
                st.error(f"DB 오류: {e}")
            finally:
                conn.close()

        # 그룹 삭제

    def group_delete_page(self):
        st.header("그룹 삭제")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT group_id, group_name FROM "group"
                WHERE group_creator = ?
            """,
                (user_id,),
            )
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("삭제 가능한 그룹이 없습니다.")
            return

        selected_group = st.selectbox("삭제할 그룹을 선택하세요:", groups, format_func=lambda x: x[1])

        if st.button("그룹 삭제"):
            try:
                conn = self.create_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM \"group\" WHERE group_id = ? AND group_creator = ?",
                    (selected_group[0], user_id),
                )
                if cursor.rowcount == 0:
                    st.error("그룹장만 그룹을 삭제할 수 있습니다.")
                else:
                    conn.commit()
                    st.success(f"'{selected_group[1]}' 그룹이 삭제되었습니다!")
            except sqlite3.Error as e:
                st.error(f"DB 오류: {e}")
            finally:
                conn.close()

    # 그룹 탈퇴 및 양도
    def manage_group_members_page(self):
        st.header("그룹 탈퇴 및 양도")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT g.group_id, g.group_name
                FROM "group" g
                JOIN group_member gm ON g.group_id = gm.group_id
                WHERE gm.user_id = ?
                """,
                (user_id,),
            )
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("참여 중인 그룹이 없습니다.")
            return

        selected_group = st.selectbox("탈퇴하려는 그룹을 선택하세요:", groups, format_func=lambda x: x[1])

        # 그룹장인지 확인
        is_creator = False
        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT group_creator FROM "group"
                WHERE group_id = ?
                """,
                (selected_group[0],),
            )
            creator = cursor.fetchone()
            if creator and creator[0] == user_id:
                is_creator = True
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if is_creator:
            st.info("현재 그룹장입니다. 그룹장을 다른 사용자에게 양도하거나 그룹 탈퇴가 불가능합니다.")
            conn = self.create_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT user_id FROM group_member
                    WHERE group_id = ? AND role = 'member'
                    """,
                    (selected_group[0],),
                )
                members = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error as e:
                st.error(f"DB 오류: {e}")
                return
            finally:
                conn.close()

            if not members:
                st.warning("양도 가능한 그룹원이 없습니다.")
                return

            new_leader = st.selectbox("새로운 그룹장을 선택하세요:", members)

            if st.button("그룹장 양도 및 탈퇴"):
                conn = self.create_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE group_member
                        SET role = 'admin'
                        WHERE group_id = ? AND user_id = ?
                        """,
                        (selected_group[0], new_leader),
                    )
                    cursor.execute(
                        """
                        DELETE FROM group_member
                        WHERE group_id = ? AND user_id = ?
                        """,
                        (selected_group[0], user_id),
                    )
                    cursor.execute(
                        """
                        UPDATE "group"
                        SET group_creator = ?
                        WHERE group_id = ?
                        """,
                        (new_leader, selected_group[0]),
                    )
                    conn.commit()
                    st.success(f"'{selected_group[1]}' 그룹장을 '{new_leader}'에게 양도하고 탈퇴하였습니다.")
                except sqlite3.Error as e:
                    st.error(f"DB 오류: {e}")
                finally:
                    conn.close()
        else:
            if st.button("그룹 탈퇴"):
                conn = self.create_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        DELETE FROM group_member
                        WHERE group_id = ? AND user_id = ?
                        """,
                        (selected_group[0], user_id),
                    )
                    if cursor.rowcount > 0:
                        conn.commit()
                        st.success(f"'{selected_group[1]}' 그룹에서 성공적으로 탈퇴하였습니다.")
                    else:
                        st.error("탈퇴에 실패하였습니다.")
                except sqlite3.Error as e:
                    st.error(f"DB 오류: {e}")
                finally:
                    conn.close()

        # 그룹원 내보내기

    def remove_group_member_page(self):
        st.header("그룹원 내보내기")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT group_id, group_name FROM "group"
                WHERE group_creator = ?
            """,
                (user_id,),
            )
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("관리 가능한 그룹이 없습니다.")
            return

        selected_group = st.selectbox("그룹을 선택하세요:", groups, format_func=lambda x: x[1])

        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id FROM group_member
                WHERE group_id = ? AND role = 'member'
            """,
                (selected_group[0],),
            )
            members = [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not members:
            st.warning("해당 그룹에 내보낼 그룹원이 없습니다.")
            return

        selected_member = st.selectbox("내보낼 그룹원을 선택하세요:", members)

        if st.button("그룹원 내보내기"):
            conn = self.create_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM group_member
                    WHERE group_id = ? AND user_id = ?
                """,
                    (selected_group[0], selected_member),
                )
                if cursor.rowcount > 0:
                    conn.commit()
                    st.success(f"'{selected_member}'님을 그룹에서 내보냈습니다.")
                else:
                    st.error("그룹원 내보내기에 실패하였습니다.")
            except sqlite3.Error as e:
                st.error(f"DB 오류: {e}")
            finally:
                conn.close()

    # 초대 기능
    def group_invitation_page(self):
        st.header("그룹 초대")
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error("로그인이 필요합니다.")
            return

        conn = self.create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT group_id, group_name FROM "group"
                WHERE group_creator = ?
            """,
                (user_id,),
            )
            groups = cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return
        finally:
            conn.close()

        if not groups:
            st.warning("초대 가능한 그룹이 없습니다.")
            return

        selected_group = st.selectbox("초대할 그룹을 선택하세요:", groups, format_func=lambda x: x[1])
        invitee_id = st.text_input("초대할 사용자 ID를 입력하세요")

        if st.button("초대 요청"):
            conn = self.create_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO group_member (group_id, user_id, role)
                    VALUES (?, ?, 'member')
                """,
                    (selected_group[0], invitee_id),
                )
                conn.commit()
                st.success(f"'{invitee_id}'님에게 초대 요청을 보냈습니다.")
            except sqlite3.IntegrityError:
                st.warning("해당 사용자는 이미 그룹의 멤버입니다.")
            except sqlite3.Error as e:
                st.error(f"DB 오류: {e}")
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

def search_groups_page():
    """그룹 검색 페이지"""
    st.header("그룹 검색 및 참여")

    # 검색 기준 선택
    search_criteria = st.selectbox(
        "검색 기준을 선택하세요",
        ["시간대", "이름", "날짜", "카테고리"],
        index=0
    )

    user_input = None

    if search_criteria == "시간대":
        user_input = st.time_input("시간대를 선택하세요")
    elif search_criteria == "이름":
        user_input = st.text_input("그룹 이름을 입력하세요")
    elif search_criteria == "날짜":
        user_input = st.date_input("약속 날짜를 선택하세요")
    elif search_criteria == "카테고리":
        dao = CategoryDAO()
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
            if search_criteria == "시간대":
                query = """
                    SELECT g.group_name, g.group_creator, g.meeting_date, g.meeting_time, c.category, l.location_name, COUNT(gm.user_id) as current_members
                    FROM "group" g
                    LEFT JOIN food_categories c ON g.category = c.category_id
                    LEFT JOIN locations l ON g.location = l.location_id
                    LEFT JOIN group_member gm ON g.group_id = gm.group_id
                    WHERE g.meeting_time = ?
                    GROUP BY g.group_id
                """
                params = (user_input.strftime("%H:%M:%S"),)

            elif search_criteria == "이름":
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
            st.error(f"DB 오류: {e}")
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
                if st.button(f"그룹 참여", key=f"join_{group_name}"):
                    join_group(group_name)


def main():
    # Sidebar 메뉴
    st.sidebar.title("그룹 관리 메뉴")
    page = st.sidebar.radio(
        "페이지를 선택하세요:",
        [
            "내가 속한 그룹",
            "장소 검색 및 저장",
            "그룹 생성",
            "그룹 수정",
            "그룹 삭제",
            "그룹 탈퇴 및 양도",
            "그룹원 내보내기",
            "그룹 초대",
            "검색",
        ],
    )

    # GroupAndLocationApp 초기화
    kakao_api_key = "393132b4dfde1b54fc18b3bacc06eb3f"  # 실제 API 키로 대체
    app = GroupAndLocationApp(db_name="zip.db", kakao_api_key="6c1cbbc51f7ba2ed462ab5b62d3a3746")

    # 페이지별 메서드 호출
    if page == "내가 속한 그룹":
        app.my_groups_page()
    elif page == "장소 검색 및 저장":
        app.location_page()
    elif page == "그룹 생성":
        app.group_creation_page()
    elif page == "그룹 수정":
        app.group_update_page()
    elif page == "그룹 삭제":
        app.group_delete_page()
    elif page == "그룹 탈퇴 및 양도":
        app.manage_group_members_page()
    elif page == "그룹원 내보내기":
        app.remove_group_member_page()
    elif page == "그룹 초대":
        app.group_invitation_page()
    elif page == "검색":
        search_groups_page()




if __name__ == "__main__":
    main()


