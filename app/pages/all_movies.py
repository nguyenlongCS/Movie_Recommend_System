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

if st.button("← Quay lại"):
    st.switch_page("main.py")

st.title("📋 Toàn bộ phim")

df = rec.movies[['title', 'release_year']].dropna(subset=['release_year']).copy()
df['release_year'] = df['release_year'].astype(int)
df = df.sort_values('title').rename(columns={'title': 'Tên phim', 'release_year': 'Năm phát hành'})

search = st.text_input("Lọc theo tên phim (tùy chọn)", "")
if search:
    df = df[df['Tên phim'].str.contains(search, case=False, na=False)]

st.write(f"Tổng số: {len(df)} phim")
st.dataframe(df, use_container_width=True, hide_index=True, height=600)