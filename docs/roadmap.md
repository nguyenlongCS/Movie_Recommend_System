# Roadmap — Movie Recommender System

Trạng thái hiện tại: **Đã hoàn thành Giai đoạn 1–3 / 8**

## Tổng quan các giai đoạn

| # | Giai đoạn | Trạng thái | Nội dung chính |
|---|---|---|---|
| 1 | Data Cleaning | ✅ Hoàn thành | Đọc, merge, xử lý thiếu/trùng, parse JSON, chuẩn hóa chuỗi |
| 2 | EDA | ✅ Hoàn thành | Phân bố dữ liệu, sparsity, ngưỡng lọc cho CF |
| 3 | Feature Engineering | ✅ Hoàn thành | Metadata soup, vector hóa, weighted rating, ma trận User-Item |
| 4 | Modeling | ⏳ Tiếp theo | Content-Based, Collaborative Filtering, Hybrid |
| 5 | Evaluation | ⬜ Chưa bắt đầu | Precision@K, Recall@K, RMSE/MAE, so sánh phương pháp |
| 6 | SQLite & lưu hành vi người dùng | ⬜ Chưa bắt đầu | Schema, logic Play/Like/Dislike |
| 7 | Ứng dụng Streamlit | ⬜ Chưa bắt đầu | Giao diện, thẻ phim, kết nối logic gợi ý |
| 8 | Hoàn thiện | ⬜ Chưa bắt đầu | Biểu đồ (tương lai), README báo cáo |

Chi tiết từng đầu việc: xem `docs/checklist.md`.
Chi tiết dữ liệu và các quyết định kỹ thuật: xem `docs/dataset.md`.

---

## Giai đoạn 4 — Modeling (kế hoạch chi tiết, sắp thực hiện)

### 4.1. Content-Based Filtering
- Tính cosine similarity trên ma trận TF-IDF (và/hoặc CountVectorizer) đã lưu ở `models_artifacts/`
- Xây hàm gợi ý: nhập 1 phim → trả về top-N phim tương tự nhất
- Phục vụ mục **"Vì bạn thích ..."**

### 4.2. Collaborative Filtering
- Dùng ma trận User-Item đã lọc (`user_item_matrix.pkl`)
- Áp dụng Item-based KNN (`sklearn.neighbors.NearestNeighbors`) hoặc giảm chiều bằng `TruncatedSVD`
- Xây hàm gợi ý: nhập userId → trả về top-N phim được user tương tự đánh giá cao
- Phục vụ mục **"Người giống bạn đang xem"**

### 4.3. Hybrid
- Công thức: `score = α * CB_score + β * CF_score`
- `α`, `β` điều chỉnh theo lượng dữ liệu user đã có (user mới/ít dữ liệu → nghiêng về CB nhiều hơn)
- Phục vụ mục **"Phim dành riêng cho bạn"**

### 4.4. Lưu model
- Lưu toàn bộ artifact vào `models_artifacts/` (`.pkl`) để ứng dụng Streamlit dùng lại, không train lại mỗi lần chạy

---

## Giai đoạn 5 — Evaluation (kế hoạch)
- Tách train/test hợp lý trên `ratings_clean.csv`
- Tính RMSE/MAE cho Collaborative Filtering
- Tính Precision@K, Recall@K cho cả 3 phương pháp
- So sánh CountVectorizer vs TF-IDF (quyết định treo lại từ Bước 3)
- Tính Coverage, Diversity (đánh giá thêm cho mục "Có thể bạn sẽ bất ngờ")

## Giai đoạn 6 — SQLite (kế hoạch)
- Schema: `users`, `movies`, `watched`, `liked`, `disliked`
- Play → insert `watched`; Like → insert `liked`; Dislike → insert `disliked`
- Mỗi mục gợi ý trong UI truy vấn đúng bảng tương ứng (VD: "Dựa trên phim bạn đã thích" đọc từ `liked`)

## Giai đoạn 7 — Streamlit App (kế hoạch)
- Thanh tìm kiếm + 6 mục gợi ý (chỉ hiển thị khi có dữ liệu)
- Thẻ phim: poster (TMDb), hover hiển thị tên/thể loại/điểm/lý do gợi ý, nút Play/Like/Dislike
- Kết nối SQLite để lưu và đọc lịch sử người dùng theo thời gian thực

## Giai đoạn 8 — Hoàn thiện (kế hoạch, chưa ưu tiên)
- Biểu đồ trực quan (thống kê cá nhân, thể loại yêu thích...)
- README báo cáo tổng hợp toàn bộ pipeline Data Mining
