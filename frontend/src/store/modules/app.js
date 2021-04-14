// Pathify
import { make } from 'vuex-pathify'

// Data
const state = {
  drawer: null,
  drawerImage: true,
  mini: false,
  items: [
    {
      title: 'Home',
      icon: 'mdi-view-dashboard',
      to: '/',
    },
    {
      title: 'Trash',
      icon: 'mdi-trash-can',
      to: '/trash',
    },
    {
      title: 'Shared By Me',
      icon: 'mdi-chart-bubble',
      to: '/shared',
    },
    {
      title: 'Starred Files',
      icon: 'mdi-file-star',
      to: '/starred',
    },
  ],
}

const mutations = make.mutations(state)

const actions = {
  ...make.actions(state),
  init: async ({ dispatch }) => {
    //
  },
}

const getters = {}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
