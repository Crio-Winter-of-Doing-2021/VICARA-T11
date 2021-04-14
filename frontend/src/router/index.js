// Imports
import Vue from 'vue'
import Router from 'vue-router'
import { trailingSlash } from '@/util/helpers'
import {
  layout,
  route,
} from '@/util/routes'
import AuthPage from '@/views/auth.vue'
import store from '@/store/index.js'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  scrollBehavior: (to, from, savedPosition) => {
    if (to.hash) return { selector: to.hash }
    if (savedPosition) return savedPosition

    return { x: 0, y: 0 }
  },
  routes: [
    layout('Default', [
      route('Home'),

      // Components
      route('Starred Files', null, '/starred'),
      route('Shared', null, '/shared'),
      route('Trash', null, '/trash'),

      
    ]),
    { path: '/auth', component: AuthPage },
  ],
})

router.beforeEach((to, from, next) => {
 
  // if (localStorage.getItem('token') && to.path === '/auth') {
  //   next('/')
  //   return
  // }
  if (!isExpired(localStorage.getItem('token')) || to.path === '/auth') {
        next()
      } else {
        next('/auth')
      }
})

function parseJwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(Buffer.from(base64, "base64").toString("ascii").split("").map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
};

function isExpired(token) {
  if (token) {
    const jwtPayload = parseJwt(localStorage.token);
    if (jwtPayload.exp < Date.now()/1000) {
        // token expired
        localStorage.removeItem('token')
        return true
    } else {
      return false
    }

  }
  
};

export default router
