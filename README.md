# 🎬 Movie Recommender System (Refactor)

Hệ thống gợi ý phim đơn giản, tập trung vào quy trình **Data Mining** (Data Cleaning → EDA → Feature Engineering → Modeling → Evaluation), kết hợp 3 phương pháp gợi ý: **Content-Based Filtering**, **Collaborative Filtering**, và **Hybrid**.

## Trạng thái hiện tại

✅ Data Cleaning · ✅ EDA · ✅ Feature Engineering · ✅ Modeling · ✅ Evaluation · ✅ SQLite · ✅ Streamlit App · ⏳ Hoàn thiện (tiếp theo)

Xem chi tiết tiến độ tại [`docs/checklist.md`](docs/checklist.md) và kế hoạch tổng thể tại [`docs/roadmap.md`](docs/roadmap.md).

## Tính năng chính

- **Phim dành riêng cho bạn** — gợi ý bằng mô hình Hybrid
- **Danh sách phim** — hiển thị 10 phim, có nút Toàn bộ phim (có bộ lọc theo thể loại)
- **Vì bạn thích ...** — gợi ý phim tương tự một phim đã thích (Content-Based)
- **Dựa trên phim bạn đã thích** — gợi ý từ toàn bộ danh sách phim đã thích
- **Người giống bạn đang xem** — gợi ý bằng Collaborative Filtering
- **Có thể bạn sẽ bất ngờ** — gợi ý ngẫu nhiên có chọn lọc (dựa trên Weighted Rating)
- Mỗi thẻ phim hiện **thanh điểm đánh giá** (theo %) và mục **"Chi tiết kỹ thuật"** riêng (phương pháp, công thức, điểm từng thành phần) — đúng trọng tâm Data Mining của project
- Trang **"Lịch sử của tôi"**: 3 tab Phim đã xem / Đã thích / Hạn chế, có thể xóa lịch sử theo từng loại

## Dataset

[The Movies Dataset (Kaggle)](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset) — chi tiết cấu trúc, các vấn đề dữ liệu và cách xử lý tại [`docs/dataset.md`](docs/dataset.md).

## Công nghệ sử dụng

Python, Streamlit, pandas, numpy, scikit-learn, CSV, SQLite

## Bắt đầu nhanh

Xem hướng dẫn cài đặt và chạy chi tiết tại [`docs/setup.md`](docs/setup.md).

```bash
pip install pandas numpy scikit-learn nltk streamlit
```

Đặt dataset vào `data/raw/`, sau đó chạy lần lượt các notebook trong `notebooks/` theo đúng thứ tự đánh số. Sau khi có đủ artifact (`models_artifacts/`) và database (`database/app.db`), chạy ứng dụng từ thư mục gốc:

```bash
streamlit run app/main.py
```

## Cấu trúc project

```
movie-recommender/
├── data/{raw,interim,processed}/
├── notebooks/              # 01_data_cleaning → 07_evaluation
├── notebooks_export/       # export từ (.ipynb) sang HTML, PDF,...
├── src/                    # Code module hoá
│   ├── db/                 # schema.sql, db_utils.py (SQLite)
│   ├── recommender.py      # Class MovieRecommender (CB/CF/Hybrid hợp nhất)
│   ├── add_overview.py     # Bổ sung cột overview vào movies_features.csv
│   └── refresh_posters.py  # Refresh poster_path có chọn lọc qua TMDb API
├── app/                    # Ứng dụng Streamlit
│   ├── main.py              # Trang chính
│   ├── pages/                # Trang phụ (Toàn bộ phim, Lịch sử của tôi)
│   └── components/           # movie_card.py
├── models_artifacts/       # Model/vectorizer đã lưu (.pkl)
├── database/               # SQLite (app.db)
├── reports/figures/        # Biểu đồ (chưa phát triển)
└── docs/                   # checklist.md · dataset.md · roadmap.md · setup.md
```

## Tài liệu

| File | Nội dung |
|---|---|
| [`docs/checklist.md`](docs/checklist.md) | Việc đã/chưa làm, cập nhật theo từng bước |
| [`docs/dataset.md`](docs/dataset.md) | Mô tả dataset, các vấn đề dữ liệu, kết quả EDA, Feature Engineering, Modeling, Evaluation, SQLite & App |
| [`docs/roadmap.md`](docs/roadmap.md) | Kế hoạch thực hiện theo từng giai đoạn |
| [`docs/setup.md`](docs/setup.md) | Hướng dẫn cài đặt, thứ tự chạy notebook, lưu ý kỹ thuật |
