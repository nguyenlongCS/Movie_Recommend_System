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
- `app/main.py` + `app/pages/all_movies.py` + `app/pages/my_history.py` (multipage qua `st.switch_page`) + `app/components/movie_card.py`
- Refresh poster qua TMDb API cho 197/202 phim quan trọng (dataset gốc có nhiều poster đã bị TMDb gỡ do thu thập từ 2017)
- Phát hiện & sửa 7 lỗi kỹ thuật ban đầu (đáng chú ý nhất: lỗi React #231 do thuộc tính HTML sự kiện inline xung đột với cách Streamlit render qua react-markdown), sau đó bổ sung thêm 2 lỗi phát hiện khi mở rộng tính năng (hàm backend thiếu cột dữ liệu mới)
- Kiểm thử end-to-end đầy đủ: Play/Like/Dislike, ràng buộc loại trừ, tìm kiếm, trường hợp "sạch" — tất cả đạt
- **Mở rộng sau phản hồi thực tế**: trang "Lịch sử của tôi" (3 tab, có nút xóa, chủ ý không có nút Play/Like/Dislike), tooltip thẻ phim nâng cấp (thanh điểm màu theo %, expander "Chi tiết kỹ thuật" hiện phương pháp + công thức + điểm từng thành phần), bổ sung cột `overview` cho modal chi tiết, bộ lọc thể loại ở trang "Toàn bộ phim"
- Dọn code thừa trong `recommender.py` (biến bị gán đè, comment code cũ) — đã xác nhận không đổi logic

Chi tiết đầy đủ: xem mục 14 trong `docs/dataset.md`.

---

## Giai đoạn 8 — Hoàn thiện (kế hoạch, chưa ưu tiên)
- Biểu đồ trực quan (thống kê cá nhân, thể loại yêu thích...)
- README báo cáo tổng hợp toàn bộ pipeline Data Mining
