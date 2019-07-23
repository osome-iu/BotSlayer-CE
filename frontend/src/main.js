import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import axios from "axios";
import VueAxios from "vue-axios";

import VueTimeago from 'vue-timeago'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.min.css'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faGoogle, faTwitter } from '@fortawesome/free-brands-svg-icons'
import { faRetweet, faQuestionCircle } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'


Vue.use(VueAxios, axios);

// Used for the "Last Seen" column
Vue.use(VueTimeago, {
  name: 'Timeago',
  locale: 'en'
});

// Used in the b-button, b-table, etc.
// Very reactive bootstrap elements this way
import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue);

// FontAwesome inclusions
library.add(faGoogle, faTwitter, faRetweet, faQuestionCircle)
Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
