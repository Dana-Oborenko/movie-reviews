<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const router = useRouter()

const movie = ref(null)
const reviews = ref([])
const loading = ref(true)
const error = ref('')

const newReviewText = ref('')
const movieId = Number(route.params.id)

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
}

async function deleteReview(id) {
  if (!confirm('Delete?')) return
  await api.delete(`/reviews/${id}`)
  await loadReviews()
}

onMounted(async () => {
  await loadMovie()
  await loadReviews()
  loading.value = false
})
</script>

<template>
  <button @click="router.push('/')">← Back</button>

  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>

  <div v-else>
    <h2>#{{ movie.id }} — {{ movie.title }}</h2>
    <p>{{ movie.description }}</p>

    <section>
      <h3>Add Review</h3>
      <input v-model="newReviewText" placeholder="Your review" />
      <button @click="addReview">Create</button>
    </section>

    <section>
      <h3>Reviews</h3>
      <ul>
        <li v-for="r in reviews" :key="r.id">
          <strong>#{{ r.id }}</strong> — {{ r.sentiment }} ({{ r.score }})
          <br />
          {{ r.text }}
          <button @click="deleteReview(r.id)">Delete</button>
        </li>
      </ul>
    </section>
  </div>
</template>
