# Checklist — Movie Recommender System

Cập nhật lần cuối: sau khi hoàn tất **Bước 1 — Data Cleaning**

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

- [ ] Content-Based: cosine similarity trên TF-IDF/CountVectorizer matrix
- [ ] Collaborative Filtering: Item-based KNN hoặc TruncatedSVD
- [ ] Hybrid: công thức kết hợp có trọng số (α*CB + β*CF)
- [ ] Lưu model/artifact (`.pkl`) vào `models_artifacts/`

## Giai đoạn 5 — Evaluation

- [ ] Tách train/test
- [ ] Tính RMSE/MAE (CF)
- [ ] Tính Precision@K, Recall@K (CB, CF, Hybrid)
- [ ] Tính Coverage, Diversity
- [ ] So sánh và kết luận phương pháp phù hợp cho từng mục gợi ý

## Giai đoạn 6 — SQLite & lưu hành vi người dùng

- [ ] Thiết kế schema (`users`, `movies`, `watched`, `liked`, `disliked`)
- [ ] Logic cập nhật: Play → `watched`, Like → `liked`, Dislike → `disliked`
- [ ] Logic truy vấn phục vụ từng mục gợi ý

## Giai đoạn 7 — Ứng dụng Streamlit

- [ ] Khung giao diện (thanh tìm kiếm + các mục gợi ý)
- [ ] Component thẻ phim (poster, hover tooltip, nút Play/Like/Dislike)
- [ ] Kết nối logic gợi ý (CB, CF, Hybrid, ngẫu nhiên có chọn lọc)
- [ ] Kết nối SQLite

## Giai đoạn 8 — Hoàn thiện

- [ ] Biểu đồ trực quan (chưa phát triển ở giai đoạn này)
- [ ] README tổng hợp báo cáo Data Mining
