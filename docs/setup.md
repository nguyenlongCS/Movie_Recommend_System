# Setup — Hướng dẫn cài đặt & chạy project

## 1. Yêu cầu môi trường
- Python 3.10+ (đã test trên Python 3.12)
- pip

## 2. Cài đặt thư viện

```bash
pip install pandas numpy scikit-learn nltk streamlit
```

## 3. Cấu trúc thư mục

```
movie-recommender/
├── data/
│   ├── raw/            # File CSV gốc từ Kaggle (KHÔNG chỉnh sửa)
│   ├── interim/         # Dữ liệu trung gian trong quá trình xử lý
│   └── processed/       # Dữ liệu sạch, sẵn sàng dùng cho modeling
├── notebooks/            # Notebook phát triển từng bước
├── notebooks_export/      # Export notebook (.ipynb) sang HTML/PDF...
├── src/                   # Code chính thức (module hoá, dùng sau khi ổn định từ notebook)
├── app/                   # Ứng dụng Streamlit
├── models_artifacts/      # Model/vectorizer/ma trận đã lưu (.pkl)
├── database/              # File SQLite
├── reports/figures/       # Biểu đồ (chưa phát triển)
└── docs/                  # Tài liệu project (file này nằm ở đây)
```

## 4. Chuẩn bị dữ liệu

Tải dataset từ Kaggle: https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset

Đặt các file sau vào `data/raw/`:
```
movies_metadata.csv
credits.csv
keywords.csv
links.csv
links_small.csv
ratings.csv
ratings_small.csv
```

> Trong giai đoạn phát triển, chỉ dùng `links_small.csv` và `ratings_small.csv` (nhẹ, nhanh). Bản đầy đủ (`links.csv`, `ratings.csv`) chỉ cân nhắc dùng ở giai đoạn cuối nếu cần cải thiện chất lượng Collaborative Filtering.

## 5. Thứ tự chạy notebook

Chạy tuần tự theo đúng thứ tự (mỗi notebook đọc output đã lưu của notebook trước):

| # | Notebook | Input | Output |
|---|---|---|---|
| 1 | `01_data_cleaning.ipynb` | `data/raw/*.csv` | `data/processed/movies_clean.csv`, `data/processed/ratings_clean.csv` |
| 2 | `02_eda.ipynb` | `data/processed/movies_clean.csv`, `ratings_clean.csv` | (không sinh file, chỉ phân tích — kết luận ghi trong `docs/dataset.md`) |
| 3 | `03_feature_engineering.ipynb` | `data/processed/movies_clean.csv`, `ratings_clean.csv`, `data/raw/links_small.csv` | `data/processed/movies_features.csv`, các file `.pkl` trong `models_artifacts/` |
| 4 | `04_content_based.ipynb` | *(sắp thực hiện)* | |
| 5 | `05_collaborative_filtering.ipynb` | *(sắp thực hiện)* | |
| 6 | `06_hybrid.ipynb` | *(sắp thực hiện)* | |
| 7 | `07_evaluation.ipynb` | *(sắp thực hiện)* | |

## 6. Lưu ý quan trọng khi phát triển

- Luôn tạo thư mục đích trước khi lưu file: `os.makedirs('../data/processed', exist_ok=True)` — tránh lỗi `OSError: Cannot save file into a non-existent directory`.
- Các cột từng được điền chuỗi rỗng (`fillna('')`) sẽ bị đọc lại thành `NaN` khi mở lại CSV bằng `pd.read_csv`. Luôn gọi lại `fillna('')` cho các cột này (`director_clean`, `overview`...) sau khi đọc file đã lưu.
- Các cột kiểu `list` (`genres_clean`, `keywords_clean`, `cast_clean`...) khi lưu ra CSV sẽ thành chuỗi dạng `"['a', 'b']"`. Khi đọc lại, cần `ast.literal_eval` để chuyển về đúng kiểu `list`.
- `ratings.csv` (movieId - MovieLens) và `movies_clean.csv` (id - TMDb) là 2 hệ id khác nhau, cần map qua `links_small.csv` (`movieId ↔ tmdbId`).

## 7. Chạy ứng dụng Streamlit (khi đã hoàn thành Giai đoạn 7)

```bash
cd app
streamlit run main.py
```