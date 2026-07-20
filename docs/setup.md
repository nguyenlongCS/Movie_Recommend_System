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
| 4 | `04_content_based.ipynb` | `data/processed/movies_features.csv`, `tfidf_matrix.pkl` | `content_based_candidate_indices.pkl`, `title_indices.pkl` |
| 5 | `05_collaborative_filtering.ipynb` | `user_item_matrix.pkl` | `user_knn_model.pkl` (⚠️ bản v1, chưa mean-centering — xem mục 6) |
| 6 | `06_hybrid.ipynb` | Artifact từ notebook 3-5 | `movies_id_to_pos.pkl` |
| 7 | `07_evaluation.ipynb` | Artifact từ notebook 3-6 | (không sinh file — kết quả ghi trong `docs/dataset.md` mục 10) |

## 6. Lưu ý quan trọng khi phát triển

- Luôn tạo thư mục đích trước khi lưu file: `os.makedirs('../data/processed', exist_ok=True)` — tránh lỗi `OSError: Cannot save file into a non-existent directory`.
- Các cột từng được điền chuỗi rỗng (`fillna('')`) sẽ bị đọc lại thành `NaN` khi mở lại CSV bằng `pd.read_csv`. Luôn gọi lại `fillna('')` cho các cột này (`director_clean`, `overview`...) sau khi đọc file đã lưu.
- Các cột kiểu `list` (`genres_clean`, `keywords_clean`, `cast_clean`...) khi lưu ra CSV sẽ thành chuỗi dạng `"['a', 'b']"`. Khi đọc lại, cần `ast.literal_eval` để chuyển về đúng kiểu `list`.
- `ratings.csv` (movieId - MovieLens) và `movies_clean.csv` (id - TMDb) là 2 hệ id khác nhau, cần map qua `links_small.csv` (`movieId ↔ tmdbId`).
- Không tính cosine similarity cho **toàn bộ** ma trận phim×phim (45,429×45,429 tốn ~16GB RAM) — chỉ tính on-demand giữa 1 phim/1 nhóm phim với tập candidate khi cần gợi ý.
- Content-Based cần **giới hạn candidate pool** theo ngưỡng tối thiểu (`vote_count ≥ 10`) — nếu không, phim có metadata quá ít (soup ngắn, gần như không ai vote) sẽ bị TF-IDF cosine similarity thổi phồng điểm giả tạo và lọt vào top gợi ý dù không liên quan.
- Tránh `groupby().apply()` khi hàm trả về DataFrame cùng cấu trúc mỗi nhóm (dễ lỗi `KeyError` với pandas 2.2+) — dùng cách tiếp cận vector hóa (`groupby().cumcount()`, `groupby().transform()`) thay thế.
- **Collaborative Filtering cần mean-centering**: dự đoán rating trực tiếp bằng trung bình có trọng số trên rating thô (không trừ độ lệch trung bình từng user) cho kết quả RMSE **tệ hơn cả baseline đơn giản** (đoán bằng trung bình của chính user). Công thức đúng: `dự đoán = trung bình(user) + Σ(similarity × (rating_neighbor − trung bình(neighbor))) / Σ(similarity)`.
- Khi so sánh Precision@K/Recall@K giữa các phương pháp, phải đảm bảo **candidate pool giống nhau** giữa các phương pháp — so sánh CB (toàn bộ catalog) với CF (chỉ tập phim có rating) sẽ cho kết quả sai lệch nghiêm trọng (đánh giá thấp CB một cách giả tạo).
- Đã kiểm định: **TF-IDF tốt hơn CountVectorizer** rõ rệt cho Content-Based (Precision@5: 0.0280 vs 0.0108) — dùng TF-IDF làm chính thức.
- **Module `.py` trong `src/` (khác notebook)**: notebook luôn chạy từ `notebooks/` nên `../` ổn định, nhưng file `.py` có thể chạy từ bất kỳ thư mục nào tùy người dùng `cd` tới đâu → đường dẫn tương đối `../` không đáng tin cậy. Luôn xác định đường dẫn bằng `os.path.dirname(os.path.abspath(__file__))` rồi suy ngược lên `PROJECT_ROOT`.
- **SQLite: sắp xếp theo "gần đây nhất" không nên dùng cột timestamp** nếu nhiều thao tác có thể diễn ra trong cùng 1 giây (`CURRENT_TIMESTAMP` của SQLite chỉ phân giải tới cấp giây) — dùng `ORDER BY id DESC` (autoincrement) đáng tin cậy hơn.

## 7. Chạy ứng dụng Streamlit (khi đã hoàn thành Giai đoạn 7)

```bash
cd app
streamlit run main.py
```
