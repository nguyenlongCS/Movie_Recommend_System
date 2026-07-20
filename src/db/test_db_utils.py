import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_utils import (mark_watched, like_movie, dislike_movie,
                       get_watched_ids, get_liked_ids, get_disliked_ids, get_latest_liked_id)

USER_ID = 1

# Test 1: Play
mark_watched(USER_ID, 550)   # Fight Club
mark_watched(USER_ID, 680)   # Pulp Fiction
print("Watched:", get_watched_ids(USER_ID))

# Test 2: Like
like_movie(USER_ID, 238)     # The Godfather
like_movie(USER_ID, 424)     # Schindler's List
print("Liked:", get_liked_ids(USER_ID))

# Test 3: Dislike
dislike_movie(USER_ID, 155)  # The Dark Knight (test thôi, giả lập)
print("Disliked:", get_disliked_ids(USER_ID))

# Test 4: Ràng buộc loại trừ — Like 1 phim đang Dislike, phải tự gỡ khỏi Dislike
print("\n--- Test ràng buộc loại trừ ---")
like_movie(USER_ID, 155)     # Like lại phim vừa Dislike ở trên
print("Liked sau khi like lại phim đã dislike:", get_liked_ids(USER_ID))
print("Disliked sau đó (phải KHÔNG còn 155):", get_disliked_ids(USER_ID))

# Test 5: Bấm Like lại phim đã Like (kiểm tra không bị trùng lặp)
like_movie(USER_ID, 238)
print("\nLiked sau khi like lại phim đã like (không được nhân đôi):", get_liked_ids(USER_ID))

# Test 6: Latest liked (seed cho 'Vì bạn thích ...')
print("\nPhim thích gần nhất:", get_latest_liked_id(USER_ID))