import os
import sys
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(APP_DIR), 'src'))

from recommender import MovieRecommender

st.set_page_config(page_title="Toàn bộ phim", layout="wide")


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()

if st.button("Quay lại"):
    st.switch_page("main.py")

st.title("Toàn bộ phim")

df = rec.movies.copy()

available_cols = {
    'title': 'Tên phim',
    'release_year': 'Năm phát hành',
    'genres_display': 'Thể loại',
    'vote_average': 'Đánh giá (/10)',
    'weighted_rating': 'Đánh giá hiệu chỉnh',
    'vote_count': 'Số lượt đánh giá',
    'popularity': 'Độ phổ biến',
}
cols_to_use = [c for c in available_cols if c in df.columns]

df = df.dropna(subset=['release_year'])
df['release_year'] = df['release_year'].astype(int)

for numeric_col in ['vote_average', 'weighted_rating', 'popularity']:
    if numeric_col in df.columns:
        df[numeric_col] = df[numeric_col].round(2)

df = df[cols_to_use].rename(columns=available_cols)
df = df.sort_values('Tên phim')

search = st.text_input("Lọc theo tên phim (tùy chọn)", "")
if search:
    df = df[df['Tên phim'].str.contains(search, case=False, na=False)]

genre_options = sorted({g.strip() for genres in rec.movies['genres_display'].dropna()
                         for g in genres.split(',') if g.strip()})
selected_genres = st.multiselect("Lọc theo thể loại (tùy chọn)", genre_options)
if selected_genres:
    pattern = '|'.join(selected_genres)
    df = df[df['Thể loại'].str.contains(pattern, case=False, na=False)]

st.write(f"Tổng số: {len(df)} phim")
st.dataframe(df, use_container_width=True, hide_index=True, height=600)