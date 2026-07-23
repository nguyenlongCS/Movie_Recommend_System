import streamlit as st

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

CARD_CSS = """
<style>
.movie-card {
    position: relative; width: 100%; aspect-ratio: 2 / 3;
    border-radius: 8px; overflow: hidden; cursor: pointer;
    background-color: #2b2b2b; background-size: cover; background-position: center;
    display: flex; flex-direction: column; justify-content: flex-end;
}
.movie-label {
    background: rgba(0,0,0,0.75); color: white;
    padding: 6px 8px; font-size: 12px; font-weight: bold;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.movie-tooltip {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.95), rgba(0,0,0,0.2) 60%, rgba(0,0,0,0.0));
    color: white; padding: 10px 8px 8px 8px;
    display: flex; flex-direction: column; justify-content: flex-end;
    opacity: 0; transition: opacity 0.2s ease-in-out;
    font-size: 12px; pointer-events: none;
}
.movie-card:hover .movie-tooltip { opacity: 1; }
.movie-card:hover .movie-label { opacity: 0; }
.movie-tooltip .title { font-weight: bold; font-size: 13px; margin-bottom: 2px; }
.movie-tooltip .meta { font-size: 11px; opacity: 0.85; margin-bottom: 2px; }
.movie-tooltip .method { font-size: 10px; opacity: 0.7; margin-top: 4px; }
.movie-tooltip .metrics { font-size: 11px; color: #7ee787; margin-top: 2px; }
.movie-tooltip .reason { font-size: 11px; font-style: italic; color: #ffd166; margin-top: 4px; }
</style>
"""


def render_movie_card(movie_row, method="", metrics=None, reason=""):
    poster_path = movie_row.get('poster_path')
    poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if isinstance(poster_path, str) and poster_path.strip() else ""
    title = movie_row.get('title', 'Không rõ tên')
    vote = movie_row.get('vote_average', 0)
    genres = movie_row.get('genres_display', '')

    bg_style = f"background-image: url('{poster_url}');" if poster_url else ""
    method_html = f'<div class="method">📊 {method}</div>' if method else ""

    metrics_html = ""
    if metrics:
        parts = " · ".join(f"{k}: {v}" for k, v in metrics.items())
        metrics_html = f'<div class="metrics">{parts}</div>'

    reason_html = f'<div class="reason">{reason}</div>' if reason else ""

    html = (
        f'<div class="movie-card" style="{bg_style}">'
        f'<div class="movie-label">{title}</div>'
        f'<div class="movie-tooltip">'
        f'<div class="title">{title}</div>'
        f'<div class="meta">{genres}</div>'
        f'<div class="meta">⭐ {vote:.1f}/10</div>'
        f'{method_html}{metrics_html}{reason_html}'
        f'</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_movie_card_with_actions(movie_row, method="", metrics=None, reason="", key_prefix="",
                                    on_play=None, on_like=None, on_dislike=None):
    render_movie_card(movie_row, method=method, metrics=metrics, reason=reason)
    movie_id = movie_row['id']
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶", key=f"{key_prefix}_play_{movie_id}", help="Đánh dấu đã xem"):
            if on_play: on_play(movie_id)
    with col2:
        if st.button("👍", key=f"{key_prefix}_like_{movie_id}", help="Thích"):
            if on_like: on_like(movie_id)
    with col3:
        if st.button("👎", key=f"{key_prefix}_dislike_{movie_id}", help="Không thích"):
            if on_dislike: on_dislike(movie_id)