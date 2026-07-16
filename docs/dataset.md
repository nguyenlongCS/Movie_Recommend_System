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

## 5. Việc còn lại trước khi vào Feature Engineering (EDA)

- Phân tích phân bố dữ liệu (genres, rating, năm phát hành...)
- Phân tích độ thưa ma trận user-item để quyết định ngưỡng lọc cho Collaborative Filtering
