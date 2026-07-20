# Roadmap — Movie Recommender System

Trạng thái hiện tại: **Đã hoàn thành Giai đoạn 1–6 / 8**

## Tổng quan các giai đoạn

| # | Giai đoạn | Trạng thái | Nội dung chính |
|---|---|---|---|
| 1 | Data Cleaning | ✅ Hoàn thành | Đọc, merge, xử lý thiếu/trùng, parse JSON, chuẩn hóa chuỗi |
| 2 | EDA | ✅ Hoàn thành | Phân bố dữ liệu, sparsity, ngưỡng lọc cho CF |
| 3 | Feature Engineering | ✅ Hoàn thành | Metadata soup, vector hóa, weighted rating, ma trận User-Item |
| 4 | Modeling | ✅ Hoàn thành | Content-Based, Collaborative Filtering, Hybrid |
| 5 | Evaluation | ✅ Hoàn thành | RMSE/MAE, Precision@K/Recall@K, Coverage, so sánh vectorizer |
| 6 | SQLite & lưu hành vi người dùng | ✅ Hoàn thành | Schema, `db_utils.py`, ràng buộc Like/Dislike |
| 7 | Ứng dụng Streamlit | ⏳ Tiếp theo | Giao diện, thẻ phim, kết nối logic gợi ý |
| 8 | Hoàn thiện | ⬜ Chưa bắt đầu | Biểu đồ (tương lai), README báo cáo |

Chi tiết từng đầu việc: xem `docs/checklist.md`.
Chi tiết dữ liệu và các quyết định kỹ thuật: xem `docs/dataset.md`.

---

## Giai đoạn 6 — SQLite (đã hoàn thành)

- Schema: `users`, `watched`, `liked`, `disliked` (`src/db/schema.sql`)
- Module `src/db/db_utils.py`: Play/Like/Dislike + các hàm đọc lịch sử, ràng buộc Like↔Dislike loại trừ lẫn nhau
- Phát hiện & sửa 2 lỗi: đường dẫn tương đối sai khi chạy `.py` (khác notebook), sắp xếp "gần đây nhất" sai do độ phân giải timestamp

Chi tiết đầy đủ: xem mục 12 trong `docs/dataset.md`.

## Việc cần mang sang Giai đoạn 7 (quan trọng)

- Dùng **CF v2 (mean-centered)** thay vì bản v1 gốc
- Dùng **TF-IDF** (không dùng CountVectorizer) cho Content-Based/Hybrid
- Hàm Hybrid nhận `liked_tmdb_ids` từ `db_utils.get_liked_ids()` thay vì `user_item_matrix`
- Dùng `get_excluded_movie_ids()` để loại phim đã tương tác khỏi các mục gợi ý mới
- Mọi module `.py` trong `src/` dùng `os.path.dirname(os.path.abspath(__file__))` để xác định đường dẫn, không dùng `../` tương đối

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
