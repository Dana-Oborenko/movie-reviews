import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/HomeView.vue";
import MovieDetailView from "../views/MovieDetailView.vue";
import MoviesAdminView from "../views/MoviesAdminView.vue";
import LoginView from "../views/LoginView.vue";

const routes = [
  // Public part (Guest allowed)
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: { public: true },
  },
  {
    path: "/movies/:id",
    name: "movie-detail",
    component: MovieDetailView,
    props: true,
    meta: { public: true },
  },

  // Auth
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: { public: true },
  },

  // Admin part (protected)
  {
    path: "/admin",
    name: "movies-admin",
    component: MoviesAdminView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  // allow public routes without token
  if (to.meta?.public) return true;

  const token = localStorage.getItem("access_token");
  if (!token) return "/login";

  return true;
});

export default router;
