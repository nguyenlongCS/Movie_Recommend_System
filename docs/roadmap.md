# Roadmap — Movie Recommender System

Trạng thái hiện tại: **Đã hoàn thành Giai đoạn 1–7 / 8**

## Tổng quan các giai đoạn

| # | Giai đoạn | Trạng thái | Nội dung chính |
|---|---|---|---|
| 1 | Data Cleaning | ✅ Hoàn thành | Đọc, merge, xử lý thiếu/trùng, parse JSON, chuẩn hóa chuỗi |
| 2 | EDA | ✅ Hoàn thành | Phân bố dữ liệu, sparsity, ngưỡng lọc cho CF |
| 3 | Feature Engineering | ✅ Hoàn thành | Metadata soup, vector hóa, weighted rating, ma trận User-Item |
| 4 | Modeling | ✅ Hoàn thành | Content-Based, Collaborative Filtering, Hybrid |
| 5 | Evaluation | ✅ Hoàn thành | RMSE/MAE, Precision@K/Recall@K, Coverage, so sánh vectorizer |
| 6 | SQLite & lưu hành vi người dùng | ✅ Hoàn thành | Schema, `db_utils.py`, ràng buộc Like/Dislike |
| 7 | Ứng dụng Streamlit | ✅ Hoàn thành | `recommender.py`, thẻ phim, `main.py`, trang toàn bộ phim |
| 8 | Hoàn thiện | ⏳ Tiếp theo | Biểu đồ (tương lai), README báo cáo |

Chi tiết từng đầu việc: xem `docs/checklist.md`.
Chi tiết dữ liệu và các quyết định kỹ thuật: xem `docs/dataset.md`.

---

## Giai đoạn 7 — Ứng dụng Streamlit (đã hoàn thành)

- `src/recommender.py`: hợp nhất CB/CF/Hybrid chính thức, áp dụng đủ quyết định chốt từ Giai đoạn 5-6
- `app/main.py` + `app/pages/all_movies.py` (multipage qua `st.switch_page`) + `app/components/movie_card.py`
- Refresh poster qua TMDb API cho 197/202 phim quan trọng (dataset gốc có nhiều poster đã bị TMDb gỡ do thu thập từ 2017)
- Phát hiện & sửa 7 lỗi kỹ thuật (chi tiết mục 14 trong `docs/dataset.md`), đáng chú ý nhất: lỗi React #231 do thuộc tính HTML sự kiện inline xung đột với cách Streamlit render qua react-markdown
- Kiểm thử end-to-end đầy đủ: Play/Like/Dislike, ràng buộc loại trừ, tìm kiếm, trường hợp "sạch" — tất cả đạt

Chi tiết đầy đủ: xem mục 14 trong `docs/dataset.md`.

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
