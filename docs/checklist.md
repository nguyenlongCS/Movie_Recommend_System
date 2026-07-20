# Checklist — Movie Recommender System

Cập nhật lần cuối: sau khi hoàn tất **Giai đoạn 6 — SQLite & lưu hành vi người dùng**

---

## Giai đoạn 1 — Chuẩn bị dữ liệu

- [x] Thu thập & khảo sát dataset (Kaggle: The Movies Dataset)
- [x] Đọc 5 file: `movies_metadata.csv`, `credits.csv`, `keywords.csv`, `links_small.csv`, `ratings_small.csv`
- [x] Kiểm tra `id` không hợp lệ trong `movies` → phát hiện 3 dòng, đã loại bỏ
- [x] Kiểm tra & loại bỏ `id` trùng lặp (`movies`: 30, `credits`: 44, `keywords`: 987)
- [x] Kiểm tra & loại bỏ dòng trùng lặp toàn phần (17 dòng)
- [x] Merge `movies + credits + keywords` theo `id` (kiểu `left`)
- [x] Thống kê đầy đủ giá trị thiếu theo từng cột (`isnull().sum()`)
- [x] Xử lý thiếu theo từng cột (không `dropna()` toàn bộ):
  - `title` thiếu → loại dòng (6 dòng)
  - `cast`/`crew`/`keywords` thiếu sau merge → loại dòng (1 dòng)
  - `overview` thiếu → điền chuỗi rỗng, giữ dòng (954 dòng)
  - `release_date`, `poster_path` thiếu → giữ nguyên, chấp nhận thiếu
- [x] Chọn các cột cần thiết, loại cột không dùng (`homepage`, `tagline`, `belongs_to_collection`...)
- [x] Parse cột JSON-string (`ast.literal_eval`):
  - `genres` → `genres_list`
  - `keywords` → `keywords_list`
  - `cast` → `cast_list` (top 3 diễn viên)
  - `crew` → `director` (lọc `job == 'Director'`)
- [x] Ép kiểu dữ liệu số: `popularity` → `float64` (0 lỗi phát sinh)
- [x] Ép kiểu ngày tháng: `release_date` → `datetime64`, tách `release_year`
- [x] Chuẩn hóa chuỗi: bỏ khoảng trắng thừa, nối tên riêng liền nhau, chuyển chữ thường
  (`genres_clean`, `keywords_clean`, `cast_clean`, `director_clean`)
- [x] Xử lý `ratings_small`: kiểm tra trùng lặp (0 dòng trùng)
- [x] Lưu kết quả:
  - `data/interim/movies_merged_basic.csv`
  - `data/processed/movies_clean.csv` (45,429 dòng × 21 cột)
  - `data/processed/ratings_clean.csv` (100,004 dòng × 4 cột)

## Giai đoạn 2 — EDA

- [x] Phân bố rating (`ratings_clean`) — mean 3.54, median 4.0, lệch phải
- [x] Phân bố thể loại phim — Drama, Comedy, Thriller dẫn đầu
- [x] Phân bố số phim theo năm — min 1874 (phim thử nghiệm có thật, không phải lỗi)
- [x] Phân bố `popularity`, `vote_average`, `vote_count` — `vote_count` lệch mạnh (long-tail)
- [x] Phân tích độ thưa (sparsity) của ma trận user-item — **98.36%**
- [x] Phân bố số rating/user (min 20, mean 149), số rating/phim (median chỉ 3)
- [x] Kiểm tra mapping `ratings.movieId` ↔ `movies.id` qua `links_small` — khớp 99.81%
- [x] Xác định ngưỡng lọc cho CF: **≥ 5 rating/phim** (giữ 3,496 phim, 38.6%)
- [x] Kết luận: dùng weighted rating (IMDb-style) thay vì `vote_average` thô cho mục ngẫu nhiên có chọn lọc

## Giai đoạn 3 — Feature Engineering

- [x] Xử lý lỗi đọc lại CSV: `fillna('')` cho `director_clean`, `overview` (chuỗi rỗng bị đọc thành NaN)
- [x] Tạo "metadata soup" (genres + keywords + cast + director×2 + overview)
- [x] Kiểm tra độ dài soup — mean 64 từ, 25 phim (0.05%) có soup rỗng (chấp nhận được)
- [x] Vector hóa: CountVectorizer và TF-IDF (max_features=5000, stop_words='english') — cả hai matrix (45429, 5000)
- [x] Tính Weighted Rating (IMDb-style), C=5.618, m=34 (percentile 75% vote_count)
  - Top 10 kiểm định hợp lý: Shawshank Redemption, Godfather, Dark Knight, Fight Club, Pulp Fiction...
- [x] Xây ma trận User-Item cho CF (lọc ≥5 rating/phim): 90,015 ratings, 3,493 phim, 671 user
- [x] Lưu artifact cho Modeling:
  - `data/processed/movies_features.csv`
  - `models_artifacts/tfidf_vectorizer.pkl`, `tfidf_matrix.pkl`
  - `models_artifacts/count_vectorizer.pkl`, `count_matrix.pkl`
  - `models_artifacts/user_item_matrix.pkl`
- [ ] *(Chưa làm, để dành đánh giá ở Bước Evaluation)* So sánh chất lượng CountVectorizer vs TF-IDF
- [ ] *(Chưa làm, tùy chọn)* Thử nghiệm Stemming (PorterStemmer) — có thể bổ sung nếu Evaluation cho thấy cần cải thiện

## Giai đoạn 4 — Modeling

### 4.1. Content-Based Filtering
- [x] Tính cosine similarity on-demand (không lưu ma trận đầy đủ 45429×45429 — tốn ~16GB RAM)
- [x] Phát hiện & sửa lỗi nghiêm trọng: phim có soup cực ngắn (vote_count≈0) bị TF-IDF thổi phồng similarity giả tạo
  → Khắc phục: giới hạn candidate pool theo `vote_count >= 10` (còn 22,915/45,429 phim đủ điều kiện được đề xuất)
- [x] Kiểm định định tính: The Godfather, La La Land cho kết quả rất tốt; Toy Story chấp nhận được;
      Inception là giới hạn đã biết của bag-of-words (không bắt được ngữ nghĩa trừu tượng)
- [x] Thời gian chạy: ~0.046s/lần — đủ nhanh cho web app
- [x] Lưu artifact: `content_based_candidate_indices.pkl`, `title_indices.pkl`

### 4.2. Collaborative Filtering
- [x] User-based CF bằng `NearestNeighbors` (cosine) trên ma trận User-Item đã lọc (671 user × 3493 phim)
- [x] Kiểm định định tính trên 4 user: kết quả nhất quán theo cụm gu xem phim (VD user 300 ra toàn LOTR + sci-fi kinh điển)
- [x] Xử lý cold-start (user không có trong ma trận) — trả về rỗng kèm cảnh báo
- [x] Ghi chú: `cf_score` không map trực tiếp thang 0.5–5.0 (bị pha loãng bởi neighbor chưa rate) — chỉ dùng để xếp hạng nội bộ, không hiển thị trực tiếp cho người dùng
- [x] Thời gian chạy: ~0.068s/lần
- [x] Lưu artifact: `user_knn_model.pkl`

### 4.3. Hybrid
- [x] Công thức: `hybrid_score = α·CB_norm + β·CF_norm`, chuẩn hóa min-max trước khi cộng
- [x] Trọng số động: `α = max(0.2, 1 - n_ratings/50)`, `β = 1-α` — user càng nhiều rating càng nghiêng về CF
- [x] Kiểm định: kết quả Hybrid thực sự pha trộn có ý nghĩa (không chỉ copy CF khi β lớn — CB vẫn điều chỉnh thứ hạng khi tín hiệu nội dung đủ mạnh, VD Empire Strikes Back được đẩy hạng nhờ cb_score cao)
- [x] Xử lý cold-start hoàn toàn (không có CF lẫn phim đã thích) — trả về rỗng kèm cảnh báo
- [x] Thời gian chạy: ~0.083s/lần

## Giai đoạn 5 — Evaluation

- [x] Tách train/test theo từng user (80/20), xử lý lỗi `groupby().apply()` bằng cách tiếp cận vector hóa
- [x] Dựng lại `train_matrix` + fit lại KNN chỉ trên train (tránh rò rỉ dữ liệu test)
- [x] Xây hàm dự đoán rating riêng cho RMSE/MAE (khác hàm xếp hạng top-N ở Giai đoạn 4)
- [x] Tính RMSE/MAE cho CF — phát hiện v1 (rating thô) thua cả baseline user-mean
  → Sửa thành **CF v2 (mean-centered)**, cải thiện rõ rệt: RMSE 1.0474→0.9818, MAE 0.8027→0.7455
  → **Chốt dùng CF v2 làm phiên bản chính thức** (cần cập nhật lại hàm ở Giai đoạn 4.2/4.3 khi triển khai app)
- [x] Precision@5 / Recall@5 cho CB, CF, Hybrid + baseline (popularity)
  → Phát hiện & sửa lỗi so sánh không công bằng (CB dùng candidate pool 22,915 phim trong khi CF chỉ 3,493) → giới hạn lại candidate pool CB về giao với tập CF (3,459 phim)
  → Kết quả: CF=0.2224, **Hybrid=0.2341 (tốt nhất)**, CB=0.0280, Baseline=0.0482
- [x] Coverage@5 (200 user mẫu): CB=0.1223 (đa dạng nhất), CF=0.0671, Hybrid=0.0752
- [x] So sánh CountVectorizer vs TF-IDF: TF-IDF thắng rõ rệt (0.0280 vs 0.0108)
  → **Chốt dùng TF-IDF** làm vectorizer chính thức, không dùng CountVectorizer trong app thực tế

## Giai đoạn 6 — SQLite & lưu hành vi người dùng

- [x] Quyết định thiết kế: 1 user mặc định (không có đăng nhập), không lưu trùng metadata phim vào SQLite (chỉ tham chiếu `movie_id`), Like/Dislike loại trừ lẫn nhau, `UNIQUE(user_id, movie_id)` chống trùng lặp
- [x] Thiết kế schema (`src/db/schema.sql`): `users`, `watched`, `liked`, `disliked` + index theo `user_id`
- [x] Phát hiện & sửa lỗi đường dẫn tương đối khi chạy file `.py` (khác notebook) — chuyển sang `os.path.dirname(os.path.abspath(__file__))` để xác định `PROJECT_ROOT` ổn định bất kể chạy từ đâu
- [x] Xây `src/db/db_utils.py`: `mark_watched`, `like_movie`, `dislike_movie`, `get_watched_ids`, `get_liked_ids`, `get_disliked_ids`, `get_latest_liked_id`, `get_excluded_movie_ids`
- [x] Kiểm định đầy đủ luồng nghiệp vụ (`test_db_utils.py`):
  - Ghi Watched/Liked/Disliked đúng
  - Ràng buộc loại trừ Like↔Dislike hoạt động đúng
  - Chống trùng lặp khi bấm lại nút cũ (`INSERT OR REPLACE`)
  - Phát hiện & sửa lỗi sắp xếp "gần đây nhất": `CURRENT_TIMESTAMP` cấp giây không đủ phân giải khi thao tác nhanh → đổi sang `ORDER BY id DESC` (đáng tin cậy hơn)

## Giai đoạn 7 — Ứng dụng Streamlit

- [ ] Khung giao diện (thanh tìm kiếm + các mục gợi ý)
- [ ] Component thẻ phim (poster, hover tooltip, nút Play/Like/Dislike)
- [ ] Kết nối logic gợi ý (CB, CF, Hybrid, ngẫu nhiên có chọn lọc)
- [ ] Kết nối SQLite

## Giai đoạn 8 — Hoàn thiện

- [ ] Biểu đồ trực quan (chưa phát triển ở giai đoạn này)
- [ ] README tổng hợp báo cáo Data Mining
