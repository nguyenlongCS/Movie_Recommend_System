import os
import sys
import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
sys.path.append(os.path.join(PROJECT_ROOT, 'src', 'db'))

from recommender import MovieRecommender
from db_utils import (mark_watched, like_movie, dislike_movie,
                       get_liked_ids, get_disliked_ids, get_latest_liked_id,
                       get_excluded_movie_ids)
from components.movie_card import CARD_CSS, render_movie_card_with_actions

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)

APP_USER_ID = 1


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()

# ---------- Tiêu đề + nút Lịch sử ----------
col_title, col_history = st.columns([5, 1])
with col_title:
    st.title("🎬 Movie Recommender System")
with col_history:
    st.write("")
    if st.button("🗂️ Lịch sử của tôi"):
        st.switch_page("pages/my_history.py")

# ---------- Thanh tìm kiếm ----------
search_query = st.text_input("🔍 Tìm kiếm phim", "")

if search_query:
    matches = rec.movies[rec.movies['title'].str.contains(search_query, case=False, na=False)]
    matches = matches.sort_values('weighted_rating', ascending=False).head(10)
    st.subheader(f"Kết quả tìm kiếm: '{search_query}'")
    if matches.empty:
        st.info("Không tìm thấy phim phù hợp.")
    else:
        cols = st.columns(5)
        for i, (_, row) in enumerate(matches.iterrows()):
            with cols[i % 5]:
                render_movie_card_with_actions(
                    row, key_prefix="search",
                    on_play=lambda mid: (mark_watched(APP_USER_ID, mid), st.rerun()),
                    on_like=lambda mid: (like_movie(APP_USER_ID, mid), st.rerun()),
                    on_dislike=lambda mid: (dislike_movie(APP_USER_ID, mid), st.rerun()),
                )
    st.divider()

# ---------- Dữ liệu hành vi hiện tại ----------
excluded_ids = get_excluded_movie_ids(APP_USER_ID)
liked_ids = get_liked_ids(APP_USER_ID)
latest_liked = get_latest_liked_id(APP_USER_ID)


def render_section(title, df, method="", reason_fn=None, metrics_fn=None, n_cols=5):
    if df is None or df.empty:
        return
    st.subheader(title)
    cols = st.columns(n_cols)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % n_cols]:
            reason = reason_fn(row) if reason_fn else ""
            metrics = metrics_fn(row) if metrics_fn else None
            render_movie_card_with_actions(
                row, method=method, metrics=metrics, reason=reason,
                key_prefix=title.replace(" ", "_"),
                on_play=lambda mid: (mark_watched(APP_USER_ID, mid), st.rerun()),
                on_like=lambda mid: (like_movie(APP_USER_ID, mid), st.rerun()),
                on_dislike=lambda mid: (dislike_movie(APP_USER_ID, mid), st.rerun()),
            )
    st.divider()


# ---------- 1. Phim dành riêng cho bạn (Hybrid) ----------
hybrid_df = rec.get_hybrid_recommendations(APP_USER_ID, liked_tmdb_ids=liked_ids, top_n=5, exclude_ids=excluded_ids)
alpha, beta = hybrid_df.attrs.get('alpha', 0), hybrid_df.attrs.get('beta', 0)
render_section(
    "🎯 Phim dành riêng cho bạn", hybrid_df,
    method=f"Hybrid (α={alpha:.2f}·Content-Based + β={beta:.2f}·Collaborative)",
    reason_fn=lambda r: f"Điểm tổng hợp: {r['hybrid_score']:.2f}",
    metrics_fn=lambda r: {"CB": f"{r['cb_score']:.2f}", "CF": f"{r['cf_score']:.2f}"},
)

# ---------- 2. Danh sách phim (10 phim) ----------
top_df = rec.get_top_movies(top_n=10, exclude_ids=excluded_ids)
render_section(
    "📋 Danh sách phim", top_df,
    method="Weighted Rating (công thức IMDb)",
    reason_fn=lambda r: f"Đánh giá: {r['weighted_rating']:.2f}",
    n_cols=5,
)
if st.button("Xem toàn bộ phim"):
    st.switch_page("pages/all_movies.py")

# ---------- 3. Vì bạn thích ... ----------
if latest_liked is not None:
    liked_title_series = rec.movies[rec.movies['id'] == latest_liked]['title']
    liked_title = liked_title_series.iloc[0] if len(liked_title_series) > 0 else ""
    similar_df = rec.get_similar_movies(latest_liked, top_n=5, exclude_ids=excluded_ids)
    render_section(
        f"💡 Vì bạn thích: {liked_title}", similar_df,
        method="Content-Based Filtering (TF-IDF + Cosine Similarity)",
        reason_fn=lambda r: f"Độ giống {liked_title}: {r['similarity_score']:.2f}",
    )

# ---------- 4. Dựa trên phim bạn đã thích ----------
if len(liked_ids) > 0:
    based_on_liked_df = rec.get_similar_to_liked_list(liked_ids, top_n=5, exclude_ids=excluded_ids)
    render_section(
        "❤️ Dựa trên phim bạn đã thích", based_on_liked_df,
        method="Content-Based Filtering (TF-IDF, trung bình toàn bộ danh sách đã thích)",
        reason_fn=lambda r: f"Độ phù hợp: {r['similarity_score']:.2f}",
    )

# ---------- 5. Người giống bạn đang xem (CF) ----------
cf_df = rec.get_cf_recommendations(APP_USER_ID, top_n=5, exclude_ids=excluded_ids)
render_section(
    "👥 Người giống bạn đang xem", cf_df,
    method="Collaborative Filtering (User-based KNN, mean-centered)",
    reason_fn=lambda r: f"Điểm dự đoán: {r['cf_score']:.1f}/5.0",
)

# ---------- 6. Có thể bạn sẽ bất ngờ ----------
surprise_df = rec.get_surprise_me(top_n=5, exclude_ids=excluded_ids)
render_section(
    "🎲 Có thể bạn sẽ bất ngờ", surprise_df,
    method="Ngẫu nhiên có chọn lọc (top phim theo Weighted Rating)",
    reason_fn=lambda r: f"Đánh giá: {r['weighted_rating']:.2f}",
)