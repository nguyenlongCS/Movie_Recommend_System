import os
import sys
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
sys.path.append(os.path.join(PROJECT_ROOT, 'src', 'db'))

from recommender import MovieRecommender
from db_utils import (get_watched_ids, get_liked_ids, get_disliked_ids,
                       mark_watched, like_movie, dislike_movie)
from components.movie_card import CARD_CSS, render_movie_card_with_actions

st.set_page_config(page_title="Lịch sử của tôi", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)

APP_USER_ID = 1


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()

if st.button("← Quay lại"):
    st.switch_page("main.py")

st.title("🗂️ Lịch sử của tôi")


def render_movie_list(title, movie_ids, empty_msg, key_prefix):
    st.subheader(f"{title} ({len(movie_ids)})")
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
            render_movie_card_with_actions(
                row, key_prefix=key_prefix,
                primary_score=row['weighted_rating'] / 10, primary_label="Đánh giá",
                on_play=lambda mid: (mark_watched(APP_USER_ID, mid), st.rerun()),
                on_like=lambda mid: (like_movie(APP_USER_ID, mid), st.rerun()),
                on_dislike=lambda mid: (dislike_movie(APP_USER_ID, mid), st.rerun()),
            )
    st.divider()


tab1, tab2, tab3 = st.tabs(["▶ Đã xem", "👍 Đã thích", "👎 Đã hạn chế"])

with tab1:
    render_movie_list("Phim đã xem", get_watched_ids(APP_USER_ID),
                       "Bạn chưa đánh dấu phim nào là đã xem.", "hist_watched")

with tab2:
    render_movie_list("Phim đã thích", get_liked_ids(APP_USER_ID),
                       "Bạn chưa thích phim nào.", "hist_liked")

with tab3:
    render_movie_list("Phim hạn chế", get_disliked_ids(APP_USER_ID),
                       "Bạn chưa hạn chế phim nào.", "hist_disliked")