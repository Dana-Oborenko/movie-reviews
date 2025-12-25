import { createRouter, createWebHistory } from 'vue-router'
import MoviesAdminView from '../views/MoviesAdminView.vue'
import MovieDetailView from '../views/MovieDetailView.vue'

const routes = [
  {
    path: '/',
    name: 'movies-admin',
    component: MoviesAdminView,
  },
  {
    path: '/movies/:id',
    name: 'movie-detail',
    component: MovieDetailView,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
