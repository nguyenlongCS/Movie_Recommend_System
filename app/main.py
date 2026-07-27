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
from components.movie_card import CARD_CSS, render_movie_card

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)

# Khoảng cách giữa poster và nút "Xem chi tiết"
st.markdown("<style>.stButton button { margin-top: 10px; }</style>", unsafe_allow_html=True)

APP_USER_ID = 1
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()


# ---------- Modal thông tin phim đầy đủ ----------
@st.dialog("Thông tin phim", width="large")
def show_movie_modal(movie_row, method="", formula="", reason="", metrics=None):
    poster_path = movie_row.get('poster_path')
    poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if isinstance(poster_path, str) and poster_path.strip() else None
    release_year = movie_row.get('release_year')
    runtime = movie_row.get('runtime')
    vote_average = movie_row.get('vote_average', 0)

    col_poster, col_info = st.columns([1, 2])
    with col_poster:
        # Dùng CSS background-image (giống hệt kỹ thuật ở trang chủ) thay vì thẻ <img> thật —
        # nếu link ảnh chết, chỉ hiện màu nền xám thay vì icon ảnh vỡ xấu xí của trình duyệt.
        bg_style = f"background-image: url('{poster_url}');" if poster_url else ""
        st.markdown(
            f'<div style="width:100%; aspect-ratio:2/3; border-radius:8px; '
            f'background-color:#2b2b2b; background-size:cover; background-position:center; '
            f'{bg_style}"></div>',
            unsafe_allow_html=True,
        )
            

    with col_info:
        st.subheader(movie_row.get('title', ''))

        meta_parts = []
        if release_year is not None and str(release_year) != 'nan':
            meta_parts.append(str(int(release_year)))
        if movie_row.get('genres_display'):
            meta_parts.append(movie_row['genres_display'])
        if meta_parts:
            st.caption(" • ".join(meta_parts))

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Đánh giá", f"{vote_average:.1f}/10")
        with col_b:
            if runtime is not None and str(runtime) != 'nan':
                st.metric("Thời lượng", f"{int(runtime)} phút")

        rating_pct = max(0, min(100, vote_average * 10))
        st.progress(rating_pct / 100, text=f"Điểm đánh giá: {rating_pct:.0f}%")

        st.markdown("**Nội dung**")
        overview = movie_row.get('overview', '')
        st.write(overview if isinstance(overview, str) and overview.strip() else "Không có mô tả.")

    st.divider()
    st.markdown("**Chi tiết kỹ thuật**")
    if method:
        st.caption(f"Phương pháp: {method}")
    if formula:
        st.caption(f"Công thức: {formula}")
    if reason:
        st.caption(f"Lý do gợi ý: {reason}")
    if metrics:
        for label, value in metrics.items():
            pct = max(0, min(100, value * 100))
            st.progress(pct / 100, text=f"{label}: {pct:.0f}%")
    if not (method or metrics or reason):
        st.caption("Không có thông tin kỹ thuật cho phim này.")

    st.divider()
    col1, col2, col3 = st.columns(3)
    movie_id = movie_row['id']
    with col1:
        if st.button("Play", key=f"modal_play_{movie_id}", use_container_width=True):
            mark_watched(APP_USER_ID, movie_id)
            st.toast("Tính năng phát video chỉ là mô phỏng.")
    with col2:
        if st.button("Like", key=f"modal_like_{movie_id}", use_container_width=True):
            like_movie(APP_USER_ID, movie_id)
            st.rerun()
    with col3:
        if st.button("Dislike", key=f"modal_dislike_{movie_id}", use_container_width=True):
            dislike_movie(APP_USER_ID, movie_id)
            st.rerun()


# ---------- Tiêu đề + nút Lịch sử ----------
col_title, col_history = st.columns([5, 1])
with col_title:
    st.title("Movie Recommender System")
with col_history:
    st.write("")
    if st.button("Lịch sử của tôi", use_container_width=True):
        st.switch_page("pages/my_history.py")

# ---------- Thanh tìm kiếm ----------
search_query = st.text_input("Tìm kiếm phim", "")

# ---------- Dữ liệu hành vi hiện tại ----------
excluded_ids = get_excluded_movie_ids(APP_USER_ID)
liked_ids = get_liked_ids(APP_USER_ID)
latest_liked = get_latest_liked_id(APP_USER_ID)


def render_poster_section(title, df, n_display, method="", formula="", reason_fn=None, metrics_fn=None, n_cols=5):
    """
    Chỉ hiển thị poster (khung cố định + hover tooltip có thanh điểm đánh giá)
    kèm nút 'Xem chi tiết' tách riêng bên dưới để mở modal.
    """
    if df is None or df.empty:
        return
    df = df.drop_duplicates(subset='id').head(n_display)
    if df.empty:
        return

    st.subheader(title)
    cols = st.columns(n_cols)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % n_cols]:
            render_movie_card(row, primary_score=row.get('vote_average', 0) / 10, primary_label="Đánh giá")
            if st.button("Xem chi tiết", key=f"{title}_view_{row['id']}", use_container_width=True):
                reason = reason_fn(row) if reason_fn else ""
                metrics = metrics_fn(row) if metrics_fn else None
                show_movie_modal(row, method=method, formula=formula, reason=reason, metrics=metrics)
    st.divider()


# ---------- Kết quả tìm kiếm ----------
if search_query:
    matches = rec.movies[rec.movies['title'].str.contains(search_query, case=False, na=False)]
    matches = matches.sort_values('weighted_rating', ascending=False)
    render_poster_section(f"Kết quả tìm kiếm: '{search_query}'", matches, n_display=10)

# ---------- 1. Phim dành riêng cho bạn (Hybrid) — 5 thẻ ----------
hybrid_df = rec.get_hybrid_recommendations(APP_USER_ID, liked_tmdb_ids=liked_ids, top_n=5, exclude_ids=excluded_ids)
alpha, beta = hybrid_df.attrs.get('alpha', 0), hybrid_df.attrs.get('beta', 0)
render_poster_section(
    "Phim dành riêng cho bạn", hybrid_df, n_display=5,
    method="Hybrid (kết hợp Content-Based và Collaborative Filtering)",
    formula=f"hybrid_score = {alpha:.2f}×Content-Based + {beta:.2f}×Collaborative",
    reason_fn=lambda r: f"Điểm tổng hợp: {r['hybrid_score']:.2f}",
    metrics_fn=lambda r: {"Content-Based": r['cb_score'], "Collaborative Filtering": r['cf_score']},
)

# ---------- 2. Danh sách phim — 10 thẻ ----------
top_df = rec.get_top_movies(top_n=10, exclude_ids=excluded_ids)
render_poster_section(
    "Danh sách phim", top_df, n_display=10,
    method="Weighted Rating (công thức IMDb)",
    formula="WR = (v/(v+m))×R + (m/(v+m))×C",
    reason_fn=lambda r: f"Đánh giá: {r['weighted_rating']:.2f}",
)
if st.button("Xem toàn bộ phim"):
    st.switch_page("pages/all_movies.py")

# ---------- 3. Vì bạn thích ... — 5 thẻ ----------
if latest_liked is not None:
    liked_title_series = rec.movies[rec.movies['id'] == latest_liked]['title']
    liked_title = liked_title_series.iloc[0] if len(liked_title_series) > 0 else ""
    similar_df = rec.get_similar_movies(latest_liked, top_n=5, exclude_ids=excluded_ids)
    render_poster_section(
        f"Vì bạn thích: {liked_title}", similar_df, n_display=5,
        method="Content-Based Filtering (TF-IDF + Cosine Similarity)",
        formula="similarity = cosine(TF-IDF(phim nguồn), TF-IDF(phim ứng viên))",
        reason_fn=lambda r: f"Độ giống {liked_title}: {r['similarity_score']:.2f}",
    )

# ---------- 4. Dựa trên phim bạn đã thích — 5 thẻ ----------
if len(liked_ids) > 0:
    based_on_liked_df = rec.get_similar_to_liked_list(liked_ids, top_n=5, exclude_ids=excluded_ids)
    render_poster_section(
        "Dựa trên phim bạn đã thích", based_on_liked_df, n_display=5,
        method="Content-Based Filtering (TF-IDF, trung bình similarity với toàn bộ danh sách đã thích)",
        reason_fn=lambda r: f"Độ phù hợp: {r['similarity_score']:.2f}",
    )

# ---------- 5. Người giống bạn đang xem (CF) — 5 thẻ ----------
cf_df = rec.get_cf_recommendations(APP_USER_ID, top_n=5, exclude_ids=excluded_ids)
render_poster_section(
    "Người giống bạn đang xem", cf_df, n_display=5,
    method="Collaborative Filtering (User-based KNN, cosine similarity, mean-centered)",
    formula="dự đoán = trung bình(bạn) + Σ(sim×lệch(neighbor)) / Σ(sim)",
    reason_fn=lambda r: f"Điểm dự đoán: {r['cf_score']:.1f}/5.0",
)

# ---------- 6. Có thể bạn sẽ bất ngờ — 5 thẻ ----------
# Lưu danh sách phim vào session_state để giữ NGUYÊN qua các lần rerun (VD khi bấm "Xem chi tiết")
# Tránh lỗi: sample() ngẫu nhiên lại mỗi lần rerun khiến nút vừa bấm "biến mất" trước khi modal kịp mở.
if 'surprise_movie_ids' not in st.session_state:
    surprise_seed_df = rec.get_surprise_me(top_n=5, exclude_ids=excluded_ids)
    st.session_state['surprise_movie_ids'] = surprise_seed_df['id'].tolist()

surprise_ids = st.session_state['surprise_movie_ids']
surprise_df = rec.movies[rec.movies['id'].isin(surprise_ids)].copy()
surprise_df['__order'] = surprise_df['id'].apply(lambda x: surprise_ids.index(x))
surprise_df = surprise_df.sort_values('__order').drop(columns='__order')

render_poster_section(
    "Có thể bạn sẽ bất ngờ", surprise_df, n_display=5,
    method="Ngẫu nhiên có chọn lọc (lấy mẫu ngẫu nhiên trong top phim theo Weighted Rating)",
    reason_fn=lambda r: f"Đánh giá: {r['weighted_rating']:.2f}",
)