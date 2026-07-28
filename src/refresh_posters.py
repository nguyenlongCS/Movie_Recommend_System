import os
import time
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MOVIES_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'movies_features.csv')

API_KEY = os.environ.get('TMDB_API_KEY')
if not API_KEY:
    raise ValueError("Chưa đặt biến môi trường TMDB_API_KEY")

movies = pd.read_csv(MOVIES_PATH)

# --- Chọn phạm vi refresh: mở rộng từ 200 lên 1000 phim theo weighted_rating ---
TOP_N = 1000
top_ids = movies.sort_values('weighted_rating', ascending=False).head(TOP_N)['id'].tolist()

demo_titles = ['The Godfather', 'Inception', 'Toy Story', 'La La Land',
               'The Dark Knight', 'The Lord of the Rings: The Fellowship of the Ring',
               'The Shawshank Redemption', 'Pulp Fiction', "Schindler's List"]
demo_ids = movies[movies['title'].isin(demo_titles)]['id'].tolist()

target_ids = list(set(top_ids) | set(demo_ids))
print(f"Số phim sẽ refresh poster: {len(target_ids)}")
print("Lưu ý: bao gồm cả các phim đã refresh ở lần chạy trước (top 200) — gọi lại không sao, chỉ tốn thêm vài chục request.")

# --- Gọi API tuần tự, có nghỉ giữa các request để tránh vượt rate limit ---
updated = {}
failed = []

for i, movie_id in enumerate(target_ids):
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}"
    try:
        resp = requests.get(url, params={"api_key": API_KEY}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            new_poster = data.get("poster_path")
            if new_poster:
                updated[movie_id] = new_poster
            else:
                failed.append((movie_id, "không có poster trên TMDb"))
        else:
            failed.append((movie_id, f"status {resp.status_code}"))
    except Exception as e:
        failed.append((movie_id, str(e)))

    if (i + 1) % 50 == 0:
        print(f"Đã xử lý {i+1}/{len(target_ids)}...")
    time.sleep(0.05)  # nghỉ nhẹ giữa các request, tránh bị TMDb giới hạn tốc độ

print(f"\nCập nhật thành công: {len(updated)}")
print(f"Thất bại: {len(failed)}")
if failed[:5]:
    print("Vài ví dụ thất bại:", failed[:5])

# --- Ghi đè poster_path mới vào movies_features.csv ---
for movie_id, new_poster in updated.items():
    movies.loc[movies['id'] == movie_id, 'poster_path'] = new_poster

movies.to_csv(MOVIES_PATH, index=False)
print("\nĐã lưu movies_features.csv với poster_path đã cập nhật")

file_size_mb = os.path.getsize(MOVIES_PATH) / (1024 * 1024)
print(f"Kích thước file sau khi lưu: {file_size_mb:.2f} MB")