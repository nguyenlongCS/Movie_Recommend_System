import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')

movies_clean = pd.read_csv(os.path.join(DATA_DIR, 'movies_clean.csv'))
movies_clean['overview'] = movies_clean['overview'].fillna('')

movies_features = pd.read_csv(os.path.join(DATA_DIR, 'movies_features.csv'))

# Nếu đã lỡ có cột overview từ lần chạy trước, loại bỏ trước khi merge lại để tránh cột trùng (overview_x/overview_y)
if 'overview' in movies_features.columns:
    movies_features = movies_features.drop(columns=['overview'])

movies_features = movies_features.merge(movies_clean[['id', 'overview']], on='id', how='left')
movies_features['overview'] = movies_features['overview'].fillna('')

movies_features.to_csv(os.path.join(DATA_DIR, 'movies_features.csv'), index=False)
print("Đã bổ sung cột overview, số dòng có nội dung:", (movies_features['overview'].str.strip() != '').sum())