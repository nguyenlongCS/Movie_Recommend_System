import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'app.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------- GHI HÀNH VI ----------

def mark_watched(user_id, movie_id):
    """Play: đánh dấu phim đã xem (giả lập, không phát video)"""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO watched (user_id, movie_id, watched_at) "
        "VALUES (?, ?, CURRENT_TIMESTAMP)",
        (user_id, movie_id)
    )
    conn.commit()
    conn.close()


def like_movie(user_id, movie_id):
    """Like: thêm vào yêu thích, đồng thời gỡ khỏi hạn chế nếu có (ràng buộc loại trừ)"""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO liked (user_id, movie_id, liked_at) "
        "VALUES (?, ?, CURRENT_TIMESTAMP)",
        (user_id, movie_id)
    )
    conn.execute("DELETE FROM disliked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    conn.commit()
    conn.close()


def dislike_movie(user_id, movie_id):
    """Dislike: thêm vào hạn chế, đồng thời gỡ khỏi yêu thích nếu có (ràng buộc loại trừ)"""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO disliked (user_id, movie_id, disliked_at) "
        "VALUES (?, ?, CURRENT_TIMESTAMP)",
        (user_id, movie_id)
    )
    conn.execute("DELETE FROM liked WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    conn.commit()
    conn.close()


# ---------- ĐỌC LỊCH SỬ ----------

def get_watched_ids(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT movie_id FROM watched WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_liked_ids(user_id, order_by_recent=True):
    conn = get_connection()
    order = "ORDER BY id DESC" if order_by_recent else ""
    rows = conn.execute(f"SELECT movie_id FROM liked WHERE user_id = ? {order}", (user_id,)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_disliked_ids(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT movie_id FROM disliked WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_latest_liked_id(user_id):
    """Lấy phim mới thích gần nhất — dùng làm seed cho mục 'Vì bạn thích ...'"""
    liked = get_liked_ids(user_id, order_by_recent=True)
    return liked[0] if liked else None

def get_excluded_movie_ids(user_id):
    """Gộp toàn bộ phim đã watched/liked/disliked — dùng để loại khỏi các mục gợi ý mới"""
    excluded = set(get_watched_ids(user_id)) | set(get_liked_ids(user_id)) | set(get_disliked_ids(user_id))
    return excluded