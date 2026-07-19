# Roadmap — Movie Recommender System

Trạng thái hiện tại: **Đã hoàn thành Giai đoạn 1–5 / 8**

## Tổng quan các giai đoạn

| # | Giai đoạn | Trạng thái | Nội dung chính |
|---|---|---|---|
| 1 | Data Cleaning | ✅ Hoàn thành | Đọc, merge, xử lý thiếu/trùng, parse JSON, chuẩn hóa chuỗi |
| 2 | EDA | ✅ Hoàn thành | Phân bố dữ liệu, sparsity, ngưỡng lọc cho CF |
| 3 | Feature Engineering | ✅ Hoàn thành | Metadata soup, vector hóa, weighted rating, ma trận User-Item |
| 4 | Modeling | ✅ Hoàn thành | Content-Based, Collaborative Filtering, Hybrid |
| 5 | Evaluation | ✅ Hoàn thành | RMSE/MAE, Precision@K/Recall@K, Coverage, so sánh vectorizer |
| 6 | SQLite & lưu hành vi người dùng | ⏳ Tiếp theo | Schema, logic Play/Like/Dislike |
| 7 | Ứng dụng Streamlit | ⬜ Chưa bắt đầu | Giao diện, thẻ phim, kết nối logic gợi ý |
| 8 | Hoàn thiện | ⬜ Chưa bắt đầu | Biểu đồ (tương lai), README báo cáo |

Chi tiết từng đầu việc: xem `docs/checklist.md`.
Chi tiết dữ liệu và các quyết định kỹ thuật: xem `docs/dataset.md`.

---

## Giai đoạn 5 — Evaluation (đã hoàn thành)

- RMSE/MAE: phát hiện CF v1 thua baseline → sửa bằng mean-centering (CF v2), chốt dùng v2
- Precision@5/Recall@5: Hybrid (0.2341) > CF (0.2224) > Baseline (0.0482) > CB (0.0280) — xác nhận giá trị định lượng của Hybrid
- Coverage@5: CB đa dạng nhất (0.1223), CF thấp nhất do popularity bias (0.0671)
- TF-IDF thắng CountVectorizer rõ rệt (0.0280 vs 0.0108) — chốt dùng TF-IDF

Chi tiết đầy đủ: xem mục 10 trong `docs/dataset.md`.

## Việc cần mang sang Giai đoạn 6-7 (quan trọng)

- Cập nhật hàm CF dùng **mean-centering (v2)** thay vì bản v1 gốc ở Giai đoạn 4
- Sửa hàm Hybrid nhận `liked_tmdb_ids` từ SQLite (bảng `liked`) thay vì suy ra từ `user_item_matrix`
- Dùng **TF-IDF** (không dùng CountVectorizer) cho Content-Based/Hybrid trong app

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
