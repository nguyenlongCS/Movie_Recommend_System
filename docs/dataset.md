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

## 8. Kết quả Modeling (Giai đoạn 4)

### 4.1. Content-Based Filtering
Tính cosine similarity **on-demand** (1 phim với toàn bộ tập, không lưu ma trận đầy đủ 45429×45429 — sẽ tốn ~16GB RAM).

**Lỗi phát hiện & khắc phục:** phim có `soup` cực ngắn (chỉ 5-6 từ, VD chỉ có 1 genre + tên diễn viên hiếm gặp) và `vote_count ≈ 0` bị TF-IDF cosine similarity thổi phồng điểm giả tạo (do chuẩn hóa vector ngắn khiến trọng số từ chung bị phóng đại). Khắc phục bằng cách giới hạn **candidate pool** — chỉ đề xuất trong số phim có `vote_count ≥ 10` (còn 22,915/45,429 phim đủ điều kiện).

Kiểm định định tính sau khi sửa: *The Godfather* → đúng phần 2, phần 3 + phim mafia khác; *La La Land* → đúng phim nhạc jazz + phim đầu tay của cùng đạo diễn (Guy and Madeline on a Park Bench). *Toy Story* chấp nhận được. *Inception* là giới hạn đã biết của bag-of-words (không bắt được ngữ nghĩa trừu tượng như "giấc mơ lồng nhau") — chấp nhận cho phạm vi project đơn giản.

Thời gian: ~0.046s/lần.

### 4.2. Collaborative Filtering
User-based CF dùng `NearestNeighbors` (cosine similarity) trên ma trận User-Item đã lọc (671 user × 3,493 phim từ Bước 3).

Kiểm định định tính trên 4 user cho kết quả rất nhất quán theo cụm gu xem phim — VD user 300 nhận toàn LOTR (3 phần) + Empire Strikes Back + Sixth Sense (cụm sci-fi/fantasy rõ rệt), xác nhận thuật toán bắt đúng pattern hành vi.

Xử lý đúng cold-start (user không có trong ma trận → trả về rỗng kèm cảnh báo).

**Lưu ý kỹ thuật:** `cf_score` không map trực tiếp thang rating gốc 0.5–5.0, do công thức trung bình có trọng số tính trên toàn bộ k-neighbor kể cả neighbor chưa rate phim đó (đóng góp 0). Điểm này chỉ dùng để **xếp hạng nội bộ** (top-N vẫn chính xác), không nên hiển thị trực tiếp cho người dùng như "điểm dự đoán".

Thời gian: ~0.068s/lần.

### 4.3. Hybrid
Công thức: `hybrid_score = α·CB_norm + β·CF_norm` (CB và CF được chuẩn hóa min-max về [0,1] trước khi cộng, vì thang giá trị gốc khác nhau hoàn toàn).

Trọng số động theo lượng dữ liệu user: `α = max(0.2, 1 - n_ratings/50)`, `β = 1 - α`. Đã kiểm định α/β thay đổi đúng công thức (user 20 rating → α=0.6; user 100 rating → α=0.2 chạm sàn).

Kết quả pha trộn có ý nghĩa thực sự — không chỉ đơn thuần "copy" CF khi β lớn: khi α đủ cao, CB điều chỉnh thứ hạng theo nội dung phim (VD user 1 với α=0.6, Pulp Fiction chen vào top-5 nhờ tín hiệu nội dung mạnh).

**Ghi chú thiết kế quan trọng cho Giai đoạn 7:** hàm hiện tại lấy "phim đã thích" từ `user_item_matrix` (rating ≥ 4 trong MovieLens) — chỉ phù hợp để **kiểm định thuật toán**. Trong ứng dụng thực tế, cần sửa hàm để nhận `liked_tmdb_ids` từ bảng `liked` trong SQLite làm tham số, vì user thật của app sẽ không nằm trong tập MovieLens có sẵn.

Xử lý đúng cold-start hoàn toàn (không có CF lẫn phim đã thích). Thời gian: ~0.083s/lần.

### Artifact đã lưu thêm ở Giai đoạn 4
| File | Nội dung |
|---|---|
| `content_based_candidate_indices.pkl` | Danh sách index các phim đủ điều kiện làm candidate (vote_count≥10) |
| `title_indices.pkl` | Index tra cứu nhanh vị trí phim theo title |
| `user_knn_model.pkl` | Mô hình KNN đã fit trên ma trận User-Item |
| `movies_id_to_pos.pkl` | Map nhanh từ `tmdbId` sang vị trí dòng trong `movies_features.csv` |

## 10. Kết quả Evaluation (Giai đoạn 5)

### Tách train/test
80/20 theo từng user (72,279 train / 17,736 test), toàn bộ 671 user có mặt trong test.

### RMSE/MAE — Rating Prediction (Collaborative Filtering)

| Phương pháp | RMSE | MAE |
|---|---|---|
| Baseline: global mean | 1.0390 | 0.8374 |
| Baseline: user mean | 0.9543 | 0.7443 |
| CF v1 (rating thô, không mean-centering) | 1.0474 ❌ (thua cả baseline) | 0.8027 |
| **CF v2 (mean-centered)** | **0.9818** | **0.7455** |

**Phát hiện quan trọng:** CF v1 (trung bình có trọng số trên rating thô) thua cả baseline "đoán bằng trung bình của chính user" — nguyên nhân do không tách được "tông chấm điểm" riêng của từng user. Khắc phục bằng **mean-centering** (dự đoán = trung bình user + độ lệch có trọng số từ neighbor), cải thiện rõ rệt nhưng vẫn xấp xỉ baseline user-mean.

**Kết luận trung thực:** đây là giới hạn đã biết của User-based KNN cơ bản trên dataset nhỏ, thưa (sparsity 98.36%) — phù hợp với ghi nhận trong tài liệu học thuật, không phải lỗi triển khai. Không đầu tư thêm kỹ thuật phức tạp hơn (shrinkage, regularization) vì ngoài phạm vi project "đơn giản, không phức tạp". **Chốt dùng CF v2** làm phiên bản chính thức.

### Precision@5 / Recall@5 — Top-N Recommendation Quality

| Phương pháp | Precision@5 | Recall@5 |
|---|---|---|
| Baseline (popularity, không cá nhân hóa) | 0.0482 | 0.0227 |
| Content-Based (TF-IDF) | 0.0280 | 0.0146 |
| Collaborative Filtering | 0.2224 | 0.1254 |
| **Hybrid** | **0.2341** | **0.1261** |

**Phát hiện & sửa lỗi quan trọng:** lần đánh giá CB đầu tiên cho kết quả rất thấp (0.0065) — nguyên nhân là so sánh không công bằng: CB dùng candidate pool 22,915 phim trong khi CF chỉ hoạt động trên 3,493 phim (tập phim có rating), khiến "đáp án đúng" bị pha loãng cho CB. Sau khi giới hạn candidate pool CB về đúng phạm vi 3,459 phim giao với CF, kết quả tăng lên 0.0280 — hợp lý và có thể so sánh công bằng.

**Kết luận:** 
- **Hybrid vượt cả CF thuần lẫn CB thuần** — xác nhận định lượng giá trị của việc kết hợp 2 phương pháp (không chỉ là lý thuyết).
- CB có precision thấp hơn nhiều so với CF vì không tận dụng được tín hiệu hành vi tập thể — đây là **đặc điểm bản chất**, phù hợp cho mục đích khác (gợi ý "giống phim đã thích", không phải tối đa hóa độ chính xác dự đoán hành vi).

### Coverage@5 (đo trên mẫu 200 user)

| Phương pháp | Coverage@5 |
|---|---|
| **Content-Based** | **0.1223** (đa dạng nhất) |
| Hybrid | 0.0752 |
| Collaborative Filtering | 0.0671 (thấp nhất — "popularity bias") |

CF có độ phủ catalog thấp nhất — hiện tượng **popularity bias** đã biết trong hệ gợi ý (CF thiên về đề xuất lặp lại nhóm phim trung tâm mạng lưới, được nhiều user rate). CB đa dạng hơn nhờ dựa vào đặc trưng nội dung riêng từng phim.

➡️ **Ý nghĩa cho thiết kế UI:** CF/Hybrid phù hợp cho các mục cần độ chính xác cao (*"Phim dành riêng cho bạn"*, *"Người giống bạn đang xem"*); CB phù hợp cho mục cần khám phá đa dạng (*"Có thể bạn sẽ bất ngờ"*, *"Vì bạn thích..."*) — đúng tinh thần thiết kế 6 mục gợi ý ban đầu.

### So sánh CountVectorizer vs TF-IDF (giải quyết việc treo từ Bước 3)

| Vectorizer | Precision@5 |
|---|---|
| CountVectorizer | 0.0108 |
| **TF-IDF** | **0.0280** (gấp 2.6 lần) |

**Chốt dùng TF-IDF** làm vectorizer chính thức cho Content-Based/Hybrid. `count_matrix.pkl`/`count_vectorizer.pkl` vẫn giữ lại trong `models_artifacts/` nhưng không dùng trong pipeline chính thức.

## 12. Thiết kế SQLite (Giai đoạn 6)

### Quyết định thiết kế
- **1 user mặc định** (`user_id=1`), không xây đăng nhập — đúng tinh thần đơn giản. Schema vẫn tổng quát (có bảng `users`) để mở rộng sau nếu cần.
- **Không lưu trùng metadata phim vào SQLite** — chỉ tham chiếu `movie_id` (=`id`/tmdbId), metadata đọc từ `movies_features.csv` qua pandas.
- **Like và Dislike loại trừ lẫn nhau**: Like 1 phim đang Dislike sẽ tự động gỡ khỏi Dislike, và ngược lại. `Watched` độc lập.
- **`UNIQUE(user_id, movie_id)`** trên cả 3 bảng hành vi, dùng `INSERT OR REPLACE` để chống trùng lặp khi bấm nút nhiều lần.

### Schema (`src/db/schema.sql`)
4 bảng: `users`, `watched`, `liked`, `disliked` (cấu trúc giống nhau: `id` tự tăng, `user_id`, `movie_id`, timestamp), có index theo `user_id`.

### Module `src/db/db_utils.py`
| Hàm | Vai trò |
|---|---|
| `mark_watched(user_id, movie_id)` | Nút Play |
| `like_movie(user_id, movie_id)` | Nút Like (tự gỡ khỏi Dislike nếu có) |
| `dislike_movie(user_id, movie_id)` | Nút Dislike (tự gỡ khỏi Liked nếu có) |
| `get_watched_ids`, `get_liked_ids`, `get_disliked_ids` | Đọc từng danh sách |
| `get_latest_liked_id` | Phim thích gần nhất — seed cho mục "Vì bạn thích ..." |
| `get_excluded_movie_ids` | Gộp cả 3 danh sách — loại khỏi các mục gợi ý khác |

### Lỗi phát hiện & khắc phục
1. **Đường dẫn tương đối sai vị trí khi chạy file `.py`** (khác notebook — notebook luôn chạy từ `notebooks/`, còn file `.py` có thể chạy từ bất kỳ thư mục nào tùy người dùng `cd`). Khắc phục: dùng `os.path.dirname(os.path.abspath(__file__))` để xác định `PROJECT_ROOT` ổn định, áp dụng cho mọi module trong `src/` từ nay.
2. **`ORDER BY liked_at DESC` không đáng tin cậy** khi nhiều thao tác diễn ra trong cùng 1 giây (độ phân giải `CURRENT_TIMESTAMP` của SQLite chỉ tới cấp giây). Khắc phục: dùng `ORDER BY id DESC` (autoincrement luôn tăng, không phụ thuộc độ phân giải thời gian).

### Kiểm định
Đã test đầy đủ: ghi đúng 3 loại hành vi, ràng buộc loại trừ Like↔Dislike hoạt động chính xác, không nhân đôi khi bấm lại nút cũ, thứ tự "gần đây nhất" chính xác sau khi sửa lỗi.

## 13. Việc còn lại trước khi vào App (Giai đoạn 7)

- Cập nhật lại hàm CF dùng **mean-centering (v2)** thay vì bản v1 ban đầu (đã ghi chú từ Giai đoạn 5)
- Sửa hàm Hybrid để nhận `liked_tmdb_ids` từ `db_utils.get_liked_ids()` thay vì tự suy ra từ `user_item_matrix` (đã ghi chú từ Giai đoạn 4.3)
- Dùng TF-IDF (không dùng CountVectorizer) cho Content-Based/Hybrid
- Xây dựng ứng dụng Streamlit, kết nối logic gợi ý cho 6 mục, dùng `get_excluded_movie_ids` để lọc phim đã tương tác khỏi gợi ý mới
