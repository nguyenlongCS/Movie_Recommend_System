# Dataset — The Movies Dataset (Kaggle)

Nguồn: https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset

## 1. Các file gốc sử dụng (`data/raw/`)

| File | Shape gốc | Vai trò |
|---|---|---|
| `movies_metadata.csv` | (45,466, 24) | Thông tin phim: title, overview, genres, popularity, vote... |
| `credits.csv` | (45,476, 3) | Diễn viên (`cast`) và đoàn làm phim (`crew`), map theo `id` |
| `keywords.csv` | (46,419, 2) | Từ khóa mô tả phim, map theo `id` |
| `links_small.csv` | (9,125, 3) | Map `movieId` (MovieLens) ↔ `tmdbId` — dùng để lấy poster |
| `ratings_small.csv` | (100,004, 4) | Rating của user, dùng cho Collaborative Filtering (bản nhẹ) |
| `links.csv` | — | Bản đầy đủ của `links_small.csv`, **chưa dùng** ở giai đoạn dev |
| `ratings.csv` | — | Bản đầy đủ của `ratings_small.csv` (~26 triệu dòng, 692MB), **chưa dùng** ở giai đoạn dev — chỉ cân nhắc dùng khi train CF ở giai đoạn cuối |

> Quy ước: trong suốt quá trình code/test, luôn dùng `ratings_small.csv` + `links_small.csv` để đảm bảo nhẹ và nhanh. Chỉ chuyển sang bản đầy đủ nếu cần cải thiện chất lượng CF ở giai đoạn cuối.

## 2. Các cột gốc quan trọng trong `movies_metadata.csv`

| Cột | Kiểu gốc | Ghi chú |
|---|---|---|
| `id` | str (lẫn lỗi) | Định danh phim — dùng để merge. 3 dòng bị lỗi parse (giá trị là ngày tháng) |
| `title` | str | Tên phim |
| `overview` | str | Mô tả nội dung — dùng cho Content-Based |
| `genres` | str (JSON-string) | Dạng `[{'id': 16, 'name': 'Animation'}, ...]` |
| `popularity` | str (cần ép kiểu) | Độ phổ biến — có lỗi định dạng lẫn trong dữ liệu gốc |
| `vote_average`, `vote_count` | float64 | Điểm đánh giá trung bình và số lượt đánh giá |
| `release_date` | str (cần ép kiểu) | Ngày phát hành |
| `poster_path` | str | Đường dẫn poster (dùng ghép với TMDb image base URL) |
| `budget`, `revenue` | str/float (có lỗi định dạng) | Chưa dùng ở giai đoạn hiện tại |

`credits.csv` có `cast`, `crew` dạng JSON-string. `keywords.csv` có `keywords` dạng JSON-string.

## 3. Các vấn đề dữ liệu đã phát hiện & cách xử lý

| Vấn đề | Số lượng | Cách xử lý |
|---|---|---|
| `id` không phải số trong `movies` | 3 dòng | Loại bỏ trước khi ép kiểu `int64` |
| `id` trùng lặp trong `movies` | 30 dòng | `drop_duplicates(subset='id')` |
| `id` trùng lặp trong `credits` | 44 dòng | `drop_duplicates(subset='id')` |
| `id` trùng lặp trong `keywords` | 987 dòng | `drop_duplicates(subset='id')` |
| Dòng trùng lặp toàn phần (`movies`) | 17 dòng | `drop_duplicates()` |
| `title` trùng lặp | 3,188 dòng | **Không xử lý** — hợp lệ (phim remake/cùng tên khác nhau) |
| `overview` thiếu | 954 dòng | Điền chuỗi rỗng, giữ dòng |
| `title` thiếu | 6 dòng | Loại dòng |
| `cast`/`crew`/`keywords` thiếu sau merge | 1 dòng | Loại dòng |
| `release_date` thiếu | 84 dòng | Giữ nguyên (chấp nhận NaT) |
| `poster_path` thiếu | 383 dòng | Giữ nguyên, xử lý ảnh mặc định ở UI sau |
| `popularity` sai định dạng số | — | `pd.to_numeric(errors='coerce')` — 0 lỗi phát sinh |
| `genres`/`keywords`/`cast` rỗng sau parse | 2,441 / 14,340 / 2,414 | Không phải lỗi — bản thân TMDb thiếu dữ liệu ở các phim đó, giữ nguyên (list rỗng) |
| `director` rỗng sau parse | 887 | Giữ nguyên (chuỗi rỗng) |

## 4. Kết quả sau Data Cleaning

### `data/processed/movies_clean.csv` — (45,429 dòng × 21 cột)

Các cột chính:
- `id`, `title`, `overview`, `popularity`, `vote_average`, `vote_count`, `release_date`, `release_year`, `poster_path`
- `genres_list`, `keywords_list`, `cast_list`, `director` (dạng đã parse, chưa chuẩn hóa chuỗi)
- `genres_clean`, `keywords_clean`, `cast_clean`, `director_clean` (đã lowercase, nối liền tên riêng — VD: `"tomhanks"`)

### `data/processed/ratings_clean.csv` — (100,004 dòng × 4 cột)

Cột: `userId`, `movieId`, `rating`, `timestamp`. Không có dòng trùng lặp.

> Lưu ý: `ratings_clean.csv` dùng `movieId` (MovieLens ID), khác với `id` (TMDb ID) trong `movies_clean.csv`. Cần dùng `links_small.csv` (`movieId ↔ tmdbId`) để map hai bảng này với nhau ở các bước sau (Collaborative Filtering, Hybrid).

## 5. Kết quả EDA (Bước 2)

### Phân bố rating
`mean = 3.54`, `median = 4.0`, thang điểm 0.5–5.0 — người dùng có xu hướng đánh giá cao hơn là thấp (lệch phải).

### Phân bố thể loại (top 5)
Drama (20,243) > Comedy (13,176) > Thriller (7,618) > Romance (6,730) > Action (6,590).

### Năm phát hành
`min = 1874`, `max = 2020`, `mean ≈ 1992`. Các phim rất cũ (< 1900) là phim thử nghiệm có thật thời kỳ đầu điện ảnh (Edison, Lumière...) — **không phải lỗi dữ liệu**, giữ nguyên.

### Độ thưa ma trận User-Item (`ratings_small`)
- Số user: 671 (mỗi user ≥ 20 rating — đúng thiết kế MovieLens-small)
- Số phim có rating: 9,066 (nhưng median chỉ 3 rating/phim, 25% chỉ có 1 rating)
- **Sparsity: 98.36%** — hiện tượng long-tail điển hình

### Mapping giữa CF (ratings) và CB (movies)
Qua `links_small` (`movieId ↔ tmdbId`): **99.81%** rating map được sang `movies_clean` (chỉ 71/100,004 rating không khớp). Content-Based và Collaborative Filtering dùng chung được gần như toàn bộ tập phim.

### Ngưỡng lọc đã chọn cho Collaborative Filtering
**≥ 5 rating/phim** → giữ lại 3,496 phim (38.6%). Lý do: loại bỏ phần lớn phim có 1-2 rating (similarity không đáng tin cậy) trong khi vẫn giữ đủ độ đa dạng để tránh cold-start quá nặng.

### Quyết định về công thức đánh giá phim
`vote_count` phân bố lệch mạnh (median=10, percentile 99%=2,184) → **không dùng `vote_average` thô** để xếp hạng phim ở mục "Có thể bạn sẽ bất ngờ", mà dùng **weighted rating kiểu IMDb**:

```
WR = (v / (v+m)) * R + (m / (v+m)) * C
```
- `v`: vote_count của phim
- `m`: ngưỡng vote_count tối thiểu (đề xuất lấy percentile 75% ≈ 34)
- `R`: vote_average của phim
- `C`: vote_average trung bình toàn bộ dataset

## 7. Kết quả Feature Engineering (Bước 3)

### Lỗi phát sinh & cách khắc phục
Khi đọc lại `movies_clean.csv`, các ô `director_clean` từng được điền chuỗi rỗng (`''`) bị pandas đọc thành `NaN` (kiểu `float`), gây lỗi khi nối chuỗi (`TypeError: expected str instance, float found`). Khắc phục bằng `fillna('')` ngay sau khi đọc lại CSV cho mọi cột từng chứa chuỗi rỗng.

### Metadata soup
Ghép `genres_clean + keywords_clean + cast_clean + director_clean×2 + overview` thành 1 chuỗi văn bản cho mỗi phim (trọng số đạo diễn nhân đôi). Độ dài trung bình 64 từ/phim; **25 phim (0.05%)** có soup hoàn toàn rỗng (thiếu toàn bộ metadata) — chấp nhận được, số lượng không đáng kể.

### Vector hóa
Cả `CountVectorizer` và `TfidfVectorizer` (`max_features=5000`, `stop_words='english'`) đều cho ma trận `(45429, 5000)`. Sẽ so sánh chất lượng giữa hai phương án ở bước Evaluation, chưa chọn phương án cuối cùng.

### Weighted Rating (IMDb-style)
`C = 5.618` (vote_average trung bình), `m = 34` (percentile 75% của vote_count). Top phim theo weighted rating cho kết quả hợp lý (Shawshank Redemption, The Godfather, The Dark Knight, Fight Club, Pulp Fiction, Schindler's List...) — xác nhận công thức hoạt động đúng, tránh được thiên lệch do phim ít vote nhưng điểm ảo cao.

### Ma trận User-Item (cho Collaborative Filtering)
Sau khi map `ratings.movieId → tmdbId` (qua `links_small`) và lọc theo ngưỡng ≥5 rating/phim:
- Ratings trước lọc: 99,933 (đã loại 71 dòng không map được `tmdbId`)
- Ratings sau lọc: 90,015
- Số phim: 3,493 | Số user: 671
- Shape ma trận: `(671, 3493)`

### Artifact đã lưu (dùng lại cho Modeling — không cần tính lại)
| File | Vị trí | Nội dung |
|---|---|---|
| `movies_features.csv` | `data/processed/` | id, title, soup, weighted_rating, vote_average, vote_count, popularity, release_year, poster_path |
| `tfidf_vectorizer.pkl`, `tfidf_matrix.pkl` | `models_artifacts/` | Vectorizer và ma trận TF-IDF |
| `count_vectorizer.pkl`, `count_matrix.pkl` | `models_artifacts/` | Vectorizer và ma trận CountVectorizer |
| `user_item_matrix.pkl` | `models_artifacts/` | Ma trận User-Item cho CF |

## 8. Việc còn lại trước khi vào Modeling

- Modeling: Content-Based (cosine similarity), Collaborative Filtering (KNN/SVD), Hybrid
- Evaluation: so sánh CountVectorizer vs TF-IDF, Precision@K, Recall@K, RMSE/MAE
