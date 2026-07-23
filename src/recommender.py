import os
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
ARTIFACT_DIR = os.path.join(PROJECT_ROOT, 'models_artifacts')


class MovieRecommender:
    def __init__(self):
        self.movies = pd.read_csv(os.path.join(DATA_DIR, 'movies_features.csv'))
        self.movies = self.movies.reset_index(drop=True)

        with open(os.path.join(ARTIFACT_DIR, 'tfidf_matrix.pkl'), 'rb') as f:
            self.tfidf_matrix = pickle.load(f)
        with open(os.path.join(ARTIFACT_DIR, 'content_based_candidate_indices.pkl'), 'rb') as f:
            self.candidate_indices = pickle.load(f)
        with open(os.path.join(ARTIFACT_DIR, 'user_item_matrix.pkl'), 'rb') as f:
            self.user_item_matrix = pickle.load(f)
        with open(os.path.join(ARTIFACT_DIR, 'user_knn_model.pkl'), 'rb') as f:
            self.user_knn = pickle.load(f)

        # Index tra cứu
        self.id_to_pos = pd.Series(self.movies.index, index=self.movies['id'])
        self.title_to_pos = pd.Series(self.movies.index, index=self.movies['title']).drop_duplicates(keep='first')
        self.candidate_tmdb_ids = self.movies.iloc[self.candidate_indices]['id'].values

        # Trung bình rating từng user trong ma trận CF (dùng cho mean-centering)
        self.user_means = self.user_item_matrix.replace(0, np.nan).mean(axis=1)
        self.global_mean = self.user_item_matrix.replace(0, np.nan).stack().mean()

    # ---------- CONTENT-BASED ----------

    def get_similar_movies(self, tmdb_id, top_n=5, exclude_ids=None):
        """Vì bạn thích ... : phim tương tự 1 phim cụ thể"""
        if tmdb_id not in self.id_to_pos.index:
            return pd.DataFrame()
        idx = self.id_to_pos[tmdb_id]

        sim_scores = cosine_similarity(self.tfidf_matrix[idx], self.tfidf_matrix[self.candidate_indices]).flatten()
        order = sim_scores.argsort()[::-1]

        exclude = set(exclude_ids or []) | {tmdb_id}
        results = []
        for pos in order:
            cand_id = self.candidate_tmdb_ids[pos]
            if cand_id in exclude:
                continue
            results.append((cand_id, sim_scores[pos]))
            if len(results) >= top_n:
                break

        return self._format_result(results, score_col='similarity_score')

    def get_similar_to_liked_list(self, liked_tmdb_ids, top_n=5, exclude_ids=None):
        """Dựa trên phim bạn đã thích: trung bình similarity với TOÀN BỘ danh sách đã thích"""
        liked_pos = self.id_to_pos.reindex(liked_tmdb_ids).dropna().astype(int).values
        if len(liked_pos) == 0:
            return pd.DataFrame()

        sim_matrix = cosine_similarity(self.tfidf_matrix[liked_pos], self.tfidf_matrix[self.candidate_indices])
        cb_scores = sim_matrix.mean(axis=0)

        exclude = set(exclude_ids or []) | set(liked_tmdb_ids)
        scores_df = pd.DataFrame({'id': self.candidate_tmdb_ids, 'score': cb_scores})
        scores_df = scores_df[~scores_df['id'].isin(exclude)]
        top = scores_df.sort_values('score', ascending=False).head(top_n)

        return self._format_result(list(zip(top['id'], top['score'])), score_col='similarity_score')

    # ---------- COLLABORATIVE FILTERING (mean-centered, v2) ----------

    def get_cf_recommendations(self, user_id, top_n=5, k_neighbors=10, exclude_ids=None):
        """Người giống bạn đang xem"""
        if user_id not in self.user_item_matrix.index:
            return pd.DataFrame()

        user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        distances, idx_knn = self.user_knn.kneighbors(user_vector, n_neighbors=k_neighbors + 1)
        sim_pos = idx_knn.flatten()[1:]
        sims = 1 - distances.flatten()[1:]

        neighbor_ids = self.user_item_matrix.index[sim_pos]
        neighbor_ratings = self.user_item_matrix.iloc[sim_pos]
        neighbor_means = self.user_means.reindex(neighbor_ids).fillna(self.global_mean).values

        # Mean-centering: độ lệch của neighbor so với trung bình của chính họ
        deviations = neighbor_ratings.sub(neighbor_means, axis=0)
        deviations = deviations.where(neighbor_ratings > 0, 0)  # chỉ tính ở ô neighbor thực sự đã rate

        weighted_dev = deviations.T.dot(sims) / (sims.sum() + 1e-9)
        target_mean = self.user_means.get(user_id, self.global_mean)
        predicted_scores = target_mean + weighted_dev
        predicted_scores = (target_mean + weighted_dev).clip(0.5, 5.0)

        already_rated = self.user_item_matrix.loc[user_id]
        exclude = set(exclude_ids or [])
        candidates = predicted_scores[(already_rated == 0)]
        candidates = candidates[~candidates.index.isin(exclude)]

        top = candidates.sort_values(ascending=False).head(top_n)
        return self._format_result(list(top.items()), score_col='cf_score')

    # ---------- HYBRID ----------

    def get_hybrid_recommendations(self, user_id, liked_tmdb_ids, top_n=5, k_neighbors=10, exclude_ids=None):
        """Phim dành riêng cho bạn — nhận liked_tmdb_ids từ SQLite (KHÔNG tự suy ra từ user_item_matrix)"""
        has_cf = user_id in self.user_item_matrix.index
        n_ratings = (self.user_item_matrix.loc[user_id] > 0).sum() if has_cf else 0

        # --- CB score ---
        liked_pos = self.id_to_pos.reindex(liked_tmdb_ids).dropna().astype(int).values if liked_tmdb_ids else np.array([])
        if len(liked_pos) > 0:
            sim_matrix = cosine_similarity(self.tfidf_matrix[liked_pos], self.tfidf_matrix[self.candidate_indices])
            cb_raw = sim_matrix.mean(axis=0)
        else:
            cb_raw = np.zeros(len(self.candidate_indices))

        # --- CF score (mean-centered) ---
        if has_cf:
            user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
            distances, idx_knn = self.user_knn.kneighbors(user_vector, n_neighbors=k_neighbors + 1)
            sim_pos = idx_knn.flatten()[1:]
            sims = 1 - distances.flatten()[1:]
            neighbor_ids = self.user_item_matrix.index[sim_pos]
            neighbor_ratings = self.user_item_matrix.iloc[sim_pos]
            neighbor_means = self.user_means.reindex(neighbor_ids).fillna(self.global_mean).values
            deviations = neighbor_ratings.sub(neighbor_means, axis=0)
            deviations = deviations.where(neighbor_ratings > 0, 0)
            weighted_dev = deviations.T.dot(sims) / (sims.sum() + 1e-9)
            target_mean = self.user_means.get(user_id, self.global_mean)
            cf_full = (target_mean + weighted_dev).reindex(self.candidate_tmdb_ids).fillna(0).values
            cf_full = (target_mean + weighted_dev).clip(0.5, 5.0).reindex(self.candidate_tmdb_ids).fillna(0).values
        else:
            cf_full = np.zeros(len(self.candidate_indices))

        def norm(a):
            return np.zeros_like(a) if a.max() - a.min() < 1e-9 else (a - a.min()) / (a.max() - a.min())

        cb_norm, cf_norm = norm(cb_raw), norm(cf_full)

        if has_cf:
            alpha = max(0.2, 1 - n_ratings / 50)
        else:
            alpha = 1.0
        beta = 1 - alpha

        hybrid_scores = alpha * cb_norm + beta * cf_norm

        already_rated_ids = set(self.user_item_matrix.columns[self.user_item_matrix.loc[user_id] > 0]) if has_cf else set()
        exclude = set(exclude_ids or []) | already_rated_ids | set(liked_tmdb_ids)

        # scores_df = pd.DataFrame({'id': self.candidate_tmdb_ids, 'score': hybrid_scores})
        # scores_df = scores_df[~scores_df['id'].isin(exclude)]
        # top = scores_df.sort_values('score', ascending=False).head(top_n)

        # return self._format_result(list(zip(top['id'], top['score'])), score_col='hybrid_score')

        scores_df = pd.DataFrame({
            'id': self.candidate_tmdb_ids,
            'hybrid_score': hybrid_scores,
            'cb_score': cb_norm,
            'cf_score': cf_norm,
        })
        scores_df = scores_df[~scores_df['id'].isin(exclude)]
        top = scores_df.sort_values('hybrid_score', ascending=False).head(top_n)

        result = self.movies[self.movies['id'].isin(top['id'])][
            ['id', 'title', 'weighted_rating', 'vote_average', 'poster_path', 'genres_display']].merge(top, on='id')
        result = result.sort_values('hybrid_score', ascending=False).reset_index(drop=True)
        result.attrs['alpha'] = alpha
        result.attrs['beta'] = beta
        return result

    # ---------- KHÁC ----------

    def get_top_movies(self, top_n=10, exclude_ids=None):
        """Danh sách phim — theo weighted_rating"""
        df = self.movies[~self.movies['id'].isin(set(exclude_ids or []))]
        top = df.sort_values('weighted_rating', ascending=False).head(top_n)
        return top[['id', 'title', 'weighted_rating', 'vote_average', 'poster_path']].reset_index(drop=True)

    def get_surprise_me(self, top_n=5, exclude_ids=None, pool_size=200):
        """Có thể bạn sẽ bất ngờ: chọn ngẫu nhiên có chọn lọc từ top phim theo weighted_rating"""
        df = self.movies[~self.movies['id'].isin(set(exclude_ids or []))]
        pool = df.sort_values('weighted_rating', ascending=False).head(pool_size)
        sample = pool.sample(n=min(top_n, len(pool)))
        return sample[['id', 'title', 'weighted_rating', 'vote_average', 'poster_path']].reset_index(drop=True)

    # ---------- HELPER ----------

    def _format_result(self, id_score_pairs, score_col):
        if not id_score_pairs:
            return pd.DataFrame()
        ids = [x[0] for x in id_score_pairs]
        scores = [x[1] for x in id_score_pairs]
        df = self.movies[self.movies['id'].isin(ids)][
            ['id', 'title', 'weighted_rating', 'vote_average', 'poster_path']].copy()
        score_map = dict(zip(ids, scores))
        df[score_col] = df['id'].map(score_map)
        df = df.sort_values(score_col, ascending=False).reset_index(drop=True)
        return df