import os
import sys
import sqlite3
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
sys.path.append(os.path.join(PROJECT_ROOT, 'src', 'db'))

from recommender import MovieRecommender
from db_utils import get_watched_ids, get_liked_ids, get_disliked_ids, DB_PATH

from components.movie_card import CARD_CSS, render_movie_card

st.set_page_config(page_title="Lịch sử của tôi", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)

APP_USER_ID = 1


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()


def clear_history(table_name):
    """Xóa toàn bộ lịch sử của 1 bảng (watched/liked/disliked) cho user hiện tại."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (APP_USER_ID,))
    conn.commit()
    conn.close()


if st.button("Quay lại"):
    st.switch_page("main.py")

st.title("Lịch sử của tôi")


def render_movie_list(title, movie_ids, empty_msg, table_name):
    col_title, col_clear = st.columns([5, 1])
    with col_title:
        st.subheader(f"{title} ({len(movie_ids)})")
    with col_clear:
        st.write("")
        if movie_ids and st.button("Xóa lịch sử", key=f"clear_{table_name}", use_container_width=True):
            clear_history(table_name)
            st.rerun()

    if not movie_ids:
        st.info(empty_msg)
        st.divider()
        return

    df = rec.movies[rec.movies['id'].isin(movie_ids)]
    # Giữ đúng thứ tự "gần đây nhất" theo movie_ids (đã sắp xếp sẵn từ db_utils)
    df = df.set_index('id').reindex(movie_ids).reset_index()

    n_cols = 5
    cols = st.columns(n_cols)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % n_cols]:
            render_movie_card(row, primary_score=row.get('vote_average', 0) / 10, primary_label="Đánh giá")
    st.divider()


tab1, tab2, tab3 = st.tabs(["Đã xem", "Đã thích", "Đã hạn chế"])

with tab1:
    render_movie_list("Phim đã xem", get_watched_ids(APP_USER_ID),
                       "Bạn chưa đánh dấu phim nào là đã xem.", "watched")

with tab2:
    render_movie_list("Phim đã thích", get_liked_ids(APP_USER_ID),
                       "Bạn chưa thích phim nào.", "liked")

with tab3:
    render_movie_list("Phim hạn chế", get_disliked_ids(APP_USER_ID),
                       "Bạn chưa hạn chế phim nào.", "disliked")