import time
from recommender import MovieRecommender

print("Đang khởi tạo MovieRecommender (load dữ liệu + artifact)...")
start = time.time()
rec = MovieRecommender()
print(f"Khởi tạo xong trong {time.time() - start:.2f} giây")
print(f"Số phim: {len(rec.movies)}, Candidate pool: {len(rec.candidate_indices)}")
print()

# --- Test 1: Content-Based — phim tương tự 1 phim cụ thể ---
godfather_id = rec.movies[rec.movies['title'] == 'The Godfather']['id'].iloc[0]
print(f"--- Vì bạn thích: The Godfather (id={godfather_id}) ---")
res1 = rec.get_similar_movies(godfather_id, top_n=5)
print(res1[['title', 'similarity_score']].to_string(index=False))
print()

# --- Test 2: CB theo danh sách đã thích ---
liked_test = [238, 424]  # Godfather, Schindler's List
print(f"--- Dựa trên phim đã thích {liked_test} ---")
res2 = rec.get_similar_to_liked_list(liked_test, top_n=5)
print(res2[['title', 'similarity_score']].to_string(index=False) if not res2.empty else "Rỗng")
print()

# --- Test 3: Collaborative Filtering (mean-centered) ---
print("--- Người giống bạn đang xem (user_id=300) ---")
res3 = rec.get_cf_recommendations(300, top_n=5)
print(res3[['title', 'cf_score']].to_string(index=False) if not res3.empty else "Rỗng")
print()

# --- Test 4: Hybrid ---
print("--- Phim dành riêng cho bạn (user_id=1, liked=[238,424]) ---")
res4 = rec.get_hybrid_recommendations(1, liked_tmdb_ids=[238, 424], top_n=5)
print(res4[['title', 'hybrid_score']].to_string(index=False) if not res4.empty else "Rỗng")
print()

# --- Test 5: Hybrid với user cold-start (không có trong CF, chỉ có liked) ---
print("--- Phim dành riêng cho bạn (user cold-start, chỉ có liked=[238]) ---")
res5 = rec.get_hybrid_recommendations(999999, liked_tmdb_ids=[238], top_n=5)
print(res5[['title', 'hybrid_score']].to_string(index=False) if not res5.empty else "Rỗng")
print()

# --- Test 6: Danh sách phim (top weighted rating) ---
print("--- Danh sách phim (top 10) ---")
res6 = rec.get_top_movies(top_n=10)
print(res6[['title', 'weighted_rating']].to_string(index=False))
print()

# --- Test 7: Có thể bạn sẽ bất ngờ ---
print("--- Có thể bạn sẽ bất ngờ ---")
res7 = rec.get_surprise_me(top_n=5)
print(res7[['title', 'weighted_rating']].to_string(index=False))
print()

# --- Test 8: exclude_ids có hoạt động không ---
print("--- Test exclude_ids: loại The Godfather Part II khỏi gợi ý 'Vì bạn thích Godfather' ---")
part2_id = rec.movies[rec.movies['title'].str.contains('Godfather: Part II', na=False)]['id']
exclude_test = list(part2_id) if len(part2_id) > 0 else []
res8 = rec.get_similar_movies(godfather_id, top_n=5, exclude_ids=exclude_test)
print(f"Excluded id: {exclude_test}")
print(res8[['id', 'title']].to_string(index=False))