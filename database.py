import pymysql
import os
from datetime import datetime



# MySQL 연결 설정
def create_connection():
    connection = pymysql.connect(
        host='localhost',
        user='zip',
        password='12zipzip34',
        database='zip',
        charset='utf8mb4'
    )
    return connection

# 글 등록 함수
def create_post(title, content, image_path=None, file_path=None):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO posts (title, content, image_path, file_path)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (title, content, image_path, file_path))
            connection.commit()
    except Exception as e:
        print(f"Error creating post: {e}")
    finally:
        connection.close()

# 글 수정 함수
def update_post(post_id, title, content, image_path=None, file_path=None):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                UPDATE posts SET title = %s, content = %s, image_path = %s, file_path = %s, updated_at = %s
                WHERE post_id = %s
            """
            cursor.execute(query, (title, content, image_path, file_path, datetime.now(), post_id))
            connection.commit()
    except Exception as e:
        print(f"Error updating post: {e}")
    finally:
        connection.close()

# 글 삭제 함수
def delete_post(post_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM posts WHERE post_id = %s"
            cursor.execute(query, (post_id,))
            connection.commit()
    except Exception as e:
        print(f"Error deleting post: {e}")
    finally:
        connection.close()

# 글 조회 함수
def get_posts():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM posts ORDER BY created_at DESC"
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []
    finally:
        connection.close()

# 특정 글 조회 함수
def get_post(post_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM posts WHERE post_id = %s"
            cursor.execute(query, (post_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching post: {e}")
        return None
    finally:
        connection.close()
