<script setup>
// Admin page: list movies & reviews, add/delete movie/review, filter + stats chart
import { onMounted, onBeforeUnmount, ref, computed, watch } from 'vue'
import { api } from '../api'
import SentimentChart from '../components/SentimentChart.vue'

// Data state
const movies = ref([])
const reviews = ref([])
// Stats state
const stats = ref({})

// Polling state
let pollTimer = null
const POLL_INTERVAL_MS = 2000


// Form state
const newMovieTitle = ref('')
const newMovieDesc = ref('')
const newReviewMovieId = ref(null)
const newReviewText = ref('')

// UI state
const selectedMovieForFilter = ref(null) // which movie to filter reviews by

// Derived state: reviews filtered by selectedMovieForFilter
const filteredReviews = computed(() => {
  if (!selectedMovieForFilter.value) {
    return reviews.value
  }
  const id = Number(selectedMovieForFilter.value)
  return reviews.value.filter((r) => r.movie_id === id)
})

// Load data helpers
async function loadMovies() {
  const { data } = await api.get('/movies')
  movies.value = data
}

async function loadReviews(movieId) {
  const url = movieId ? `/reviews?movie_id=${movieId}` : '/reviews'
  const { data } = await api.get(url)
  reviews.value = data
}

async function loadStats() {
  const { data } = await api.get('/reviews/stats')
  stats.value = data || {}
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function hasPendingReviews(list) {
  return Array.isArray(list) && list.some((r) => r.ml_status === 'pending')
}

async function refreshCurrentReviews() {
  const movieId = selectedMovieForFilter.value
    ? Number(selectedMovieForFilter.value)
    : undefined

  await loadReviews(movieId)
  await loadStats()
  startPollingIfNeeded()

  // Stop polling if no pending reviews left
  if (!hasPendingReviews(reviews.value)) {
    stopPolling()
  }
}

function startPollingIfNeeded() {
  // Do not start another timer if already running
  if (pollTimer) return

  // Start only if there are pending reviews
  if (!hasPendingReviews(reviews.value)) return

  pollTimer = setInterval(async () => {
    try {
      await refreshCurrentReviews()
    } catch (e) {
      console.error(e)
      stopPolling()
    }
  }, POLL_INTERVAL_MS)
}

// Actions
async function addMovie() {
  if (!newMovieTitle.value.trim()) return
  try {
    await api.post('/movies', {
      title: newMovieTitle.value.trim(),
      description: newMovieDesc.value.trim() || null,
    })
    newMovieTitle.value = ''
    newMovieDesc.value = ''
    await loadMovies()
  } catch (e) {
    console.error(e)
    alert('Failed to create movie')
  }
}

async function deleteMovie(id) {
  if (!confirm('Delete this movie and all its reviews?')) return
  try {
    await api.delete(`/movies/${id}`)
    await loadMovies()
    await loadReviews(
      selectedMovieForFilter.value ? Number(selectedMovieForFilter.value) : undefined,
    )
    await loadStats()
  } catch (e) {
    console.error(e)
    alert('Failed to delete movie')
  }
}

async function addReview() {
  if (!newReviewMovieId.value || !newReviewText.value.trim()) return
  try {
    const movieId = Number(newReviewMovieId.value)
    await api.post('/reviews', {
      movie_id: movieId,
      text: newReviewText.value.trim(),
    })
    newReviewText.value = ''
    await loadReviews(
      selectedMovieForFilter.value ? Number(selectedMovieForFilter.value) : movieId,
    )
    await loadStats()
    startPollingIfNeeded()
  } catch (e) {
    console.error(e)
    alert('Failed to create review')
  }
}

async function deleteReview(id) {
  if (!confirm('Delete this review?')) return
  try {
    await api.delete(`/reviews/${id}`)
    const movieId = selectedMovieForFilter.value
      ? Number(selectedMovieForFilter.value)
      : undefined
    await loadReviews(movieId)
    await loadStats()
    startPollingIfNeeded()
  } catch (e) {
    console.error(e)
    alert('Failed to delete review')
  }
}

async function retryReview(id) {
  try {
    await api.post(`/reviews/${id}/retry`)
    const movieId = selectedMovieForFilter.value
      ? Number(selectedMovieForFilter.value)
      : undefined
    await loadReviews(movieId)
    await loadStats()
  } catch (e) {
    console.error(e)
    alert('Failed to retry review analysis')
  }
}


// Init
onMounted(async () => {
  await loadMovies()
  await loadReviews()
  await loadStats()
  startPollingIfNeeded()
})

watch(selectedMovieForFilter, async () => {
  stopPolling()
  const movieId = selectedMovieForFilter.value
    ? Number(selectedMovieForFilter.value)
    : undefined
  await loadReviews(movieId)
  await loadStats()
  startPollingIfNeeded()
})


</script>

<template>
  <!-- ВАЖНО: тут уже БЕЗ <main> и BEЗ большого h1 -->
  <!-- они будут в App.vue, чтобы не дублировать -->

  <!-- Add Movie -->
  <section style="margin:24px 0; padding:16px; border:1px solid #444; border-radius:12px">
    <h2 style="margin-top:0">Add Movie</h2>
    <div style="display:flex; gap:8px; flex-wrap:wrap">
      <input
        v-model="newMovieTitle"
        type="text"
        placeholder="Title"
        style="flex:1; padding:8px"
      />
      <input
        v-model="newMovieDesc"
        type="text"
        placeholder="Description (optional)"
        style="flex:2; padding:8px"
      />
      <button @click="addMovie" style="padding:8px 12px; cursor:pointer">
        Create
      </button>
    </div>
  </section>

  <!-- Movies list -->
  <section style="margin:24px 0;">
    <h2 style="margin-top:0">Movies ({{ movies.length }})</h2>
    <ul>
      <li v-for="m in movies" :key="m.id" style="margin-bottom:6px">
        <strong>#{{ m.id }} · {{ m.title }}</strong>
        <span v-if="m.description"> — {{ m.description }}</span>

        <!-- show reviews for this movie -->
        <button
          style="margin-left:8px; padding:2px 8px; cursor:pointer"
          @click="loadReviews(m.id); selectedMovieForFilter = m.id"
          title="Show reviews for this movie"
        >
          Show reviews
        </button>

        <!-- delete movie -->
        <button
          style="margin-left:4px; padding:2px 8px; cursor:pointer; background:#a33; color:white"
          @click="deleteMovie(m.id)"
          title="Delete movie"
        >
          Delete
        </button>
      </li>
    </ul>
  </section>

  <!-- Add Review -->
  <section style="margin:24px 0; padding:16px; border:1px solid #444; border-radius:12px">
    <h2 style="margin-top:0">Add Review</h2>
    <div style="display:flex; gap:8px; flex-wrap:wrap">
      <select v-model="newReviewMovieId" style="padding:8px">
        <option :value="null" disabled>Select movie</option>
        <option v-for="m in movies" :key="m.id" :value="m.id">
          #{{ m.id }} · {{ m.title }}
        </option>
      </select>
      <input
        v-model="newReviewText"
        type="text"
        placeholder="Your review text"
        style="flex:1; padding:8px"
      />
      <button @click="addReview" style="padding:8px 12px; cursor:pointer">
        Create
      </button>
    </div>
  </section>

  <!-- Reviews list + filter + stats -->
  <section style="margin:24px 0;">
    <h2 style="margin-top:0">Reviews ({{ filteredReviews.length }})</h2>

    <div style="margin-bottom:12px; display:flex; gap:8px; align-items:center">
      <span>Filter by movie:</span>
      <select v-model="selectedMovieForFilter" style="padding:6px; min-width:200px">
        <option :value="null">All movies</option>
        <option v-for="m in movies" :key="m.id" :value="m.id">
          #{{ m.id }} · {{ m.title }}
        </option>
      </select>
      <button
        style="padding:4px 10px; cursor:pointer"
        @click="loadReviews(selectedMovieForFilter ? Number(selectedMovieForFilter) : undefined)"
      >
        Reload reviews
      </button>
    </div>

    <!-- Sentiment stats + chart -->
    <div style="margin-bottom:12px;">
      <h3 style="margin:0 0 4px 0;">Sentiment stats</h3>
      <div v-if="Object.keys(stats).length === 0">
        No stats yet (no reviews).
      </div>
      <div v-else style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap">
        <ul style="margin:0; padding-left:18px; min-width:140px;">
          <li v-for="(count, label) in stats" :key="label">
            {{ label }}: {{ count }}
          </li>
        </ul>
        <SentimentChart :stats="stats" />
      </div>
    </div>

    <ul>
      <li v-for="r in filteredReviews" :key="r.id" style="margin-bottom:8px">
        <div>
          <strong>#{{ r.id }}</strong>
          · movie_id={{ r.movie_id }}

          <!-- ML status -->
          <span v-if="r.ml_status === 'pending'">
            · analyzing...
          </span>

          <span v-else-if="r.ml_status === 'failed'">
            · failed
            <span v-if="r.ml_error"> ({{ r.ml_error }})</span>
            <button
              style="margin-left:8px; padding:2px 8px; cursor:pointer"
              @click="retryReview(r.id)"
            >
              Retry
            </button>
          </span>

          <span v-else>
            <span v-if="r.sentiment"> · {{ r.sentiment }}</span>
            <span v-if="r.score"> ({{ r.score }})</span>
          </span>

          <button
            style="margin-left:8px; padding:2px 8px; cursor:pointer; background:#a33; color:white"
            @click="deleteReview(r.id)"
          >
            Delete
          </button>
        </div>

        <div>{{ r.text }}</div>
      </li>

    </ul>
  </section>
</template>
