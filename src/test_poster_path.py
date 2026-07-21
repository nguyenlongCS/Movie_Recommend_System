import pandas as pd
movies = pd.read_csv('data/processed/movies_features.csv')
missing_poster = movies['poster_path'].isna().sum()
print(f"Phim thiếu poster_path: {missing_poster} / {len(movies)} ({missing_poster/len(movies):.1%})")
print(movies['poster_path'].dropna().head(3).tolist())