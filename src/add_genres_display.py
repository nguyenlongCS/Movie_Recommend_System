import os
import ast
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

movies_clean = pd.read_csv(os.path.join(DATA_DIR, 'movies_clean.csv'))
movies_clean['genres_list'] = movies_clean['genres_list'].apply(ast.literal_eval)
movies_clean['genres_display'] = movies_clean['genres_list'].apply(lambda lst: ', '.join(lst[:3]))

movies_features = pd.read_csv(os.path.join(DATA_DIR, 'movies_features.csv'))
movies_features = movies_features.merge(movies_clean[['id', 'genres_display']], on='id', how='left')
movies_features['genres_display'] = movies_features['genres_display'].fillna('')
movies_features.to_csv(os.path.join(DATA_DIR, 'movies_features.csv'), index=False)
print("Đã bổ sung cột genres_display")  