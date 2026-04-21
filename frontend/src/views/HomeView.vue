<template>
  <div class="page">
    <div class="searchBar">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search movies..."
        class="searchInput"
      />
    </div>

    <div v-if="loading" class="state">Loading…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <div v-else-if="movies.length === 0" class="state">
      No movies available.
    </div>

    <div v-else-if="filteredMovies.length === 0" class="state">
      No movies found.
    </div>

    <div v-else class="grid">
      <article
        v-for="movie in filteredMovies"
        :key="movie.id"
        class="card"
        @click="openMovie(movie.id)"
      >
        <div class="posterWrapper">
          <img
            v-if="movie.poster_url"
            :src="movie.poster_url"
            :alt="movie.title"
            class="poster"
          />
          <div v-else class="posterPlaceholder">No poster</div>
        </div>

        <div class="cardBody">
          <div class="titleRow">
            <h3>{{ movie.title }}</h3>
            <span v-if="movie.year" class="year">{{ movie.year }}</span>
          </div>

          <div class="meta">
            <span
              v-if="movie.external_rating !== null && movie.external_rating !== undefined"
              class="rating"
            >
              ⭐ {{ movie.external_rating }}
            </span>
            <span v-if="formatGenres(movie.genres)" class="genres">
              {{ formatGenres(movie.genres) }}
            </span>
          </div>

          <p v-if="movie.description" class="description">
            {{ truncate(movie.description) }}
          </p>
          <p v-else class="description muted">
            No description yet.
          </p>
          <div class="cardFooter">
            <button class="viewBtn" @click.stop="openMovie(movie.id)">
              View details
            </button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { api } from "../api";

const router = useRouter();

const movies = ref([]);
const loading = ref(false);
const error = ref("");
const searchQuery = ref("");

function openMovie(id) {
  router.push({ name: "movie-detail", params: { id } });
}

function truncate(text, max = 120) {
  if (!text) return "";
  return text.length > max ? text.slice(0, max) + "…" : text;
}

function formatGenres(genres) {
  if (!genres) return "";
  if (Array.isArray(genres)) return genres.join(", ");
  if (typeof genres === "string") {
    try {
      const parsed = JSON.parse(genres);
      if (Array.isArray(parsed)) return parsed.join(", ");
    } catch {
      return genres;
    }
  }
  return "";
}

const filteredMovies = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  if (!query) return movies.value;

  return movies.value.filter((movie) => {
    return (
      movie.title.toLowerCase().includes(query) ||
      (movie.description || "").toLowerCase().includes(query) ||
      formatGenres(movie.genres).toLowerCase().includes(query)
    );
  });
});

async function loadMovies() {
  loading.value = true;
  error.value = "";
  try {
    const res = await api.get("/movies");
    movies.value = Array.isArray(res.data)
      ? res.data
      : res.data?.items || [];
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      e.message ||
      "Failed to load movies";
  } finally {
    loading.value = false;
  }
}

onMounted(loadMovies);
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  margin-bottom: 20px;
}

.subtitle {
  opacity: 0.7;
}

.state {
  margin-top: 20px;
  opacity: 0.8;
}

.state.error {
  color: #c0392b;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.card {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.card {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
}

.posterWrapper {
  height: 220px;
  background: rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.posterPlaceholder {
  opacity: 0.6;
}

.cardBody {
  padding: 12px;
}

.titleRow {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
}

.year {
  font-size: 13px;
  opacity: 0.7;
}

.meta {
  margin-top: 6px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 13px;
}

.rating {
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 999px;
  padding: 2px 10px;
}

.genres {
  opacity: 0.75;
}

.description {
  margin-top: 10px;
  font-size: 13px;
}

.muted {
  opacity: 0.6;
}

.searchBar {
  margin-bottom: 16px;
}

.searchInput {
  width: 100%;
  max-width: 400px;
  padding: 10px;
  font-size: 14px;
}

.cardFooter {
  margin-top: 12px;
  display: flex;
  justify-content: flex-start;
}

.viewBtn {
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
}
</style>
