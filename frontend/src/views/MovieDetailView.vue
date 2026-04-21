<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const router = useRouter()

const movie = ref(null)
const reviews = ref([])
const loading = ref(true)
const error = ref('')
const isAuthenticated = !!localStorage.getItem('access_token')
const isAdmin = localStorage.getItem('user_role') === 'admin'

const newReviewText = ref('')
const reviewFilter = ref('all')
const movieId = Number(route.params.id)

let pollTimer = null
const POLL_INTERVAL_MS = 2000

function hasPendingReviews(list) {
  return Array.isArray(list) && list.some((r) => r.ml_status === 'pending')
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function startPollingIfNeeded() {
  if (pollTimer) return
  if (!hasPendingReviews(reviews.value)) return

  pollTimer = setInterval(async () => {
    try {
      await loadReviews()
      if (!hasPendingReviews(reviews.value)) {
        stopPolling()
      }
    } catch (e) {
      console.error(e)
      stopPolling()
    }
  }, POLL_INTERVAL_MS)
}

function formatGenres(genres) {
  if (!genres) return ''
  if (Array.isArray(genres)) return genres.join(', ')
  if (typeof genres === 'string') {
    try {
      const parsed = JSON.parse(genres)
      if (Array.isArray(parsed)) return parsed.join(', ')
    } catch {
      return genres
    }
  }
  return ''
}

const filteredReviews = computed(() => {
  if (reviewFilter.value === 'all') return reviews.value

  if (reviewFilter.value === 'positive') {
    return reviews.value.filter((r) => r.sentiment === 'POSITIVE')
  }

  if (reviewFilter.value === 'negative') {
    return reviews.value.filter((r) => r.sentiment === 'NEGATIVE')
  }

  if (reviewFilter.value === 'pending') {
    return reviews.value.filter((r) => r.ml_status === 'pending')
  }

  if (reviewFilter.value === 'failed') {
    return reviews.value.filter((r) => r.ml_status === 'failed')
  }

  return reviews.value
})

async function loadMovie() {
  try {
    const { data } = await api.get(`/movies/${movieId}`)
    movie.value = data
  } catch (e) {
    error.value = 'Movie not found'
  }
}

async function loadReviews() {
  try {
    const { data } = await api.get(`/reviews?movie_id=${movieId}`)
    reviews.value = data
  } catch {
    error.value = 'Failed to load reviews'
  }
}

async function addReview() {
  if (!newReviewText.value.trim()) return
  await api.post('/reviews', {
    movie_id: movieId,
    text: newReviewText.value,
  })
  newReviewText.value = ''
  await loadReviews()
  startPollingIfNeeded()
}

async function deleteReview(id) {
  if (!confirm('Delete?')) return
  await api.delete(`/reviews/${id}`)
  await loadReviews()
}

onMounted(async () => {
  await loadMovie()
  await loadReviews()
  startPollingIfNeeded()
  loading.value = false
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <div class="page">
    <button class="backBtn" @click="router.push('/')">← Back</button>

    <div v-if="loading" class="state">Loading...</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <div v-else class="content">
      <section class="hero">
        <div class="posterBlock">
          <img
            v-if="movie.poster_url"
            :src="movie.poster_url"
            :alt="movie.title"
            class="poster"
          />
          <div v-else class="posterPlaceholder">No poster</div>
        </div>

        <div class="infoBlock">
          <h1 class="title">#{{ movie.id }} — {{ movie.title }}</h1>

          <div class="meta">
            <span v-if="movie.year" class="chip">{{ movie.year }}</span>
            <span v-if="movie.external_rating !== null && movie.external_rating !== undefined" class="chip">
              ⭐ {{ movie.external_rating }}
            </span>
            <span v-if="formatGenres(movie.genres)" class="chip">
              {{ formatGenres(movie.genres) }}
            </span>
          </div>

          <p v-if="movie.description" class="description">{{ movie.description }}</p>
          <p v-else class="description muted">No description yet.</p>
        </div>
      </section>

      <section class="reviewFormCard">
        <h3>Add Review</h3>

        <div v-if="!isAuthenticated">
          <em>Login to add a review</em>
        </div>

        <div v-else class="reviewForm">
          <input v-model="newReviewText" placeholder="Your review" class="reviewInput" />
          <button @click="addReview" class="primaryBtn">Create</button>
        </div>
      </section>

      <section class="reviewsSection">
        <h3>Reviews ({{ filteredReviews.length }})</h3>

        <div class="reviewFilterBar">
          <label for="review-filter">Filter:</label>
          <select id="review-filter" v-model="reviewFilter" class="reviewFilterSelect">
            <option value="all">All reviews</option>
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div v-if="filteredReviews.length === 0" class="muted">No reviews for this filter.</div>

        <ul v-else class="reviewsList">
          <li v-for="r in filteredReviews" :key="r.id" class="reviewItem">
            <div class="reviewHeader">
              <strong>#{{ r.id }}</strong>

              <span v-if="r.ml_status === 'pending'" class="status pending">analyzing…</span>

              <span v-else-if="r.ml_status === 'failed'" class="status failed">
                failed
                <span v-if="r.ml_error"> ({{ r.ml_error }})</span>
              </span>

              <span v-else-if="r.sentiment" class="status done">
                {{ r.sentiment }} <span v-if="r.score">({{ r.score }})</span>
              </span>

              <span v-else class="status">
                {{ r.ml_status }}
              </span>
            </div>

            <div class="reviewText">{{ r.text }}</div>

            <button v-if="isAdmin" @click="deleteReview(r.id)" class="deleteBtn">
              Delete
            </button>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

.backBtn {
  margin-bottom: 16px;
  padding: 8px 12px;
  cursor: pointer;
}

.state {
  margin-top: 20px;
}

.state.error {
  color: #c0392b;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
}

.posterBlock {
  width: 100%;
  min-height: 460px;
  border-radius: 16px;
  overflow: hidden;
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

.infoBlock {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.title {
  margin: 0;
}

.meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 14px;
}

.description {
  line-height: 1.5;
  max-width: 720px;
}

.muted {
  opacity: 0.65;
}

.reviewFormCard,
.reviewsSection {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 16px;
  padding: 16px;
}

.reviewForm {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.reviewInput {
  flex: 1;
  min-width: 260px;
  padding: 10px;
}

.primaryBtn {
  padding: 10px 14px;
  cursor: pointer;
}

.reviewsList {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reviewItem {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 12px;
}

.reviewHeader {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.reviewText {
  margin-bottom: 10px;
  white-space: pre-wrap;
}

.status {
  font-size: 14px;
  opacity: 0.85;
}

.status.pending {
  opacity: 0.75;
}

.status.failed {
  color: #c0392b;
}

.status.done {
  font-weight: 600;
}

.deleteBtn {
  padding: 6px 10px;
  cursor: pointer;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .posterBlock {
    min-height: 360px;
  }
}

.reviewFilterBar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.reviewFilterSelect {
  padding: 8px 10px;
}
</style>